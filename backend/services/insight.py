import json  # turns the model's reply string into a real Python dict
import os  # reads OPENROUTER_KEY from the environment
import re  # pulls the JSON object out of a reply wrapped in extra text
from datetime import date  # today's calendar day, for the cache lookup

import requests
from sqlalchemy import select
from sqlalchemy.orm import Session

from database import engine
from tables import Insight

# free models get rate-limited upstream independently, so we try several in
# order rather than pinning one
MODELS = [
    "minimax/minimax-m3:free",
    "google/gemma-4-31b-it:free",
    "z-ai/glm-5.2:free",
]

OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"

# shown if every model fails or every reply is unparseable
FALLBACK_INSIGHT = {
    "insight": (
        "Markets are quiet on our side today — the daily insight could not be "
        "generated. Your prices and news below are still live."
    ),
    "topic": "general",
}


SYSTEM_PROMPT = """You are a crypto market commentator writing one short daily insight for a personal dashboard.

Rules:
- 2 to 3 sentences, under 60 words.
- Write for the reader's stated investor type: match their time horizon and what they would actually care about.
- Mention at least one of their coins by name.
- Be concrete and opinionated. No hedging, no "always do your own research", no disclaimers.
- Never give financial advice or price predictions. Comment on themes, behaviour and what to watch.

Reply with JSON only, no markdown fences, in exactly this shape:
{"insight": "<your text>", "topic": "<the single ticker the insight is most about, uppercase, or general>"}

The topic must be exactly one word: a single ticker from the reader's coins, or "general" if the insight is not about one specific coin. Never list two tickers, never add punctuation or extra words."""


# fills the reader's own answers into the message the model actually receives
def build_user_prompt(coins, investor_type):
    coin_list = ", ".join(coins)
    return (
        f"Investor type: {investor_type}\n"
        f"Coins they follow: {coin_list}\n"
        f"Write today's insight."
    )


# digs {"insight": ..., "topic": ...} out of whatever the model actually sent
def parse_reply(text, coins):
    # models often wrap JSON in ```json fences or a sentence — this grabs the
    # outermost {...} and ignores anything around it
    match = re.search(r"\{.*\}", text, re.DOTALL)
    if not match:
        return None

    try:
        data = json.loads(match.group())
    except json.JSONDecodeError:
        return None

    insight = data.get("insight")
    if not isinstance(insight, str) or not insight.strip():
        return None

    # the prompt asks for one of the user's tickers, but the model can ignore
    # that — anything unexpected becomes "general" rather than a junk topic
    topic = str(data.get("topic", "")).strip().upper()
    if topic not in coins:
        topic = "general"

    return {"insight": insight.strip(), "topic": topic}


# asks each free model in turn, returning the first reply that parses
def generate_insight(coins, investor_type):
    headers = {
        "Authorization": f"Bearer {os.environ['OPENROUTER_KEY']}",
        "Content-Type": "application/json",
    }
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": build_user_prompt(coins, investor_type)},
    ]

    for model in MODELS:
        try:
            response = requests.post(
                OPENROUTER_URL,
                headers=headers,
                json={"model": model, "messages": messages, "max_tokens": 300},
                timeout=45,
            )
            if response.status_code != 200:
                # usually a 429: this model is busy, try the next one
                continue
            reply = response.json()["choices"][0]["message"]["content"]
        except Exception:
            # network error or an unexpected response shape
            continue

        parsed = parse_reply(reply, coins)
        if parsed:
            return parsed

    return FALLBACK_INSIGHT


# today's insight for this user: reuse the saved one, or generate and save it
def get_daily_insight(user_id, coins, investor_type):
    today = date.today()

    with Session(engine) as session:
        saved = session.scalars(
            select(Insight).where(
                Insight.user_id == user_id,
                Insight.date == today,
            )
        ).first()

        if saved:
            return {"id": saved.id, "insight": saved.insight, "topic": saved.topic}

        result = generate_insight(coins, investor_type)

        # the fallback is saved like any other result, so a refresh loop can't
        # keep re-calling the models and burning the daily quota — see
        # questions.md for the freeze-vs-retry trade-off this accepts
        row = Insight(
            user_id=user_id,
            date=today,
            insight=result["insight"],
            topic=result["topic"],
        )
        session.add(row)
        session.commit()
        # Postgres generates the id during commit, so it's only readable
        # while the session is still open
        return {"id": row.id, "insight": row.insight, "topic": row.topic}

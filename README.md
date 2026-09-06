# AI Crypto Advisor

A personalized crypto dashboard. You sign up, answer three short questions
once, and the app builds a dashboard from your answers: live coin prices,
news ordered around the coins you follow, an AI-written insight of the day,
and a meme. Every item can be voted on, and the votes are stored for future
recommendation work.

**Live app:** _(added after deployment)_
**Demo login:** _(added after deployment)_

---

## Screenshots

The dashboard — sections ordered by the user's own answers, every item
votable:

![The dashboard](docs/screenshots/dashboard.png)

The quiz, revisited as an editable preferences page. Coin choices are capped
at five, and the content types set the section order:

![The preferences quiz](docs/screenshots/onboarding.png)

---

## What the quiz actually changes

| Your answer | What it affects |
|---|---|
| Coins (1-5) | Which coins appear in Prices; which news moves to the top |
| Investor type | The prompt the AI insight is written from |
| Content types | The order the four sections appear in |

A HODLer and a Day Trader who follow the same coins get different insights.
Someone who picks "meme" and "prices" sees those two sections first.

---

## Architecture

```
   Browser
      |  JWT in localStorage, sent as a Bearer header on every call
      v
   Vercel ---- React 19, plain JavaScript, Vite, Tailwind, React Router
      |
      |  direct cross-origin calls; the Render domain is allow-listed by CORS
      v
   Render ---- FastAPI, Uvicorn, SQLAlchemy ------> Render PostgreSQL
      |                                             users, votes, insights
      |
      +--> CoinGecko      prices, cached 60s per coin, shared across users
      +--> RSS feeds      CoinDesk, Cointelegraph, Decrypt; static fallback
      +--> OpenRouter     the daily insight, one per user per day, cached in the DB
      |
      +--- memegen.link   the meme URL comes from the backend, but the image
                          itself is loaded straight by the browser
```

Each of the four dashboard sections calls its own endpoint, so one slow or
failing source degrades a single card instead of the page.

---

## Stack

**Frontend** — React with plain JavaScript, built by Vite, styled with
Tailwind, routed by React Router. Hosted on Vercel.

**Backend** — FastAPI (Python), served by Uvicorn, talking to Postgres
through SQLAlchemy. Hosted on Render.

**Data** — CoinGecko for prices, CoinDesk/Cointelegraph/Decrypt RSS for news,
OpenRouter for the AI insight, and a hand-written meme file rendered by
memegen.link.

---

## Running it locally

Two terminals. Backend first:

```bash
cd backend
python -m venv venv
venv\Scripts\activate          # macOS/Linux: source venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload      # http://127.0.0.1:8000
```

It needs a `backend/.env` file, which is not committed:

```
DATABASE_URL=postgresql://user:password@host/dbname
JWT_SECRET=any long random string
OPENROUTER_KEY=sk-or-v1-...
```

Then the frontend:

```bash
cd frontend
npm install
npm run dev                    # http://localhost:5173
```

`http://127.0.0.1:8000/docs` gives an interactive page for every endpoint.

---

## Layout

```
backend/
  main.py        the eleven endpoints
  auth.py        password hashing and JWT tokens
  schemas.py     the shape each request body must have
  tables.py      the three tables, as SQLAlchemy classes
  database.py    the database connection
  services/      one file per outside data source

frontend/src/
  pages/         Login, Signup, Onboarding, Dashboard
  sections/      the four dashboard cards
  components/    VoteButtons, CoinIcon, ProtectedRoute, SectionError
  lib/           the fetch wrapper, and the preference rules
```

---

## Things worth knowing

**Nothing goes blank.** Each section fetches independently, so a slow or
broken source affects only its own card. News falls back to a hand-picked
list if all three feeds fail; the AI insight falls back to a fixed message if
every model is rate-limited.

**The AI insight is generated once per user per day** and cached in the
database, because OpenRouter's free tier allows 50 requests a day.

**Votes are per item, not per section.** A thumbs-down on a Dogecoin meme
records `topic: "DOGE"`, not `"memes"` — so the data says what someone is
actually interested in. Re-voting the same item the same day updates that row;
voting on it a different day is a new row, so changes of opinion over time
are preserved.

**Passwords are bcrypt-hashed.** The database never sees a real one.

---

## Not built

Named on purpose, so nothing reads as an oversight:

- **No tests.** The build was verified by hand at every step, including
  deliberately breaking each external source to confirm the fallbacks fire.
- **No refresh tokens.** One JWT with a 24-hour expiry; an expired token
  redirects to the login page.
- **Votes are stored but unused.** The assignment asks for the data to be
  collected, not consumed. `docs/ARCHITECTURE.md` suggests how it could be.
- **Changing your preferences doesn't regenerate today's insight.** It's the
  insight of the *day*; the new preferences apply tomorrow.

---

## Documents

- [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) — how it's built and why
- [`docs/AI_COLLABORATION.md`](docs/AI_COLLABORATION.md) — how AI tools were
  used while building it

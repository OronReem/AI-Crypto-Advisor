import re  # searches text for patterns, used here for whole-word coin matching
from email.utils import parsedate_to_datetime  # reads RSS's date format
import requests  # makes HTTP requests to other servers, like the browser's fetch()
import xml.etree.ElementTree as ET  # turns RSS's XML text into a searchable tree

# RSS feeds publish a news site's latest headlines as XML instead of a web
# page — free, no API key. Three sources, so one being down doesn't blank
# the section.
FEEDS = {
    "CoinDesk": "https://www.coindesk.com/arc/outboundfeeds/rss/",
    "Cointelegraph": "https://cointelegraph.com/rss",
    "Decrypt": "https://decrypt.co/feed",
}

# RSS carries no coin tag, so a headline's topic is found by scanning it.
# Kept separate from prices.py's COINGECKO_IDS on purpose: those are ids an
# API expects, these are the words a journalist actually writes. Ambiguous
# English words ("link", "dot", "uni") are deliberately left out.
COIN_NAMES = {
    "BTC": ["bitcoin", "btc"],
    "ETH": ["ethereum", "ether", "eth"],
    "SOL": ["solana", "sol"],
    "ADA": ["cardano", "ada"],
    "DOGE": ["dogecoin", "doge"],
    "XRP": ["ripple", "xrp"],
    "BNB": ["binance", "bnb"],
    "LTC": ["litecoin", "ltc"],
    "DOT": ["polkadot"],
    "MATIC": ["polygon", "matic"],
    "AVAX": ["avalanche", "avax"],
    "LINK": ["chainlink"],
    "TRX": ["tron", "trx"],
    "SHIB": ["shiba", "shib"],
    "ATOM": ["cosmos", "atom"],
    "UNI": ["uniswap"],
}

# shown only if all three feeds fail — evergreen explainers rather than
# headlines, since a hardcoded "Bitcoin hits $81,000" would go stale and
# read as a live price
FALLBACK_ARTICLES = [
    {
        "title": "What is Bitcoin? A beginner's guide to the first cryptocurrency",
        "source": "CoinDesk",
        "url": "https://www.coindesk.com/learn/what-is-bitcoin",
        "topic": "BTC",
    },
    {
        "title": "What is Ethereum and how do smart contracts work?",
        "source": "CoinDesk",
        "url": "https://www.coindesk.com/learn/what-is-ethereum",
        "topic": "ETH",
    },
    {
        "title": "How to store your bitcoin safely",
        "source": "CoinDesk",
        "url": "https://www.coindesk.com/learn/how-to-store-your-bitcoin",
        "topic": "BTC",
    },
    {
        "title": "What is proof-of-stake?",
        "source": "CoinDesk",
        "url": "https://www.coindesk.com/learn/what-is-proof-of-stake",
        "topic": "general",
    },
    {
        "title": "What is DeFi? Decentralized finance explained",
        "source": "CoinDesk",
        "url": "https://www.coindesk.com/learn/what-is-defi",
        "topic": "general",
    },
]


# returns the ticker a headline is about, or "general" if it names no coin
def find_topic(title):
    lowered = title.lower()
    for ticker, names in COIN_NAMES.items():
        for name in names:
            # \b marks a word boundary, so "eth" matches "ETH rallies" but
            # not the "eth" hiding inside "together"
            if re.search(rf"\b{name}\b", lowered):
                return ticker
    return "general"


# RSS dates look like "Thu, 04 Sep 2026 14:30:00 +0000" — converted to the
# ISO format JavaScript's Date can read, or None if the tag is missing or
# malformed
def parse_date(raw):
    if not raw:
        return None
    try:
        return parsedate_to_datetime(raw).isoformat()
    except (TypeError, ValueError):
        return None


# fetches every feed and returns a flat list of {title, url, topic, published}
def fetch_articles():
    articles = []
    for source, feed_url in FEEDS.items():
        try:
            # some sites reject requests that don't look like a browser
            response = requests.get(
                feed_url,
                timeout=10,
                headers={"User-Agent": "Mozilla/5.0"},
            )
            # .content, not .text, so the parser reads the encoding itself
            root = ET.fromstring(response.content)
        except Exception:
            # one dead feed shouldn't take the other two down with it
            continue

        # every article in an RSS document is an <item> tag
        for item in root.iter("item"):
            title = item.findtext("title")
            link = item.findtext("link")
            if title and link:
                articles.append(
                    {
                        "title": title,
                        "url": link,
                        "source": source,
                        "topic": find_topic(title),
                        "published": parse_date(item.findtext("pubDate")),
                    }
                )
    return articles


# given the user's tickers, returns the 5 articles to show, theirs first
def get_news(coins):
    articles = fetch_articles()
    # every feed failed — serve the hardcoded list so the section is never
    # blank, rather than returning nothing
    if not articles:
        return FALLBACK_ARTICLES
    # coins is None until the user finishes onboarding
    coincs = coins or []
    matching = [a for a in articles if a["topic"] in coins]
    rest = [a for a in articles if a["topic"] not in coins]
    return (matching + rest)[:5]

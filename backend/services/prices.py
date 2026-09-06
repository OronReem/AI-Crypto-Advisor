import time  # measures how old a cached price is

import requests  # makes HTTP requests to other servers, like the browser's fetch()

# CoinGecko needs its own full lowercase ids, not the tickers we store —
# matches the fixed list of coins offered in the onboarding quiz
COINGECKO_IDS = {
    "BTC": "bitcoin",
    "ETH": "ethereum",
    "SOL": "solana",
    "ADA": "cardano",
    "DOGE": "dogecoin",
    "XRP": "ripple",
    "BNB": "binancecoin",
    "LTC": "litecoin",
    "DOT": "polkadot",
    "MATIC": "matic-network",
    "AVAX": "avalanche-2",
    "LINK": "chainlink",
    "TRX": "tron",
    "SHIB": "shiba-inu",
    "ATOM": "cosmos",
    "UNI": "uniswap",
}


# {"BTC": (79960, 1757160000.0)} — kept per coin rather than per user, so
# two users who both follow BTC share one lookup. In memory on purpose: a
# restart just costs one extra call, and a price must never outlive the day
_cache = {}
CACHE_SECONDS = 60


# given tickers like ["BTC", "ETH"], returns [{"coin": "BTC", "price": 61240}, ...]
def get_prices(coins):
    now = time.time()
    prices = {}
    stale = []

    for coin in coins:
        cached = _cache.get(coin)
        if cached and now - cached[1] < CACHE_SECONDS:
            prices[coin] = cached[0]
        else:
            stale.append(coin)

    # only the coins we don't already have a fresh price for
    if stale:
        ids = [COINGECKO_IDS[coin] for coin in stale]
        try:
            response = requests.get(
                "https://api.coingecko.com/api/v3/simple/price",
                params={"ids": ",".join(ids), "vs_currencies": "usd"},
                # without this, a hanging CoinGecko would hang our endpoint forever
                timeout=10,
            )
            data = response.json()
        except Exception:
            data = {}

        for coin in stale:
            # CoinGecko rate-limits shared cloud IPs and answers with an error
            # object instead of prices, so the coin's key can simply be absent
            entry = data.get(COINGECKO_IDS[coin])
            if entry and "usd" in entry:
                prices[coin] = entry["usd"]
                _cache[coin] = (entry["usd"], now)
            elif coin in _cache:
                # an old price beats an error card — the cache holds the last
                # value we successfully fetched, however long ago that was
                prices[coin] = _cache[coin][0]

    # rebuilt from `coins` so the order always matches the user's own list.
    # a coin with neither a fresh price nor a cached one is dropped rather
    # than crashing the whole section
    return [
        {"coin": coin, "price": prices[coin]} for coin in coins if coin in prices
    ]

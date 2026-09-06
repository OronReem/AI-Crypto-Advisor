# Architecture

## The three layers

```
+---------------------------------------------------------------+
|  BROWSER            React app, served by Vercel                |
|                     holds the JWT, decides what to render      |
+---------------------------------------------------------------+
                            |
                            |  HTTPS + Authorization: Bearer <token>
                            v
+---------------------------------------------------------------+
|  SERVER             FastAPI app, run by Uvicorn on Render      |
|                     verifies the token, owns all the rules     |
+---------------------------------------------------------------+
              |                                |
              |                                |
              v                                v
+---------------------------+   +-------------------------------+
|  DATABASE                 |   |  OUTSIDE WORLD                |
|  PostgreSQL on Render     |   |  CoinGecko, RSS, OpenRouter   |
|  users, votes, insights   |   |  memegen.link                 |
+---------------------------+   +-------------------------------+
```

The browser never touches the database or any external API directly, with one
exception: the meme *image* is loaded straight from memegen.link by the
`<img>` tag. The backend supplies the URL; the browser fetches the picture.

### Who is allowed to talk to whom

```
                    +-----------+
                    |  BROWSER  |
                    +-----------+
                       |     |
             JSON over |     | just an <img> tag
             HTTPS     |     |
                       v     v
                +---------+  +--------------+
                | BACKEND |  | memegen.link |
                +---------+  +--------------+
                     |
     SQL             |             HTTPS
     +---------------+-------+---------+----------+
     |                       |         |          |
     v                       v         v          v
+----------+          +-----------+ +------+ +------------+
| Postgres |          | CoinGecko | | RSS  | | OpenRouter |
|          |          |  prices   | | x3   | |  insight   |
+----------+          +-----------+ +------+ +------------+
```

**The rules this enforces:**

- The browser talks to exactly one server of ours, and one image host.
- No secret ever reaches the browser. `DATABASE_URL`, `JWT_SECRET` and
  `OPENROUTER_KEY` exist only on the backend.
- Every arrow out of the backend can fail without taking the page with it.
- Nothing talks *back* to us. There are no webhooks, no callbacks — every
  arrow starts because a user opened a page.

---

## Layer 1 — the frontend

```
main.jsx                starts React, mounts the app
   |
App.jsx                 BrowserRouter + the route table
   |
   +-- /signup     -> Signup.jsx
   +-- /login      -> Login.jsx
   +-- /onboarding -> ProtectedRoute -> Onboarding.jsx
   +-- /dashboard  -> ProtectedRoute -> Dashboard.jsx
                                             |
       +----------------+----------------+---+------------+
       |                |                |                |
  PricesSection   InsightSection    NewsSection      MemeSection
       |                |                |                |
       +----------------+----------------+----------------+
                                |
                          VoteButtons          one per item on screen

  lib/api.js          every call to the backend goes through here
  lib/preferences.js  the two rules about a user's answers
```

### Who hands what to whom

**The token.** Three files touch it, and nothing else does:

```
   Login.jsx / Signup.jsx   ---- writes ---->  localStorage
   ProtectedRoute           ---- reads  ---->  ("is one there?")
   lib/api.js               ---- reads  ---->  (adds the Bearer header)
                            ---- clears --->  (on a 401, then -> /login)
```

**The data.** Fetched once at the top, handed down as props:

```
   Dashboard.jsx
       |
       |  GET /me    -> { name, coins, investor_type, content_types }
       |  GET /votes -> { section: { item: direction } }
       |
       |  content_types --> orderSections() --> ['prices','insight',...]
       |
       +--> PricesSection    myVotes = votes.prices
       +--> InsightSection   myVotes = votes.insight
       +--> NewsSection      myVotes = votes.news
       +--> MemeSection      myVotes = votes.meme
                |
                |  each section fetches its own endpoint,
                |  then renders one of these per item:
                v
           VoteButtons
             props: section, topic, item, initialVote = myVotes[item]
                |
                |  on click
                v
           POST /vote
```

Data flows down as props; the only thing flowing back up is a `POST`. No
component reads another component's state.

**Grouped by kind, not by feature.** `pages/` are whole screens, `sections/`
are the four dashboard cards, `components/` are the small reusable pieces,
`lib/` is logic with no UI. With four screens and four sections, this is
easier to hold in your head than a folder per feature.

**Two rules live in `lib/preferences.js`:**

- `isOnboarded(user)` — has this user finished the quiz?
- `orderSections(contentTypes)` — which order do the four cards go in?

Both are presentation logic over data `GET /me` already returns, so they'd
cost a round trip to put on the server for no gain with a single client.

---

## Layer 2 — the backend

```
backend/
|
+-- main.py        the 11 endpoints, CORS, table creation
|      imports from everything below
|
+-- auth.py        create_token()  get_current_user()  pwd_context
+-- schemas.py     the four request shapes FastAPI validates against
+-- tables.py      User, Vote, Insight  (the database schema, as classes)
+-- database.py    the engine and Base — 13 lines
|
+-- services/      one file per outside source, no FastAPI in any of them
    +-- prices.py    CoinGecko  + a 60-second in-memory cache
    +-- news.py      3 RSS feeds + a static fallback
    +-- memes.py     47 hand-written entries, one picked at random
    +-- insight.py   OpenRouter  + the daily cache in Postgres
```

### Who calls whom

Arrows point from a file to the files it imports.

```
                            main.py
                          (the routes)
                                |
        +---------+-------------+-------------+
        |         |             |             |
        v         v             v             v
   schemas.py  auth.py     tables.py      services/
   validates   tokens +    User, Vote,    prices.py
   the body    passwords   Insight        news.py
                  |            |          memes.py
                  |            |          insight.py
                  +-----+------+              |
                        |                     |
                        v                     |
                   database.py                |
                   engine, Base <-------------+
                                       (only insight.py, for
                                        the daily cache)
```

**`database.py` is at the bottom of everything.** It's 13 lines and imports
nothing else from the project, which is what keeps this graph free of cycles.

**Three of the four services import nothing from the project at all** —
`prices.py`, `news.py` and `memes.py` only reach outward:

```
   prices.py   ---> CoinGecko
   news.py     ---> CoinDesk / Cointelegraph / Decrypt RSS
   memes.py    ---> nothing (a static list in the file)
   insight.py  ---> OpenRouter  +  Postgres (its daily cache)
```

**Why `services/` exists at all.** Those four files know nothing about HTTP,
tokens or FastAPI — they take plain arguments and return plain data. That's
what makes them testable in isolation, and it's why every one of them could be
run from a one-line script during the build to prove it worked before any
endpoint existed.

### The endpoints

| Method | Path | Token? | What it does |
|---|---|---|---|
| GET | `/health` | no | `SELECT 1` — proves the DB connection is alive |
| POST | `/signup` | no | Creates a user, returns a token |
| POST | `/login` | no | Verifies the password, returns a token |
| GET | `/me` | yes | The user's own row, preferences included |
| POST | `/onboarding` | yes | Saves the three quiz answers |
| POST | `/vote` | yes | Records a vote (upsert) |
| GET | `/votes` | yes | Every item this user has voted on |
| GET | `/dashboard/prices` | yes | Their coins, priced |
| GET | `/dashboard/news` | yes | 5 articles, theirs first |
| GET | `/dashboard/meme` | yes | One random meme |
| GET | `/dashboard/insight` | yes | Today's AI insight |

Four separate dashboard endpoints rather than one combined response, so a slow
or failing source degrades one card instead of the whole page.

---

## Layer 3 — the data

```
                users
   +--------------------------------+
   | id            PK               |
   | email         UNIQUE           |
   | name                           |
   | password_hash   (bcrypt)       |
   | coins           TEXT[]  NULL   |  <- NULL until the quiz is done
   | investor_type   TEXT    NULL   |
   | content_types   TEXT[]  NULL   |
   +--------------------------------+
            |                    |
            | 1:many             | 1:many
            v                    v
   +----------------------+   +---------------------------+
   |       votes          |   |        insights           |
   | id          PK       |   | id          PK            |
   | user_id     FK       |   | user_id     FK            |
   | section              |   | date        DATE          |
   | topic                |   | insight     TEXT          |
   | item                 |   | topic       TEXT          |
   | direction            |   |                           |
   | created_at           |   | UNIQUE (user_id, date)    |
   |                      |   |   -> one insight per user |
   | UNIQUE (user_id,     |   |      per day. This index  |
   |   section, item,     |   |      IS the cache.        |
   |   date(created_at))  |   +---------------------------+
   |   -> one vote per    |
   |      item per day    |
   +----------------------+
```

**`topic` vs `item` — the distinction the whole vote table rests on.**

```
  topic = what the vote is ABOUT     -> the training signal
  item  = the exact thing SHOWN      -> what makes two votes distinct

  section    topic    item
  --------------------------------------------------------
  prices     BTC      BTC                    (same value)
  news       BTC      https://coindesk...    (the article URL)
  meme       DOGE     woman-cat-doge-zero    (that meme's slug)
  insight    ETH      17                     (the insights row id)
```

Two different Dogecoin memes share `topic = "DOGE"`. If the constraint were on
`topic`, the second vote would overwrite the first — losing a real opinion
rather than deduplicating a misclick. Keying on `item` keeps them apart.

**The date in the constraint** means re-voting the same item on the same day
updates that row (a misclick, corrected), while voting on it a different day
creates a new one (a genuine change of mind, preserved).

**`NULL` preferences are deliberate.** Rather than writing default coins into
a new user's row, the columns stay `NULL` and defaults are applied at the
moment of use. Otherwise nothing downstream could tell *"the user chose BTC"*
from *"the system guessed BTC"* — and this data is the product.

---

## How a request actually flows

### Logging in

```
  Login.jsx                 POST /login  {email, password}
      |                            |
      |                            v
      |                     main.py: login()
      |                            |
      |                     SELECT * FROM users WHERE email = ...
      |                            |
      |                     pwd_context.verify(typed, stored_hash)
      |                            |
      |                     create_token(user.id)   <- signed with JWT_SECRET
      |                            |
      |<--------------------- {"token": "eyJhbGc..."}
      |
  localStorage.setItem('token', ...)
      |
  GET /me  ->  isOnboarded(user)?
      |
      +-- no  -> navigate('/onboarding')
      +-- yes -> navigate('/dashboard')
```

Nothing is ever decrypted. The stored hash is compared against a fresh hash of
what was typed.

### Loading the dashboard

Six requests leave the browser at once, none waiting on another:

```
  Dashboard.jsx  --> GET /me      --> section order + the user's name
                 --> GET /votes   --> {section: {item: direction}}
                          |
                          +--> passed down as the myVotes prop
                                so each button starts already highlighted

  PricesSection  --> GET /dashboard/prices   --> cache hit? -> CoinGecko
  NewsSection    --> GET /dashboard/news     --> 3 RSS feeds -> sort -> 5
  MemeSection    --> GET /dashboard/meme     --> random.choice(MEMES)
  InsightSection --> GET /dashboard/insight  --> today's row? -> OpenRouter
```

Each card renders `Loading…`, then its own content or its own error. One
failure never blanks the page.

### Every protected request

```
  authFetch(path)
      |
      +-- reads the token from localStorage
      +-- adds  Authorization: Bearer <token>
      |
      v
  get_current_user()  (a FastAPI dependency, so it runs before the route)
      |
      +-- jwt.decode(token, JWT_SECRET)   verifies signature AND expiry
      |        |
      |        +-- invalid or expired -> 401
      |
      +-- SELECT * FROM users WHERE id = payload["sub"]
      |
      v
  the route function runs, with the real User object
      |
  ... if a 401 came back instead:
      |
  authFetch clears the token and redirects to /login
```

The token carries only the user id. Everything else — coins, investor type —
is read from the database, so a tampered token can't change what a user is
allowed to see.

---

## Decisions worth defending

**JWT in `localStorage`, not an httpOnly cookie.** Cookies are the more secure
choice against XSS. The trade was accepted knowingly: the app renders no
user-supplied HTML, React escapes by default, and the token expires in 24
hours. Cookies would have added CORS and cookie-attribute configuration to a
project where the attack surface they defend against doesn't exist.

**Frontend routing is not a security control.** `ProtectedRoute` only checks
that a token *exists* — verifying the signature needs the secret, which only
the server has. That's deliberate: bypassing it only hides your own data from
yourself. Anything that would expose someone else's data is guarded on the
server, and the quiz limits are enforced by Pydantic on the backend as well as
in the UI.

**Three caches, three different mechanisms, for three different reasons.**

```
  prices    60 seconds, in memory, keyed per coin
            -> CoinGecko's free tier is ~5-15 calls/min and every page
               load was calling it; losing the cache on restart costs
               one extra call

  insight   one day, in Postgres, keyed per user
            -> OpenRouter's free tier is 50 requests/day, and Render's
               free tier spins down when idle, which would empty an
               in-memory cache exactly when a reviewer arrives

  news      not cached at all
            -> RSS has no quota, so a cache would save nothing
```

**Every external source has a failure path, and each one was tested by
breaking it.** News falls back to a hand-picked list; the AI insight falls back
to a fixed message; prices and memes report a section-level error. The
fallbacks were verified by deliberately breaking the real sources, not by
reading the code.

**Section order is computed in the browser.** It's presentation logic over
`content_types`, which `GET /me` already returns. Putting it on the server
would mean another endpoint or another derived field for no benefit — with one
client. The moment a second client exists, that rule and `isOnboarded()` move
server-side together.

---

## Not built, on purpose

- **No tests.** Verified by hand at every step, including breaking each
  external source to confirm its fallback.
- **No refresh tokens.** One 24-hour JWT; expiry redirects to login.
- **Votes are collected, not consumed.** The assignment asks for the signal to
  be stored. With enough of it, the obvious first use is ranking: order each
  section by the topics a user has upvoted, and drop repeat downvotes.
- **Changing preferences doesn't regenerate today's insight.** It's the
  insight of the *day*; new preferences apply from tomorrow.
- **No CI.** A pipeline with no tests to run is decoration.

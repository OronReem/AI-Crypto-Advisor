# Using stored feedback to improve recommendations

A written suggestion, not an implementation — the assignment lists this as a
bonus and does not ask for code.

Today the app collects votes and stores them. Nothing reads them back. This is
what I would build on top of that data, in the order I would build it.

## What the data already gives us

Every vote is `(user_id, section, topic, item, direction, created_at)`.

Two fields carry the signal. **`topic`** is the coin the item was about — it
generalizes, because "this user likes BTC content" applies to tomorrow's BTC
article as much as today's. **`item`** is the exact thing shown, which is what
stops two different DOGE memes collapsing into one opinion.

## Step 1 — a preference tally per user

No new table and no model. One query over `votes`, grouped by user and topic:

```
  BTC    5 up   1 down
  ETH    2 up   0 down
  DOGE   0 up   3 down
```

Computed on demand rather than stored, so it is always current and there is
nothing to keep in sync. The whole history counts — the schema deliberately
writes a new row per day instead of overwriting, so the record of what someone
liked six months ago still exists.

## Step 2 — feed the tally into the AI insight

The insight prompt already receives the user's coins and investor type. Adding
the tally gives the model something the quiz cannot: what this person actually
responded to.

The effect is immediate and visible — a user who keeps downvoting DOGE
insights stops getting them, without ever editing their preferences.

## Step 3 — let the tally order the other sections

**News** currently moves articles matching the user's chosen coins to the
front. It could rank by the tally instead, so a coin they picked but
consistently downvote sinks below one they keep upvoting.

**Memes** are drawn at random. They could be weighted toward liked topics,
with repeatedly disliked ones suppressed.

Both are ordering changes over content the app already fetches. Nothing new is
called, and nothing new is stored.

## The gap: we only record what people voted on

Most items get no vote at all, and right now that is indistinguishable from
never having been seen. Those are opposite signals — "I saw it and shrugged"
versus "it never appeared" — and the data cannot tell them apart.

For a tally, this does not matter: counting explicit likes and dislikes works
fine on votes alone. It matters the moment you want to train a model, because
the model would learn only from the small, self-selected slice of content
people felt strongly enough to click on.

**The cheapest fix reuses the table we have.** On each dashboard render, write
a row for every item shown with `direction = 'shown'`. The existing unique
index on `(user_id, section, item, date)` dedupes them for free, so a refresh
does not pile up duplicates.

Two details that would need care:

- **The impression write must not overwrite a real vote.** `POST /vote` uses
  `ON CONFLICT DO UPDATE SET direction`. An impression has to use
  `ON CONFLICT DO NOTHING`, or a second page load would reset a thumbs-up
  back to `'shown'`.
- **The table stops meaning one thing.** `votes` would hold impressions and
  opinions together, so every existing query needs `WHERE direction != 'shown'`.
  That is a real cost, and the reason some systems keep impressions in their
  own table instead.

A second implicit signal is available for almost nothing: news headlines are
links, so **a click is a genuine "this interested me."** Weaker than a
thumbs-up, but it covers far more items than voting ever will.

## Step 4 — a learned ranking model

Only once there is enough data, and only after impressions exist.

The framing: given a user and a candidate item, predict the probability of an
upvote, and order by that. Features would come from the user (their coins,
investor type, their tally), the item (section, topic, source, age) and the
interaction between them. Labels are the votes: upvote positive, downvote
negative, shown-and-ignored a weak negative at much lower weight — most people
simply do not vote on things they are fine with.

Worth being blunt about the volume: a handful of users voting a few times a day
is nowhere near enough to beat the tally from step 1. For a long time the
simpler system would be the better one.

**Cold start** is already handled. A brand-new user has no votes, which is
exactly what the onboarding quiz is for — it stays the fallback ranking until
enough feedback accumulates.

## How you would know it worked

Not by inspecting the model. By measuring whether the share of shown items
that get an upvote rises — for users the change was applied to, against users
it was not, over the same period.

That measurement is only possible once impressions are logged, which is the
second reason to do it.

If the number does not move, the ranking is not earning its complexity, and
the simpler version should stay.

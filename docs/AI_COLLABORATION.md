# How this project was built with AI assistance

## The tools

**Claude and Gemini, in the browser** — used for depth. Understanding each
technology the assignment implied, mapping the options at every decision point,
and putting the same question to both models to see whether the answers held up.

**Claude Code, in the IDE** — the planner and executor. It held the
specification, the roadmap and the decision log, and wrote the code against the
real repository under the rules below.

## Understanding first

Before any code, I worked through the assignment until I knew exactly which
technologies each requirement implied, and what each one actually does. That's
where the stack was decided — React with plain JavaScript, FastAPI,
PostgreSQL, JWT — with the alternatives weighed rather than defaulted into.

## The plan

That understanding became a written specification, and the specification
became a roadmap: 10 phases, ~84 numbered steps. Each step is one feature
built all the way through — database, backend, frontend — and confirmed
working in the browser before the next one starts.

## The loop

Every step ran the same way:

1. **What** we were building. Then stop.
2. **Why** it was worth building that way. Then stop.
3. **How** — the code, explained line by line.

Three separate beats, so I approved the reasoning before seeing any code. Any
real fork in the road arrived as two or three options with their trade-offs,
and I picked. Every one of those choices is written down in a decision log,
with the options that lost.

I ran every command myself, and every step ended in the browser or in the
database — not in a code review.

## Where I corrected it

Two examples worth naming.

**Handling a failed AI insight.** When all three language models are
unavailable, the assistant proposed a short retry window so the section could
recover within the hour. I chose to cache the failure for the rest of the day
instead. OpenRouter's free tier allows fifty requests, and each attempt tries
three models — so a user refreshing during an outage would exhaust the entire
daily quota in seventeen page loads. Protecting the quota mattered more than
recovering quickly.

**Showing votes that had already been cast.** I noticed that votes were saving
correctly but the buttons reset to blank on every refresh, which reads as a
bug even though the data was intact. The proposed fix looked up the current
day's votes — but a news article stays in the feed for several days, so
yesterday's vote on it would still appear blank. The design changed to the
most recent vote per item regardless of date, which also means a meme
downvoted last week stays downvoted when it reappears.

## Where it was ahead of me

Two things, consistently.

**Testing my plans against concrete cases.** My original design made a vote
unique per user, section and topic. Traced against a real example — two
different Dogecoin memes on the same day — that rule silently overwrites the
first vote with the second. The fix was to key votes on the exact item shown,
scoped to a single day.

**Framework behaviour that isn't guessable.** Postgres refuses to index a date
derived from a timezone-aware column. React ignores a changed prop in
`useState` after the first render. Neither is something you reason your way
to; both were one question away.

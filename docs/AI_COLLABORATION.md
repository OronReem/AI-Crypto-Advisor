# How this project was built with AI assistance

## The tools

**Claude and Gemini in the browser** for working out what to build and for
checking one answer against the other. **Claude Code in the IDE** for writing
the code against the real repo.

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

Two worth naming:

- When every language model fails, it proposed a short retry window so the
  section could recover quickly. I chose to cache the failure for the rest of
  the day instead: OpenRouter's free tier allows 50 requests, and a user
  refreshing during an outage would exhaust that in seventeen loads.
- I found that votes were saving correctly but the buttons reset on refresh —
  and that scoping the fix to the current day would break news articles, which
  stay in the feed for several days.

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

import { useState, useEffect } from 'react'
import { authFetch } from '../lib/api.js'

// section/topic/item are passed in by whichever section renders this —
// same component works unmodified in Prices, News, Meme, and Insight.
// initialVote is this user's last recorded vote on this item, or undefined.
function VoteButtons({ section, topic, item, initialVote }) {
  const [myVote, setMyVote] = useState(initialVote || null)

  // the section usually renders before /votes has returned, so the first
  // value of initialVote is undefined — this catches it when it arrives
  useEffect(() => {
    if (initialVote) setMyVote(initialVote)
  }, [initialVote])

  async function handleVote(direction) {
    // update the screen immediately, before the server even replies —
    // this is "optimistic UI": assume success, since it usually succeeds
    setMyVote(direction)

    await authFetch('/vote', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ section, topic, item, direction }),
    })
  }

  // shared look for both buttons — only whether myVote matches differs
  function buttonClasses(direction) {
    const base = 'flex h-7 w-7 items-center justify-center rounded-full border transition'
    if (myVote === direction) {
      return `${base} border-gold bg-gold/15`
    }
    return `${base} border-ink-muted/20 grayscale opacity-40 hover:opacity-70`
  }

  return (
    <div className="flex gap-2">
      <button onClick={() => handleVote('up')} aria-label="Vote up" className={buttonClasses('up')}>
        👍
      </button>
      <button onClick={() => handleVote('down')} aria-label="Vote down" className={buttonClasses('down')}>
        👎
      </button>
    </div>
  )
}

export default VoteButtons

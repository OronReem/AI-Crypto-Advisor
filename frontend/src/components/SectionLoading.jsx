import { useState, useEffect } from 'react'

// "Loading…" at first, then an explanation if it drags on. The backend is on
// a free tier that sleeps when idle, so the first request after a quiet
// period can take about a minute — without this it just looks broken.
function SectionLoading() {
  const [slow, setSlow] = useState(false)

  useEffect(() => {
    const timer = setTimeout(() => setSlow(true), 3000)
    // clears the timer if the data arrives first and this unmounts
    return () => clearTimeout(timer)
  }, [])

  return (
    <p className="text-sm text-ink-muted">
      {slow
        ? 'Waking the server up — the free tier sleeps when idle, so this first load can take up to a minute.'
        : 'Loading…'}
    </p>
  )
}

export default SectionLoading

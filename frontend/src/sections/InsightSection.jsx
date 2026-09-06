import { useState, useEffect } from 'react'
import { authFetch } from '../lib/api.js'
import VoteButtons from '../components/VoteButtons.jsx'
import SectionError from '../components/SectionError.jsx'

function InsightSection({ myVotes }) {
  const [insight, setInsight] = useState(null)
  const [failed, setFailed] = useState(false)

  // runs once after the first render — the empty array is what limits it to once
  useEffect(() => {
    async function loadInsight() {
      try {
        const response = await authFetch('/dashboard/insight')
        if (!response.ok) throw new Error(response.status)
        const data = await response.json()
        setInsight(data)
      } catch {
        setFailed(true)
      }
    }
    loadInsight()
  }, [])

  if (failed) {
    return <SectionError />
  }

  if (insight === null) {
    return <p className="text-sm text-ink-muted">Loading…</p>
  }

  return (
    <div>
      {/* gold rule on the left, the way a pull quote is set */}
      <blockquote className="border-l-2 border-gold/50 pl-4">
        <p className="font-heading text-base leading-relaxed text-ink">
          {insight.insight}
        </p>
      </blockquote>

      <div className="mt-4 flex items-center justify-between gap-4">
        <VoteButtons
          section="insight"
          topic={insight.topic}
          // the insights row id — unique per user per day
          item={String(insight.id)}
          initialVote={myVotes[String(insight.id)]}
        />
        <span className="text-xs uppercase tracking-wide text-ink-muted">
          {insight.topic} · AI generated
        </span>
      </div>
    </div>
  )
}

export default InsightSection

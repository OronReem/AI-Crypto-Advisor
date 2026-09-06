import { useState, useEffect } from 'react'
import { authFetch } from '../lib/api.js'
import VoteButtons from '../components/VoteButtons.jsx'
import SectionError from '../components/SectionError.jsx'
import SectionLoading from '../components/SectionLoading.jsx'

// "4 Sep 2026" — the fallback articles carry no date, so undefined in, null out
function formatDate(iso) {
  if (!iso) return null
  return new Date(iso).toLocaleDateString('en-GB', {
    day: 'numeric',
    month: 'short',
    year: 'numeric',
  })
}

function NewsSection({ myVotes }) {
  const [articles, setArticles] = useState(null)
  const [failed, setFailed] = useState(false)

  // runs once after the first render — the empty array is what limits it to once
  useEffect(() => {
    async function loadNews() {
      try {
        const response = await authFetch('/dashboard/news')
        if (!response.ok) throw new Error(response.status)
        const data = await response.json()
        setArticles(data)
      } catch {
        setFailed(true)
      }
    }
    loadNews()
  }, [])

  if (failed) {
    return <SectionError />
  }

  if (articles === null) {
    return <SectionLoading />
  }

  return (
    // one column on a phone, two side by side from the "sm" width up
    <ul className="grid gap-x-8 sm:grid-cols-2">
      {articles.map((article) => (
        <li
          key={article.url}
          // a hairline rule above every row instead of a box around each
          // the 2nd item is the right column's first row, so it drops its
          // rule too — otherwise the columns start unevenly
          className="flex items-start justify-between gap-3 border-t border-ink-muted/15 py-3 first:border-t-0 sm:[&:nth-child(2)]:border-t-0"
        >
          <div>
            <a
              href={article.url}
              // opens in a new tab, and stops that tab from touching ours
              target="_blank"
              rel="noopener noreferrer"
              className="text-sm font-semibold leading-snug text-ink decoration-gold/40 underline-offset-4 hover:underline hover:text-gold"
            >
              {article.title}
            </a>
            <p className="mt-1 text-xs text-ink-muted">
              {article.source}
              {/* the separator only appears when there's a date to separate */}
              {formatDate(article.published) && (
                <span className="tabular-nums">
                  {' · '}
                  {formatDate(article.published)}
                </span>
              )}
            </p>
          </div>
          {/* shrink-0 stops the buttons being squeezed by a long headline */}
          <div className="shrink-0">
            <VoteButtons
              section="news"
              topic={article.topic}
              item={article.url}
              initialVote={myVotes[article.url]}
            />
          </div>
        </li>
      ))}
    </ul>
  )
}

export default NewsSection

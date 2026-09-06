import { useState, useEffect } from 'react'
import { authFetch } from '../lib/api.js'
import VoteButtons from '../components/VoteButtons.jsx'
import CoinIcon from '../components/CoinIcon.jsx'
import SectionError from '../components/SectionError.jsx'
import SectionLoading from '../components/SectionLoading.jsx'

function PricesSection({ myVotes }) {
  const [prices, setPrices] = useState(null)
  const [failed, setFailed] = useState(false)

  // runs once after the first render — the empty array is what limits it to once
  useEffect(() => {
    async function loadPrices() {
      try {
        const response = await authFetch('/dashboard/prices')
        // a 500 or 404 is a successful fetch with a bad status, so it never
        // throws — this is what catches it
        if (!response.ok) throw new Error(response.status)
        const data = await response.json()
        setPrices(data)
      } catch {
        setFailed(true)
      }
    }
    loadPrices()
  }, [])

  if (failed) {
    return <SectionError />
  }

  if (prices === null) {
    return <SectionLoading />
  }

  // the backend drops any coin it has neither a fresh nor a cached price for
  if (prices.length === 0) {
    return <SectionError />
  }

  return (
    <div className="grid grid-cols-2 gap-3 sm:grid-cols-3">
      {prices.map((row) => (
        <div
          key={row.coin}
          className="rounded-xl border border-ink-muted/15 p-4"
        >
          <div className="mb-3 flex items-center gap-2">
            <CoinIcon coin={row.coin} />
            <span className="text-sm text-ink-muted">{row.coin}</span>
          </div>
          <div className="tabular-nums text-lg font-semibold text-ink">
            ${row.price.toLocaleString()}
          </div>
          <div className="mt-3">
            <VoteButtons
              section="prices"
              topic={row.coin}
              item={row.coin}
              initialVote={myVotes[row.coin]}
            />
          </div>
        </div>
      ))}
    </div>
  )
}

export default PricesSection

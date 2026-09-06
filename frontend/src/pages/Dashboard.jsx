import { useState, useEffect } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { authFetch } from '../lib/api.js'
import { orderSections } from '../lib/preferences.js'
import PricesSection from '../sections/PricesSection.jsx'
import InsightSection from '../sections/InsightSection.jsx'
import NewsSection from '../sections/NewsSection.jsx'
import MemeSection from '../sections/MemeSection.jsx'

// each section name maps to its heading and the component that fills the card
const SECTIONS = {
  prices: { title: 'Coin Prices', Component: PricesSection },
  insight: { title: 'Your Personal Insight', Component: InsightSection },
  news: { title: 'Market News', Component: NewsSection },
  meme: { title: 'Joke of the Day', Component: MemeSection },
}

// e.g. "Friday, 5 September 2026"
const TODAY = new Date().toLocaleDateString('en-GB', {
  weekday: 'long',
  day: 'numeric',
  month: 'long',
  year: 'numeric',
})

function Dashboard() {
  const [user, setUser] = useState(null)
  const [order, setOrder] = useState([])

  // {section: {item: direction}} — fetched once here and handed to each
  // section, rather than four components each asking for the same thing
  const [votes, setVotes] = useState({})

  const navigate = useNavigate()

  // runs once after the first render — the empty array is what limits it to once
  useEffect(() => {
    async function loadUser() {
      try {
        const response = await authFetch('/me')
        if (!response.ok) throw new Error(response.status)
        const data = await response.json()
        setUser(data)
        setOrder(orderSections(data.content_types))
      } catch {
        // /me is what decides the section order, so without it we can't know
        // which sections to draw — fall back to the default order and let
        // each section report its own failure
        setOrder(orderSections(null))
      }
    }
    loadUser()

    async function loadVotes() {
      try {
        const response = await authFetch('/votes')
        if (!response.ok) throw new Error(response.status)
        setVotes(await response.json())
      } catch {
        // no highlights is a fine degradation — the sections still work
      }
    }
    loadVotes()
  }, [])

  function handleSignOut() {
    localStorage.removeItem('token')
    navigate('/login')
  }

  return (
    <div className="min-h-screen bg-warm-white">
      <header className="mx-auto max-w-3xl px-6 pt-10 pb-6">
        <div className="flex flex-wrap items-end justify-between gap-4">
          <div>
            <h1 className="font-heading text-3xl text-ink">
              {user ? `Welcome back, ${user.name}` : 'Welcome back'}
            </h1>
            <p className="mt-1 text-sm text-ink-muted">{TODAY}</p>
          </div>

          <div className="flex items-center gap-3">
            <Link
              to="/onboarding"
              className="rounded-lg border border-ink-muted/30 px-4 py-2 text-sm text-ink transition hover:border-gold"
            >
              Edit preferences
            </Link>
            <button
              onClick={handleSignOut}
              className="rounded-lg px-4 py-2 text-sm text-ink-muted transition hover:text-ink"
            >
              Sign out
            </button>
          </div>
        </div>
      </header>

      <main className="mx-auto max-w-3xl space-y-6 px-6 pb-16">
        {order.map((name) => {
          // capitalised, because JSX only treats capitalised names as components
          const { title, Component } = SECTIONS[name]
          return (
            <section
              key={name}
              className="rounded-3xl bg-white p-6 shadow-sm"
            >
              <h2 className="mb-4 font-heading text-lg text-gold">{title}</h2>
              {/* each section gets only its own slice, {} until /votes lands */}
              <Component myVotes={votes[name] || {}} />
            </section>
          )
        })}
      </main>
    </div>
  )
}

export default Dashboard

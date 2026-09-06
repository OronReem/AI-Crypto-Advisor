import { useState, useEffect } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { authFetch } from '../lib/api.js'
import { isOnboarded } from '../lib/preferences.js'

// fixed list — every option is recognised by both CoinGecko and CryptoPanic
const COIN_OPTIONS = [
  'BTC', 'ETH', 'SOL', 'ADA', 'DOGE', 'XRP', 'BNB', 'LTC',
  'DOT', 'MATIC', 'AVAX', 'LINK', 'TRX', 'SHIB', 'ATOM', 'UNI',
]

const INVESTOR_TYPES = [
  'HODLer', 'Day Trader', 'Swing Trader', 'NFT Collector',
  'Scalper', 'DeFi Yield Farmer', 'Institutional Investor',
]

// id is what we store and order sections by; label is what the user reads
const CONTENT_TYPES = [
  { id: 'news', label: 'Market News' },
  { id: 'prices', label: 'Coin Prices' },
  { id: 'insight', label: 'AI Insight' },
  { id: 'meme', label: 'Fun Meme' },
]

// adds value to the list if missing, removes it if already there
function toggleInList(list, setList, value) {
  if (list.includes(value)) {
    setList(list.filter((item) => item !== value))
  } else {
    setList([...list, value])
  }
}

// the look of one option button, in its three possible states
function pillClasses(selected, disabled) {
  const base =
    'cursor-pointer select-none rounded-lg border px-4 py-2 text-sm transition'
  if (disabled) {
    return `${base} border-ink-muted/20 text-ink-muted/50 cursor-not-allowed`
  }
  if (selected) {
    return `${base} bg-gold border-gold text-white`
  }
  return `${base} bg-white border-ink-muted/30 text-ink hover:border-gold`
}

function Onboarding() {
  const [coins, setCoins] = useState([])
  const [investorType, setInvestorType] = useState('')
  const [contentTypes, setContentTypes] = useState([])
  const [error, setError] = useState('')

  // true while a save is in flight, so the button can't be clicked twice
  const [busy, setBusy] = useState(false)

  // how many blocks are visible — only ever counts up, so nothing vanishes
  const [revealed, setRevealed] = useState(1)

  // true when the user already answered once, so this visit is an edit
  const [isEditing, setIsEditing] = useState(false)

  // hides the form until the /me check is done, so saved answers don't pop in
  const [loading, setLoading] = useState(true)

  // lets this component change the URL from code, once the save succeeds
  const navigate = useNavigate()

  // runs once on mount — if answers already exist, load them into the form
  useEffect(() => {
    async function loadExisting() {
      try {
        const response = await authFetch('/me')
        if (!response.ok) throw new Error(response.status)
        const user = await response.json()
        if (isOnboarded(user)) {
          setCoins(user.coins)
          setInvestorType(user.investor_type)
          setContentTypes(user.content_types)
          setIsEditing(true)
        }
      } catch {
        // couldn't read existing answers — show the empty quiz rather than
        // leaving the page stuck on "Loading your preferences…"
        setError("Couldn't load your saved answers.")
      } finally {
        setLoading(false)
      }
    }
    loadExisting()
  }, [])

  // re-runs whenever an answer changes, opening up the next block
  useEffect(() => {
    let target = 1
    if (coins.length > 0) target = 2
    if (target === 2 && investorType !== '') target = 3
    if (target === 3 && contentTypes.length > 0) target = 4
    setRevealed((current) => Math.max(current, target))
  }, [coins, investorType, contentTypes])

  const isValid =
    coins.length >= 1 && investorType !== '' && contentTypes.length >= 1

  async function handleSubmit(e) {
    // stops the browser's default "reload the page on submit" behaviour
    e.preventDefault()
    setError('')
    setBusy(true)

    try {
      const response = await authFetch('/onboarding', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          coins: coins,
          investor_type: investorType,
          content_types: contentTypes,
        }),
      })

      if (response.ok) {
        navigate('/dashboard')
      } else {
        setError('Could not save your answers. Please try again.')
      }
    } catch {
      setError("Couldn't reach the server. Please try again.")
    } finally {
      setBusy(false)
    }
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-warm-white flex items-center justify-center p-6">
        <p className="text-ink-muted">Loading your preferences…</p>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-warm-white flex items-center justify-center p-6">
      <div className="bg-white rounded-2xl shadow-md p-8 w-full max-w-2xl">
        <h1 className="font-heading text-3xl text-ink mb-2 text-center">
          {isEditing ? 'Your preferences' : 'Tell us what you follow'}
        </h1>
        <p className="text-ink-muted text-center mb-8">
          {isEditing
            ? 'Change anything below, then save.'
            : 'Three quick questions — your dashboard is built from the answers.'}
        </p>

        <form onSubmit={handleSubmit}>
          <div className="mb-8">
            <h2 className="font-heading text-xl text-ink mb-1">
              Which crypto assets interest you?
            </h2>
            <p className="text-sm text-ink-muted mb-4">
              Pick 1 to 5 · {coins.length} selected
            </p>
            <div className="flex flex-wrap gap-2">
              {COIN_OPTIONS.map((coin) => {
                const selected = coins.includes(coin)
                const disabled = !selected && coins.length >= 5
                return (
                  <label key={coin} className={pillClasses(selected, disabled)}>
                    <input
                      type="checkbox"
                      className="sr-only"
                      checked={selected}
                      onChange={() => toggleInList(coins, setCoins, coin)}
                      disabled={disabled}
                    />
                    {coin}
                  </label>
                )
              })}
            </div>
          </div>

          {revealed >= 2 && (
            <div className="mb-8">
              <h2 className="font-heading text-xl text-ink mb-1">
                What type of investor are you?
              </h2>
              <p className="text-sm text-ink-muted mb-4">Pick one.</p>
              <div className="flex flex-wrap gap-2">
                {INVESTOR_TYPES.map((type) => (
                  <label
                    key={type}
                    className={pillClasses(investorType === type, false)}
                  >
                    <input
                      type="radio"
                      name="investorType"
                      className="sr-only"
                      checked={investorType === type}
                      onChange={() => setInvestorType(type)}
                    />
                    {type}
                  </label>
                ))}
              </div>
            </div>
          )}

          {revealed >= 3 && (
            <div className="mb-8">
              <h2 className="font-heading text-xl text-ink mb-1">
                What content do you want to see?
              </h2>
              <p className="text-sm text-ink-muted mb-4">
                Pick at least one · they set your dashboard's order
              </p>
              <div className="flex flex-wrap gap-2">
                {CONTENT_TYPES.map((option) => (
                  <label
                    key={option.id}
                    className={pillClasses(
                      contentTypes.includes(option.id),
                      false,
                    )}
                  >
                    <input
                      type="checkbox"
                      className="sr-only"
                      checked={contentTypes.includes(option.id)}
                      onChange={() =>
                        toggleInList(contentTypes, setContentTypes, option.id)
                      }
                    />
                    {option.label}
                  </label>
                ))}
              </div>
            </div>
          )}

          {revealed >= 4 && (
            <button
              type="submit"
              disabled={!isValid || busy}
              className="w-full bg-gold text-white rounded-lg px-6 py-3 font-medium transition hover:opacity-90 disabled:cursor-not-allowed disabled:opacity-40"
            >
              {busy ? 'Saving…' : isEditing ? 'Save changes' : 'Save and continue'}
            </button>
          )}

          {error && (
            <p className="mt-4 text-center text-ink-muted">{error}</p>
          )}

          {isEditing && (
            <p className="mt-4 text-center">
              <Link to="/dashboard" className="text-sm text-ink-muted hover:text-gold">
                Back to dashboard
              </Link>
            </p>
          )}
        </form>
      </div>
    </div>
  )
}

export default Onboarding

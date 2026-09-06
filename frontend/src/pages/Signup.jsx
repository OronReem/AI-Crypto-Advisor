import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'

function Signup() {
  const [email, setEmail] = useState('')
  const [name, setName] = useState('')
  const [password, setPassword] = useState('')
  const [message, setMessage] = useState('')
  const [busy, setBusy] = useState(false)

  const navigate = useNavigate()

  async function handleSubmit(e) {
    // stops the browser's default full-page reload on submit
    e.preventDefault()
    setBusy(true)
    setMessage('')

    try {
      const response = await fetch('http://127.0.0.1:8000/signup', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, name, password }),
      })
      const data = await response.json()

      if (!data.token) {
        setMessage(data.detail)
        return
      }

      localStorage.setItem('token', data.token)
      // a brand-new account has no preferences yet, so always start the quiz
      navigate('/onboarding')
    } catch {
      setMessage("Couldn't reach the server. Please try again.")
    } finally {
      setBusy(false)
    }
  }

  return (
    <div className="min-h-screen bg-warm-white flex items-center justify-center p-6">
      <div className="bg-white rounded-2xl shadow-md p-8 w-full max-w-3xl">
        <h1 className="font-heading text-3xl text-ink mb-6 text-center">
          Sign up
        </h1>
        <form
          onSubmit={handleSubmit}
          className="flex flex-col gap-4 items-stretch"
        >
          <input
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            placeholder="Email"
            autoComplete="off"
            className="flex-1 border border-ink-muted/30 rounded-lg px-4 py-3 text-ink placeholder-ink-muted focus:outline-none focus:border-gold"
          />
          <input
            type="text"
            value={name}
            onChange={(e) => setName(e.target.value)}
            placeholder="Name"
            autoComplete="off"
            className="flex-1 border border-ink-muted/30 rounded-lg px-4 py-3 text-ink placeholder-ink-muted focus:outline-none focus:border-gold"
          />
          <input
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            placeholder="Password"
            autoComplete="new-password"
            className="flex-1 border border-ink-muted/30 rounded-lg px-4 py-3 text-ink placeholder-ink-muted focus:outline-none focus:border-gold"
          />
          <button
            type="submit"
            disabled={busy}
            className="shrink-0 whitespace-nowrap bg-gold text-white rounded-lg px-6 py-3 font-medium transition hover:opacity-90 disabled:cursor-not-allowed disabled:opacity-50"
          >
            {busy ? 'Creating account…' : 'Sign up'}
          </button>
        </form>
        {message && (
          <p className="mt-4 text-center text-ink-muted">{message}</p>
        )}
        <p className="mt-4 text-center text-ink-muted">
          Already have an account?{' '}
          <Link to="/login" className="text-gold hover:underline">
            Log in
          </Link>
        </p>
      </div>
    </div>
  )
}

export default Signup

import { useEffect, useState, type FormEvent } from 'react'
import { login, needsSetup, signup } from '../api/auth'

interface LoginPageProps {
  onAuthenticated: (token: string, email: string) => void
}

export default function LoginPage({ onAuthenticated }: LoginPageProps) {
  const [isFirstRun, setIsFirstRun] = useState<boolean | null>(null)
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState<string | null>(null)
  const [submitting, setSubmitting] = useState(false)

  useEffect(() => {
    needsSetup()
      .then(setIsFirstRun)
      .catch(() => setIsFirstRun(false))
  }, [])

  async function handleSubmit(event: FormEvent) {
    event.preventDefault()
    setError(null)
    setSubmitting(true)

    try {
      const result = isFirstRun ? await signup(email, password) : await login(email, password)
      onAuthenticated(result.token, result.email)
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Something went wrong.')
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <div className="page-shell">
      <div className="page-heading">
        <p className="eyebrow">Owner dashboard</p>
        <h1>{isFirstRun ? 'Create your owner account' : 'Log in'}</h1>
        <p className="page-subtext">
          {isFirstRun
            ? 'No owner account exists yet — create the first one to manage repair requests.'
            : 'Log in to review and schedule repair requests.'}
        </p>
      </div>

      <form className="panel settings-panel" onSubmit={handleSubmit}>
        <div className="field">
          <label htmlFor="login-email">Email</label>
          <input
            id="login-email"
            type="email"
            required
            value={email}
            onChange={(event) => setEmail(event.target.value)}
          />
        </div>

        <div className="field">
          <label htmlFor="login-password">Password</label>
          <input
            id="login-password"
            type="password"
            required
            minLength={8}
            value={password}
            onChange={(event) => setPassword(event.target.value)}
          />
        </div>

        {error && <p className="field-hint" style={{ color: 'var(--danger, #e5484d)' }}>{error}</p>}

        <div className="settings-actions">
          <button type="submit" className="btn-primary" disabled={submitting || isFirstRun === null}>
            {isFirstRun ? 'Create account' : 'Log in'}
          </button>
        </div>
      </form>
    </div>
  )
}

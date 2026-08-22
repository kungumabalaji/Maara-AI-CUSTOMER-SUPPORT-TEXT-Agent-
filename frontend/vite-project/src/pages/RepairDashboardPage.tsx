import { useEffect, useState, type FormEvent } from 'react'
import { listPending, scheduleRepair, type PendingRepair } from '../api/repairs'

interface RepairDashboardPageProps {
  token: string
  deepLinkToken: string | null
  onAuthExpired: () => void
}

export default function RepairDashboardPage({ token, deepLinkToken, onAuthExpired }: RepairDashboardPageProps) {
  const [pending, setPending] = useState<PendingRepair[]>([])
  const [selectedToken, setSelectedToken] = useState<string | null>(deepLinkToken)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const [scheduledAt, setScheduledAt] = useState('')
  const [technician, setTechnician] = useState('')
  const [notes, setNotes] = useState('')
  const [submitting, setSubmitting] = useState(false)
  const [justScheduled, setJustScheduled] = useState<string | null>(null)

  function loadPending() {
    setLoading(true)
    setError(null)
    listPending(token)
      .then((rows) => {
        setPending(rows)
        setSelectedToken((current) => current ?? rows[0]?.token ?? null)
      })
      .catch((e) => {
        if (e instanceof Error && e.message.includes('Session')) {
          onAuthExpired()
          return
        }
        setError(e instanceof Error ? e.message : 'Failed to load pending repairs.')
      })
      .finally(() => setLoading(false))
  }

  useEffect(loadPending, [token])

  const selected = pending.find((r) => r.token === selectedToken) ?? null

  async function handleSchedule(event: FormEvent) {
    event.preventDefault()
    if (!selected) return

    setSubmitting(true)
    setError(null)

    try {
      await scheduleRepair(token, selected.token, { scheduledAt: scheduledAt, technician, notes })
      setJustScheduled(selected.token)
      setPending((current) => current.filter((r) => r.token !== selected.token))
      setSelectedToken(null)
      setScheduledAt('')
      setTechnician('')
      setNotes('')
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Failed to schedule this repair.')
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <div className="page-shell">
      <div className="page-heading">
        <p className="eyebrow">Owner dashboard</p>
        <h1>Pending repair requests</h1>
        <p className="page-subtext">Review each intake and schedule it — the customer is notified automatically once you do.</p>
      </div>

      {justScheduled && <p className="settings-saved">Repair confirmed and customer notified.</p>}
      {error && <p className="field-hint" style={{ color: 'var(--danger, #e5484d)' }}>{error}</p>}

      <div className="panel inbox-panel">
        <div className="inbox-list">
          {loading && <p className="page-subtext">Loading…</p>}
          {!loading && pending.length === 0 && <p className="page-subtext">No pending requests.</p>}
          {pending.map((repair) => (
            <button
              type="button"
              key={repair.token}
              className={`inbox-row ${selectedToken === repair.token ? 'active' : ''}`}
              onClick={() => setSelectedToken(repair.token)}
            >
              <div className="inbox-row-top">
                <span className="inbox-customer">{repair.customer_email}</span>
                <span className="inbox-time">{new Date(repair.created_at).toLocaleString()}</span>
              </div>
              <p className="inbox-preview">{repair.summary}</p>
            </button>
          ))}
        </div>

        <div className="inbox-detail">
          {selected ? (
            <>
              <div className="inbox-detail-header">
                <div>
                  <strong>{selected.customer_email}</strong>
                </div>
              </div>

              <p className="page-subtext" style={{ whiteSpace: 'pre-wrap' }}>{selected.summary}</p>

              <form className="settings-panel" onSubmit={handleSchedule}>
                <div className="field">
                  <label htmlFor="scheduled-at">Appointment date &amp; time</label>
                  <input
                    id="scheduled-at"
                    type="datetime-local"
                    required
                    value={scheduledAt}
                    onChange={(event) => setScheduledAt(event.target.value)}
                  />
                </div>

                <div className="field">
                  <label htmlFor="technician">Assigned technician</label>
                  <input
                    id="technician"
                    required
                    value={technician}
                    onChange={(event) => setTechnician(event.target.value)}
                  />
                </div>

                <div className="field">
                  <label htmlFor="notes">Notes (optional)</label>
                  <textarea
                    id="notes"
                    rows={3}
                    value={notes}
                    onChange={(event) => setNotes(event.target.value)}
                  />
                </div>

                <div className="settings-actions">
                  <button type="submit" className="btn-primary" disabled={submitting}>
                    Confirm &amp; notify customer
                  </button>
                </div>
              </form>
            </>
          ) : (
            <p className="page-subtext">Select a pending request to schedule it.</p>
          )}
        </div>
      </div>
    </div>
  )
}

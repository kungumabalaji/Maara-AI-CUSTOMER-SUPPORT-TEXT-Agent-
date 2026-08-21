import { useState, type FormEvent } from 'react'
import type { BotConfig } from '../lib/types'

interface AdminSettingsPageProps {
  botConfig: BotConfig
  onSave: (config: BotConfig) => void
}

export default function AdminSettingsPage({ botConfig, onSave }: AdminSettingsPageProps) {
  const [draft, setDraft] = useState(botConfig)
  const [savedAt, setSavedAt] = useState<string | null>(null)

  function handleSubmit(event: FormEvent) {
    event.preventDefault()
    onSave(draft)
    setSavedAt(new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }))
  }

  return (
    <div className="page-shell">
      <div className="page-heading">
        <p className="eyebrow">Admin</p>
        <h1>Chatbot settings</h1>
        <p className="page-subtext">Changes apply to the widget and full-page chat for this organization.</p>
      </div>

      <form className="panel settings-panel" onSubmit={handleSubmit}>
        <div className="field">
          <label htmlFor="bot-name">Chatbot name</label>
          <input
            id="bot-name"
            value={draft.name}
            onChange={(event) => setDraft({ ...draft, name: event.target.value })}
          />
        </div>

        <div className="field">
          <label htmlFor="welcome-message">Welcome message</label>
          <textarea
            id="welcome-message"
            rows={3}
            value={draft.welcomeMessage}
            onChange={(event) => setDraft({ ...draft, welcomeMessage: event.target.value })}
          />
          <p className="field-hint">Shown as the first message when a customer opens the chat.</p>
        </div>

        <div className="field">
          <label htmlFor="system-prompt">System prompt / instructions</label>
          <textarea
            id="system-prompt"
            rows={6}
            value={draft.systemPrompt}
            onChange={(event) => setDraft({ ...draft, systemPrompt: event.target.value })}
          />
          <p className="field-hint">Sent to Claude with every conversation. Describe tone, scope, and escalation rules.</p>
        </div>

        <div className="settings-actions">
          <button type="submit" className="btn-primary">
            Save changes
          </button>
          {savedAt && <span className="settings-saved">Saved at {savedAt}</span>}
        </div>
      </form>
    </div>
  )
}

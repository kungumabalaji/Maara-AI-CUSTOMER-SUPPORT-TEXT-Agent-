import { useEffect, useState } from 'react'
import type { BotConfig } from './lib/types'
import { defaultBotConfig } from './data/mockData'
import NavBar from './components/NavBar'
import ChatPage from './pages/ChatPage'
import WidgetDemoPage from './pages/WidgetDemoPage'
import AdminSettingsPage from './pages/AdminSettingsPage'
import InboxPage from './pages/InboxPage'
import LoginPage from './pages/LoginPage'
import RepairDashboardPage from './pages/RepairDashboardPage'

export type Page = 'chat' | 'widget' | 'admin' | 'inbox' | 'repairs'

const OWNER_TOKEN_KEY = 'maara_owner_token'
const OWNER_EMAIL_KEY = 'maara_owner_email'

export default function App() {
  const params = new URLSearchParams(window.location.search)
  const deepLinkToken = params.get('token')

  const [page, setPage] = useState<Page>(params.get('view') === 'dashboard' ? 'repairs' : 'chat')
  const [botConfig, setBotConfig] = useState<BotConfig>(defaultBotConfig)
  const [ownerToken, setOwnerToken] = useState<string | null>(() => localStorage.getItem(OWNER_TOKEN_KEY))

  useEffect(() => {
    if (ownerToken) localStorage.setItem(OWNER_TOKEN_KEY, ownerToken)
    else localStorage.removeItem(OWNER_TOKEN_KEY)
  }, [ownerToken])

  function handleAuthenticated(token: string, email: string) {
    setOwnerToken(token)
    localStorage.setItem(OWNER_EMAIL_KEY, email)
  }

  function handleAuthExpired() {
    setOwnerToken(null)
  }

  return (
    <div className="app-shell">
      <div className="ambient ambient-one" />
      <div className="ambient ambient-two" />

      <NavBar page={page} onNavigate={setPage} />

      <main className="app-main">
        {page === 'chat' && <ChatPage botConfig={botConfig} />}
        {page === 'widget' && <WidgetDemoPage botConfig={botConfig} />}
        {page === 'admin' && <AdminSettingsPage botConfig={botConfig} onSave={setBotConfig} />}
        {page === 'inbox' && <InboxPage />}
        {page === 'repairs' && (
          ownerToken ? (
            <RepairDashboardPage token={ownerToken} deepLinkToken={deepLinkToken} onAuthExpired={handleAuthExpired} />
          ) : (
            <LoginPage onAuthenticated={handleAuthenticated} />
          )
        )}
      </main>
    </div>
  )
}

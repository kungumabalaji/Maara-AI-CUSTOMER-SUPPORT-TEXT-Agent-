import { useState } from 'react'
import type { BotConfig } from './lib/types'
import { defaultBotConfig } from './data/mockData'
import NavBar from './components/NavBar'
import ChatPage from './pages/ChatPage'
import WidgetDemoPage from './pages/WidgetDemoPage'
import AdminSettingsPage from './pages/AdminSettingsPage'
import InboxPage from './pages/InboxPage'

export type Page = 'chat' | 'widget' | 'admin' | 'inbox'

export default function App() {
  const [page, setPage] = useState<Page>('chat')
  const [botConfig, setBotConfig] = useState<BotConfig>(defaultBotConfig)

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
      </main>
    </div>
  )
}

import type { BotConfig } from '../lib/types'
import { suggestedPrompts } from '../data/mockData'
import ChatPanel from '../components/ChatPanel'

export default function ChatPage({ botConfig }: { botConfig: BotConfig }) {
  return (
    <div className="page-shell">
      <div className="page-heading">
        <p className="eyebrow">/chat · full page</p>
        <h1>Ask {botConfig.name}</h1>
        <p className="page-subtext">Answers are grounded in your knowledge base, with a human just one click away.</p>
      </div>

      <div className="panel chat-page-panel">
        <aside className="chat-page-rail">
          <p className="rail-label">Suggested topics</p>
          <div className="rail-topics">
            {suggestedPrompts.map((prompt) => (
              <div className="rail-topic" key={prompt}>
                {prompt}
              </div>
            ))}
          </div>
          <div className="rail-divider" />
          <div className="rail-note">
            <strong>Grounded responses</strong>
            <p>Every answer is linked back to your connected knowledge base, and unclear questions get handed to a human.</p>
          </div>
        </aside>
        <ChatPanel botConfig={botConfig} variant="full" />
      </div>
    </div>
  )
}

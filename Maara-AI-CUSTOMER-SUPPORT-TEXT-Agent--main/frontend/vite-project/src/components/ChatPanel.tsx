import { useState } from 'react'
import type { ChatMessage, BotConfig } from '../lib/types'
import { suggestedPrompts } from '../data/mockData'
import { sendChatMessage } from '../api/chat'

function timeNow() {
  return new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
}

interface ChatPanelProps {
  botConfig: BotConfig
  variant?: 'full' | 'widget'
}

export default function ChatPanel({ botConfig, variant = 'full' }: ChatPanelProps) {
  const [messages, setMessages] = useState<ChatMessage[]>([
    { id: 'welcome', role: 'assistant', text: botConfig.welcomeMessage, time: timeNow() },
  ])
  const [draft, setDraft] = useState('')
  const [isTyping, setIsTyping] = useState(false)
  const [handoffRequested, setHandoffRequested] = useState(false)

  async function send(value = draft) {
    const trimmed = value.trim()
    if (!trimmed || isTyping) return

    setMessages((current) => [...current, { id: `u-${current.length}`, role: 'user', text: trimmed, time: timeNow() }])
    setDraft('')
    setIsTyping(true)

    try {
      const { answer } = await sendChatMessage(trimmed)
      setMessages((current) => [
        ...current,
        { id: `a-${current.length}`, role: 'assistant', text: answer, time: timeNow() },
      ])
    } catch {
      setMessages((current) => [
        ...current,
        {
          id: `a-${current.length}`,
          role: 'assistant',
          text: "I couldn't reach the support backend just now. Please make sure the API server is running, or try again shortly.",
          time: timeNow(),
        },
      ])
    } finally {
      setIsTyping(false)
    }
  }

  function requestHandoff() {
    setHandoffRequested(true)
    setMessages((current) => [
      ...current,
      {
        id: `sys-${current.length}`,
        role: 'assistant',
        text: "I've flagged this conversation for a human agent. Someone from the team will jump in shortly.",
        time: timeNow(),
      },
    ])
  }

  return (
    <div className={`chat-panel chat-panel-${variant}`}>
      <header className="chat-panel-header">
        <div className="chat-panel-header-identity">
          <div className="chat-avatar">M</div>
          <div>
            <strong>{botConfig.name}</strong>
            <span className="chat-panel-status">
              <i className="status-dot" />
              {handoffRequested ? 'Agent notified' : 'AI online'}
            </span>
          </div>
        </div>
        <button
          type="button"
          className="btn-ghost btn-handoff"
          onClick={requestHandoff}
          disabled={handoffRequested}
        >
          {handoffRequested ? 'Human requested' : 'Talk to a human'}
        </button>
      </header>

      <div className="chat-panel-body" aria-live="polite">
        {messages.map((message) => (
          <div className={`chat-msg-row ${message.role}`} key={message.id}>
            {message.role === 'assistant' && <div className="chat-avatar chat-avatar-sm">M</div>}
            <div className="chat-msg-content">
              <div className="chat-bubble">{message.text}</div>
              <span className="chat-msg-time">{message.time}</span>
            </div>
          </div>
        ))}
        {isTyping && (
          <div className="chat-msg-row assistant">
            <div className="chat-avatar chat-avatar-sm">M</div>
            <div className="chat-bubble chat-typing">
              <i />
              <i />
              <i />
            </div>
          </div>
        )}
      </div>

      <div className="chat-panel-footer">
        {messages.length <= 2 && (
          <div className="chat-suggestions">
            {suggestedPrompts.map((prompt) => (
              <button type="button" key={prompt} onClick={() => send(prompt)}>
                {prompt}
              </button>
            ))}
          </div>
        )}
        <form
          className="chat-composer"
          onSubmit={(event) => {
            event.preventDefault()
            send()
          }}
        >
          <input
            value={draft}
            onChange={(event) => setDraft(event.target.value)}
            placeholder="Ask a question…"
            aria-label="Message"
          />
          <button className="chat-send" type="submit" aria-label="Send message">
            ↑
          </button>
        </form>
      </div>
    </div>
  )
}

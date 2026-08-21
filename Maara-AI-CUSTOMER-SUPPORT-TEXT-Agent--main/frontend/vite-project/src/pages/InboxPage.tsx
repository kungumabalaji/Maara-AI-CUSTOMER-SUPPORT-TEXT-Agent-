import { useState } from 'react'
import type { InboxConversation } from '../lib/types'
import { mockInbox } from '../data/mockData'
import StatusPill from '../components/StatusPill'

export default function InboxPage() {
  const [conversations, setConversations] = useState<InboxConversation[]>(mockInbox)
  const [selectedId, setSelectedId] = useState(mockInbox[0]?.id)

  const selected = conversations.find((c) => c.id === selectedId) ?? null

  function resolve(id: string) {
    setConversations((current) => current.map((c) => (c.id === id ? { ...c, status: 'resolved' } : c)))
  }

  function claim(id: string) {
    setConversations((current) => current.map((c) => (c.id === id ? { ...c, status: 'with_agent' } : c)))
  }

  return (
    <div className="page-shell">
      <div className="page-heading">
        <p className="eyebrow">Agent inbox</p>
        <h1>Conversations</h1>
        <p className="page-subtext">Conversations flagged with “Talk to a human” land here for your team to pick up.</p>
      </div>

      <div className="panel inbox-panel">
        <div className="inbox-list">
          {conversations.map((conversation) => (
            <button
              type="button"
              key={conversation.id}
              className={`inbox-row ${selectedId === conversation.id ? 'active' : ''}`}
              onClick={() => setSelectedId(conversation.id)}
            >
              <div className="inbox-row-top">
                <span className="inbox-customer">
                  {conversation.unread && <i className="unread-dot" />}
                  {conversation.customerName}
                </span>
                <span className="inbox-time">{conversation.updatedAt}</span>
              </div>
              <p className="inbox-preview">{conversation.preview}</p>
              <div className="inbox-row-bottom">
                <span className="inbox-channel">{conversation.channel}</span>
                <StatusPill status={conversation.status} />
              </div>
            </button>
          ))}
        </div>

        <div className="inbox-detail">
          {selected ? (
            <>
              <div className="inbox-detail-header">
                <div>
                  <strong>{selected.customerName}</strong>
                  <span className="inbox-channel">{selected.channel}</span>
                </div>
                <StatusPill status={selected.status} />
              </div>

              <div className="inbox-detail-messages">
                {selected.messages.map((message) => (
                  <div className={`chat-msg-row ${message.role}`} key={message.id}>
                    {message.role === 'assistant' && <div className="chat-avatar chat-avatar-sm">M</div>}
                    <div className="chat-msg-content">
                      <div className="chat-bubble">{message.text}</div>
                      <span className="chat-msg-time">{message.time}</span>
                    </div>
                  </div>
                ))}
              </div>

              <div className="inbox-detail-actions">
                <button type="button" className="btn-ghost" onClick={() => claim(selected.id)} disabled={selected.status === 'with_agent' || selected.status === 'resolved'}>
                  Assign to me
                </button>
                <button type="button" className="btn-primary" onClick={() => resolve(selected.id)} disabled={selected.status === 'resolved'}>
                  Mark resolved
                </button>
              </div>
            </>
          ) : (
            <p className="page-subtext">Select a conversation to view it.</p>
          )}
        </div>
      </div>
    </div>
  )
}

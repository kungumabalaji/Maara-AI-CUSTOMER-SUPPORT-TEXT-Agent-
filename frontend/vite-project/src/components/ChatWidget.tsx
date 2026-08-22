import { useState } from 'react'
import type { BotConfig } from '../lib/types'
import ChatPanel from './ChatPanel'

export default function ChatWidget({ botConfig }: { botConfig: BotConfig }) {
  const [open, setOpen] = useState(false)

  return (
    <div className="widget-root">
      {open && (
        <div className="widget-panel">
          <ChatPanel botConfig={botConfig} variant="widget" />
        </div>
      )}
      <button
        type="button"
        className="widget-launcher"
        onClick={() => setOpen((value) => !value)}
        aria-label={open ? 'Close support chat' : 'Open support chat'}
      >
        {open ? (
          <svg width="22" height="22" viewBox="0 0 24 24" fill="none" aria-hidden="true">
            <path d="M6 6l12 12M18 6L6 18" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round" />
          </svg>
        ) : (
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none" aria-hidden="true">
            <path
              d="M4 12.5C4 7.81 8.03 4 13 4s9 3.81 9 8.5-4.03 8.5-9 8.5c-1.06 0-2.08-.16-3.02-.47L4 22l1.2-4.32C4.44 16.28 4 14.46 4 12.5Z"
              stroke="currentColor"
              strokeWidth="1.8"
              strokeLinejoin="round"
            />
          </svg>
        )}
      </button>
    </div>
  )
}

import type { ConversationStatus } from '../lib/types'

const LABELS: Record<ConversationStatus, string> = {
  ai: 'AI handling',
  handoff_requested: 'Handoff requested',
  with_agent: 'With agent',
  resolved: 'Resolved',
}

export default function StatusPill({ status }: { status: ConversationStatus }) {
  return <span className={`status-pill status-pill-${status}`}>{LABELS[status]}</span>
}

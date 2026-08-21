import type { BotConfig, InboxConversation } from '../lib/types'

// Placeholder tenant config. In production this is loaded from
// GET /api/v1/settings and edited via the Admin Settings page.
export const defaultBotConfig: BotConfig = {
  name: 'MAARA',
  welcomeMessage:
    "Hi, I'm MAARA. Ask me anything about your account, billing, or getting started — and I'll pull an answer from your knowledge base.",
  systemPrompt:
    'You are a helpful, concise customer support assistant. Answer only from the provided knowledge base context. If you are not confident in an answer, say so and offer to connect the customer with a human agent.',
}

export const suggestedPrompts = [
  'How do I reset my password?',
  'What are your support hours?',
  'How do refunds work?',
]

// Stand-in for a real Claude response until the backend streaming
// endpoint (POST /api/v1/conversations/{id}/messages) is wired in.
const mockAnswers: Record<string, string> = {
  'how do i reset my password?':
    'Go to Settings → Security → Reset password, and we\'ll email you a reset link. Links expire after 24 hours.',
  'what are your support hours?':
    "Our team is online Monday to Friday, 9am–6pm. Outside those hours I'll keep helping, and I can flag your conversation for an agent to follow up.",
  'how do refunds work?':
    'Refunds are processed within 5–7 business days back to your original payment method. Ask me to connect you with an agent if you need one expedited.',
}

export function mockAssistantReply(question: string): string {
  const known = mockAnswers[question.trim().toLowerCase()]
  if (known) return known
  return "I don't have a confirmed answer for that yet from the knowledge base. I can connect you with a human agent, or you can try rephrasing the question."
}

export const mockInbox: InboxConversation[] = [
  {
    id: 'conv-1',
    customerName: 'Priya Shah',
    channel: 'Widget · maara.app/pricing',
    preview: "I was charged twice for my subscription this month, can someone look into it?",
    status: 'handoff_requested',
    updatedAt: '2 min ago',
    unread: true,
    messages: [
      { id: 'm1', role: 'user', text: 'Hey, I think I was double charged this month.', time: '10:02' },
      { id: 'm2', role: 'assistant', text: "I'm sorry about that. I can see this needs a closer look at your billing history — let me flag this for a member of our team.", time: '10:02' },
      { id: 'm3', role: 'user', text: 'Thanks, appreciate it.', time: '10:03' },
    ],
  },
  {
    id: 'conv-2',
    customerName: 'Daniel Osei',
    channel: 'Full page · /chat',
    preview: 'How do I invite teammates to my workspace?',
    status: 'ai',
    updatedAt: '18 min ago',
    unread: false,
    messages: [
      { id: 'm1', role: 'user', text: 'How do I invite teammates to my workspace?', time: '09:41' },
      { id: 'm2', role: 'assistant', text: 'Go to Workspace Settings → Members → Invite, then enter their email. They will get an invite link that expires in 7 days.', time: '09:41' },
    ],
  },
  {
    id: 'conv-3',
    customerName: 'Lena Marks',
    channel: 'Widget · maara.app/docs',
    preview: 'Can I export my data before cancelling?',
    status: 'with_agent',
    updatedAt: '1 hr ago',
    unread: false,
    messages: [
      { id: 'm1', role: 'user', text: 'Can I export my data before cancelling?', time: '08:55' },
      { id: 'm2', role: 'assistant', text: "Yes — you can export everything from Settings → Data → Export. I'll also loop in an agent in case you want help with the cancellation itself.", time: '08:56' },
      { id: 'm3', role: 'assistant', text: 'Agent Kim joined the conversation.', time: '09:10' },
    ],
  },
  {
    id: 'conv-4',
    customerName: 'Tomás Rivera',
    channel: 'Full page · /chat',
    preview: 'Thanks, that solved it!',
    status: 'resolved',
    updatedAt: 'Yesterday',
    unread: false,
    messages: [
      { id: 'm1', role: 'user', text: 'My invoices are not showing the right tax rate.', time: 'Yesterday' },
      { id: 'm2', role: 'assistant', text: 'That usually means your billing address is missing a region — you can add it under Billing → Address.', time: 'Yesterday' },
      { id: 'm3', role: 'user', text: 'Thanks, that solved it!', time: 'Yesterday' },
    ],
  },
]

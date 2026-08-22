export type MessageRole = 'user' | 'assistant'

export interface ChatMessage {
  id: string
  role: MessageRole
  text: string
  time: string
}

export interface BotConfig {
  name: string
  welcomeMessage: string
  systemPrompt: string
}

export type ConversationStatus = 'ai' | 'handoff_requested' | 'with_agent' | 'resolved'

export interface InboxConversation {
  id: string
  customerName: string
  channel: string
  preview: string
  status: ConversationStatus
  updatedAt: string
  unread: boolean
  messages: ChatMessage[]
}

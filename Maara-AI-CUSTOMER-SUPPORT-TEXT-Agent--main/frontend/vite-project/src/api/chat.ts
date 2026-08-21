const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? 'http://localhost:8000'

export interface ChatSource {
  row_id: number
  score: number
  content: string
}

export interface ChatApiResponse {
  answer: string
  sources: ChatSource[]
}

export async function sendChatMessage(message: string): Promise<ChatApiResponse> {
  const response = await fetch(`${API_BASE_URL}/api/chat`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ message }),
  })

  if (!response.ok) {
    const detail = await response.json().catch(() => null)
    throw new Error(detail?.detail ?? `Request failed with status ${response.status}`)
  }

  return response.json()
}

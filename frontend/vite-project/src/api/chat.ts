const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? 'http://localhost:8000'

export interface ChatApiResponse {
  answer: string
  threadId: string
}

export async function sendChatMessage(message: string, threadId?: string): Promise<ChatApiResponse> {
  const response = await fetch(`${API_BASE_URL}/api/repair`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ message, thread_id: threadId }),
  })

  const body = await response.json().catch(() => null)

  if (!response.ok || !body?.success) {
    throw new Error(body?.error ?? `Request failed with status ${response.status}`)
  }

  return { answer: body.answer, threadId: body.thread_id }
}

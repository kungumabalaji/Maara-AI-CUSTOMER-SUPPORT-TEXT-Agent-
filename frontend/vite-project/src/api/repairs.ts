const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? 'http://localhost:8000'

export interface PendingRepair {
  token: string
  thread_id: string
  customer_email: string
  summary: string
  created_at: string
}

async function parseOrThrow(response: Response) {
  const body = await response.json().catch(() => null)
  if (!response.ok) {
    throw new Error(body?.detail ?? `Request failed with status ${response.status}`)
  }
  return body
}

export async function listPending(token: string): Promise<PendingRepair[]> {
  const response = await fetch(`${API_BASE_URL}/api/repair/pending`, {
    headers: { Authorization: `Bearer ${token}` },
  })
  const body = await parseOrThrow(response)
  return body.pending
}

export async function scheduleRepair(
  token: string,
  repairToken: string,
  details: { scheduledAt: string; technician: string; notes: string },
): Promise<void> {
  const response = await fetch(`${API_BASE_URL}/api/repair/schedule/${repairToken}`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      Authorization: `Bearer ${token}`,
    },
    body: JSON.stringify({
      scheduled_at: details.scheduledAt,
      technician: details.technician,
      notes: details.notes,
    }),
  })
  await parseOrThrow(response)
}

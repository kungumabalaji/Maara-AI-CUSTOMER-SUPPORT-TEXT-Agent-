const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? 'http://localhost:8000'

export interface AuthResult {
  token: string
  email: string
}

async function parseOrThrow(response: Response) {
  const body = await response.json().catch(() => null)
  if (!response.ok) {
    throw new Error(body?.detail ?? `Request failed with status ${response.status}`)
  }
  return body
}

export async function needsSetup(): Promise<boolean> {
  const response = await fetch(`${API_BASE_URL}/api/auth/needs-setup`)
  const body = await parseOrThrow(response)
  return body.needs_setup
}

export async function login(email: string, password: string): Promise<AuthResult> {
  const response = await fetch(`${API_BASE_URL}/api/auth/login`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email, password }),
  })
  return parseOrThrow(response)
}

export async function signup(email: string, password: string): Promise<AuthResult> {
  const response = await fetch(`${API_BASE_URL}/api/auth/signup`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email, password }),
  })
  return parseOrThrow(response)
}

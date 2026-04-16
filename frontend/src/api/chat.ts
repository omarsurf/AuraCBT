import type { ChatRequest, ChatResponse } from '../types/chat'

const API_BASE = import.meta.env.VITE_API_URL ?? ''

export async function sendMessage(request: ChatRequest): Promise<ChatResponse> {
  const res = await fetch(`${API_BASE}/chat`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(request),
  })

  if (!res.ok) {
    let detail = `Request failed with status ${res.status}`
    try {
      const err = await res.json()
      if (err.detail) detail = err.detail
    } catch {
      // ignore parse errors
    }
    throw new Error(detail)
  }

  return res.json() as Promise<ChatResponse>
}

export async function checkReadiness(): Promise<boolean> {
  try {
    const res = await fetch(`${API_BASE}/readyz`)
    return res.ok
  } catch {
    return false
  }
}

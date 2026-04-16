import { describe, expect, it, vi, afterEach } from 'vitest'
import { sendMessage, checkReadiness } from './chat'

afterEach(() => {
  vi.restoreAllMocks()
})

describe('sendMessage', () => {
  it('posts messages and returns structured data', async () => {
    vi.stubGlobal('fetch', vi.fn().mockResolvedValue({
      ok: true,
      json: async () => ({
        raw_emotion: 'fear',
        emotion: 'anxiety',
        strategy: 'reassure_and_structure',
        response: "It sounds like you're carrying a lot right now. What feels most uncertain?",
      }),
    }))

    const result = await sendMessage({ messages: [{ role: 'user', content: 'I feel anxious' }] })
    expect(result.emotion).toBe('anxiety')
    expect(result.strategy).toBe('reassure_and_structure')
  })

  it('throws on non-ok response with detail', async () => {
    vi.stubGlobal('fetch', vi.fn().mockResolvedValue({
      ok: false,
      status: 422,
      json: async () => ({ detail: 'messages must not be empty' }),
    }))

    await expect(sendMessage({ messages: [] })).rejects.toThrow('messages must not be empty')
  })

  it('throws generic message when response has no detail', async () => {
    vi.stubGlobal('fetch', vi.fn().mockResolvedValue({
      ok: false,
      status: 500,
      json: async () => ({}),
    }))

    await expect(sendMessage({ messages: [] })).rejects.toThrow('Request failed with status 500')
  })
})

describe('checkReadiness', () => {
  it('returns true when backend responds ok', async () => {
    vi.stubGlobal('fetch', vi.fn().mockResolvedValue({ ok: true }))
    expect(await checkReadiness()).toBe(true)
  })

  it('returns false when fetch throws', async () => {
    vi.stubGlobal('fetch', vi.fn().mockRejectedValue(new Error('network error')))
    expect(await checkReadiness()).toBe(false)
  })
})

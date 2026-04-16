import { describe, expect, it, vi, afterEach } from 'vitest'
import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import App from './App'
import * as chatApi from './api/chat'

afterEach(() => {
  vi.restoreAllMocks()
})

describe('App', () => {
  it('renders empty state with suggestion cards', async () => {
    vi.spyOn(chatApi, 'checkReadiness').mockResolvedValue(true)
    render(<App />)
    expect(await screen.findByText("How are you feeling today?")).toBeInTheDocument()
    expect(screen.getByText("I've been feeling overwhelmed lately")).toBeInTheDocument()
  })

  it('clicking a suggestion fills the input', async () => {
    vi.spyOn(chatApi, 'checkReadiness').mockResolvedValue(true)
    render(<App />)
    await screen.findByText("How are you feeling today?")
    fireEvent.click(screen.getByText("I've been feeling overwhelmed lately"))
    const textarea = screen.getByRole('textbox')
    expect((textarea as HTMLTextAreaElement).value).toBe("I've been feeling overwhelmed lately")
  })

  it('shows assistant reply after sending a message', async () => {
    vi.spyOn(chatApi, 'checkReadiness').mockResolvedValue(true)
    vi.spyOn(chatApi, 'sendMessage').mockResolvedValue({
      raw_emotion: 'fear',
      emotion: 'anxiety',
      strategy: 'reassure_and_structure',
      response: "It sounds like you're carrying a lot right now.",
    })

    render(<App />)
    await screen.findByText("How are you feeling today?")

    const textarea = screen.getByRole('textbox')
    fireEvent.change(textarea, { target: { value: 'I feel worried' } })
    fireEvent.keyDown(textarea, { key: 'Enter', shiftKey: false })

    await waitFor(() =>
      expect(screen.getByText("It sounds like you're carrying a lot right now.")).toBeInTheDocument()
    )
  })

  it('shows error message when sendMessage throws', async () => {
    vi.spyOn(chatApi, 'checkReadiness').mockResolvedValue(true)
    vi.spyOn(chatApi, 'sendMessage').mockRejectedValue(new Error('Backend unavailable'))

    render(<App />)
    await screen.findByText("How are you feeling today?")

    const textarea = screen.getByRole('textbox')
    fireEvent.change(textarea, { target: { value: 'Hello' } })
    fireEvent.keyDown(textarea, { key: 'Enter', shiftKey: false })

    await waitFor(() =>
      expect(screen.getByText('Backend unavailable')).toBeInTheDocument()
    )
  })
})

import { useState, useEffect, useRef, useCallback } from 'react'
import { sendMessage, checkReadiness } from './api/chat'
import type { DisplayMessage, Message } from './types/chat'
import './styles.css'

function generateId(): string {
  return Math.random().toString(36).slice(2, 9)
}

function formatTime(date: Date): string {
  return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
}

// ── Icons ────────────────────────────────────────────────────────────────────

function SendIcon() {
  return (
    <svg width="17" height="17" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.3" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
      <line x1="22" y1="2" x2="11" y2="13" />
      <polygon points="22 2 15 22 11 13 2 9 22 2" />
    </svg>
  )
}

function AlertIcon() {
  return (
    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
      <circle cx="12" cy="12" r="10"/>
      <line x1="12" y1="8" x2="12" y2="12"/>
      <line x1="12" y1="16" x2="12.01" y2="16"/>
    </svg>
  )
}

// Suggestion card icons
function OverwhelmedIcon() {
  return (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
      <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2z"/>
      <path d="M8 15s1.5-2 4-2 4 2 4 2"/>
      <line x1="9" y1="9" x2="9.01" y2="9"/>
      <line x1="15" y1="9" x2="15.01" y2="9"/>
    </svg>
  )
}

function ThoughtsIcon() {
  return (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
      <path d="M9.5 2A2.5 2.5 0 0 1 12 4.5v15a2.5 2.5 0 0 1-4.96-.46 2.5 2.5 0 0 1-1.96-3 2.5 2.5 0 0 1-1.32-4.24 3 3 0 0 1 .34-5.58 2.5 2.5 0 0 1 1.32-4.24 2.5 2.5 0 0 1 4.18-1.98Z"/>
      <path d="M14.5 2A2.5 2.5 0 0 0 12 4.5v15a2.5 2.5 0 0 0 4.96-.46 2.5 2.5 0 0 0 1.96-3 2.5 2.5 0 0 0 1.32-4.24 3 3 0 0 0-.34-5.58 2.5 2.5 0 0 0-1.32-4.24 2.5 2.5 0 0 0-4.18-1.98Z"/>
    </svg>
  )
}

function AnxietyIcon() {
  return (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
      <path d="M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 0 0 0-7.78z"/>
    </svg>
  )
}

function MotivationIcon() {
  return (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
      <polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"/>
    </svg>
  )
}

// ── Subcomponents ─────────────────────────────────────────────────────────────

function TypingIndicator() {
  return (
    <div className="typing-indicator" role="status" aria-label="Assistant is typing">
      <div className="typing-dots">
        <span className="typing-dot" />
        <span className="typing-dot" />
        <span className="typing-dot" />
      </div>
    </div>
  )
}

interface MessageBubbleProps {
  msg: DisplayMessage
}

function MessageBubble({ msg }: MessageBubbleProps) {
  const isUser = msg.role === 'user'
  return (
    <div className={`message-row message-row--${msg.role}`}>
      <div className="message-content">
        <div className={`message-bubble message-bubble--${msg.role}`}>
          {msg.content}
        </div>
        <div className="message-meta">
          {msg.emotion && (
            <span className="message-tag message-tag--emotion" title="Detected emotion">
              {msg.emotion}
            </span>
          )}
          {msg.strategy && (
            <span className="message-tag message-tag--strategy" title="CBT strategy">
              {msg.strategy}
            </span>
          )}
          <time className="message-time" dateTime={msg.timestamp.toISOString()}>
            {formatTime(msg.timestamp)}
          </time>
        </div>
      </div>
    </div>
  )
}

interface EmptyStateProps {
  onChipClick: (text: string) => void
}

const SUGGESTIONS = [
  {
    icon: <OverwhelmedIcon />,
    text: "I've been feeling overwhelmed lately",
    hint: "Let's break it down together",
  },
  {
    icon: <ThoughtsIcon />,
    text: "I'm struggling with negative thoughts",
    hint: "We'll reframe them step by step",
  },
  {
    icon: <AnxietyIcon />,
    text: "I need help managing my anxiety",
    hint: "Practical CBT tools await",
  },
  {
    icon: <MotivationIcon />,
    text: "I feel stuck and unmotivated",
    hint: "We'll find your momentum",
  },
]

function EmptyState({ onChipClick }: EmptyStateProps) {
  return (
    <div className="empty-state">
      <img
        src="/assets/bg-waves.png"
        alt="Person sitting peacefully, surrounded by floating emotion shapes"
        className="empty-state__hero-img"
      />
      <h2 className="empty-state__title">How are you feeling today?</h2>
      <p className="empty-state__desc">
        Your CBT companion is here to listen. Share what's on your mind and together we'll explore healthier thought patterns.
      </p>
      <div className="suggestions" role="list" aria-label="Suggested conversation starters">
        {SUGGESTIONS.map((s) => (
          <button
            key={s.text}
            className="suggestion-card"
            role="listitem"
            onClick={() => onChipClick(s.text)}
          >
            <div className="suggestion-card__icon" aria-hidden="true">
              {s.icon}
            </div>
            <div className="suggestion-card__body">
              <div className="suggestion-card__text">{s.text}</div>
              <div className="suggestion-card__hint">{s.hint}</div>
            </div>
          </button>
        ))}
      </div>
    </div>
  )
}

// ── Main App ──────────────────────────────────────────────────────────────────

type BackendStatus = 'checking' | 'ready' | 'unavailable'

export default function App() {
  const [messages, setMessages] = useState<DisplayMessage[]>([])
  const [input, setInput] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [backendStatus, setBackendStatus] = useState<BackendStatus>('checking')

  const messagesEndRef = useRef<HTMLDivElement>(null)
  const textareaRef = useRef<HTMLTextAreaElement>(null)
  const isLoadingRef = useRef(false)

  useEffect(() => {
    checkReadiness().then((ready) => {
      setBackendStatus(ready ? 'ready' : 'unavailable')
    })
  }, [])

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages, isLoading])

  const handleInputChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    setInput(e.target.value)
    const el = e.target
    el.style.height = 'auto'
    el.style.height = `${Math.min(el.scrollHeight, 130)}px`
  }

  const submit = useCallback(async (text: string) => {
    const trimmed = text.trim()
    if (!trimmed || isLoadingRef.current) return

    setError(null)
    isLoadingRef.current = true
    setIsLoading(true)

    const userMsg: DisplayMessage = {
      id: generateId(),
      role: 'user',
      content: trimmed,
      timestamp: new Date(),
    }

    setMessages((prev) => [...prev, userMsg])
    setInput('')
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto'
    }

    const history: Message[] = [...messages, userMsg].map(({ role, content }) => ({ role, content }))

    try {
      const result = await sendMessage({ messages: history })
      const assistantMsg: DisplayMessage = {
        id: generateId(),
        role: 'assistant',
        content: result.response,
        timestamp: new Date(),
        emotion: result.emotion,
        strategy: result.strategy,
      }
      setMessages((prev) => [...prev, assistantMsg])
      setBackendStatus('ready')
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Something went wrong. Please try again.'
      setError(message)
    } finally {
      isLoadingRef.current = false
      setIsLoading(false)
      textareaRef.current?.focus()
    }
  }, [messages])

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      submit(input)
    }
  }

  const canSubmit = input.trim().length > 0 && !isLoading

  return (
    <div className="app">
      {/* Header */}
      <header className="header">
        <img src="/assets/app-icon.png" alt="CBT Coach logo" className="header__logo" />
        <div className="header__info">
          <h1 className="header__title">CBT Coach</h1>
          <p className="header__subtitle">AI-Powered Cognitive Behavioral Therapy Companion</p>
        </div>
        <div className="header__status" aria-live="polite" aria-atomic="true">
          <span
            className={`header__status-dot ${
              backendStatus === 'ready'       ? 'header__status-dot--ready' :
              backendStatus === 'unavailable' ? 'header__status-dot--error' : ''
            }`}
          />
          <span>
            {backendStatus === 'ready'       ? 'Online' :
             backendStatus === 'unavailable' ? 'Offline' : 'Connecting…'}
          </span>
        </div>
      </header>

      {/* Offline banner */}
      {backendStatus === 'unavailable' && (
        <div className="backend-banner" role="alert">
          <AlertIcon />
          <span>
            Backend not reachable. Start the server with{' '}
            <code>uvicorn app.main:app --reload</code>
          </span>
        </div>
      )}

      {/* Message list */}
      <main className="messages" aria-label="Conversation" aria-live="polite">
        {messages.length === 0 && !isLoading ? (
          <EmptyState
            onChipClick={(text) => {
              setInput(text)
              textareaRef.current?.focus()
            }}
          />
        ) : (
          <>
            {messages.map((msg) => (
              <MessageBubble key={msg.id} msg={msg} />
            ))}
            {isLoading && <TypingIndicator />}
            {error && (
              <div className="error-message" role="alert" id="chat-error">
                <AlertIcon />
                <span>{error}</span>
              </div>
            )}
          </>
        )}
        <div ref={messagesEndRef} />
      </main>

      {/* Composer */}
      <footer className="composer">
        <div className="composer__inner">
          <label htmlFor="chat-input" className="sr-only">Type your message</label>
          <textarea
            id="chat-input"
            ref={textareaRef}
            className="composer__input"
            value={input}
            onChange={handleInputChange}
            onKeyDown={handleKeyDown}
            placeholder="Share what's on your mind…"
            rows={1}
            disabled={isLoading}
            aria-label="Message input"
            aria-describedby={error ? 'chat-error' : undefined}
          />
          <button
            className={`composer__btn${isLoading ? ' composer__btn--loading' : ''}`}
            onClick={() => submit(input)}
            disabled={!canSubmit}
            aria-label="Send message"
          >
            {isLoading ? <span className="spinner" aria-hidden="true" /> : <SendIcon />}
          </button>
        </div>
        {input.length > 0 && (
          <p className="composer__floating-label" aria-hidden="true">
            Share freely — this is a safe space
          </p>
        )}
        <p className="composer__hint">Enter to send · Shift+Enter for new line</p>
      </footer>
    </div>
  )
}

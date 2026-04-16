export type Role = 'user' | 'assistant'

export interface Message {
  role: Role
  content: string
}

export interface ChatRequest {
  messages: Message[]
}

export interface ChatResponse {
  raw_emotion: string
  emotion: string
  strategy: string
  response: string
}

export interface ChatError {
  detail: string
}

export interface DisplayMessage extends Message {
  id: string
  timestamp: Date
  emotion?: string
  strategy?: string
}

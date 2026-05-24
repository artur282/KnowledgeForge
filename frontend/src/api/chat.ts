import { apiRequest } from "../lib/api"
import type { ChatResponse, ChatHistoryResponse } from "../types"

export function sendMessage(question: string, sessionId?: string) {
  return apiRequest<ChatResponse>("/chat", {
    method: "POST",
    body: { question, session_id: sessionId || null },
  })
}

export function getChatHistory(sessionId: string) {
  return apiRequest<ChatHistoryResponse>(`/chat/${sessionId}/history`)
}

import { useState, useCallback, useRef } from "react"
import { sendMessage, getChatHistory } from "../api/chat"
import type { ChatMessage, SourceInfo } from "../types"

interface DisplayMessage {
  role: "user" | "assistant"
  content: string
  sources?: SourceInfo[]
}

export function useChat(sessionId?: string) {
  const [messages, setMessages] = useState<DisplayMessage[]>([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [currentSessionId, setCurrentSessionId] = useState<string | null>(sessionId || null)
  const sessionIdRef = useRef(sessionId || null)

  const loadHistory = useCallback(async (sid: string) => {
    setError(null)
    try {
      const history = await getChatHistory(sid)
      setMessages(history.messages.map((m: ChatMessage) => ({
        role: m.role as "user" | "assistant",
        content: m.content,
        sources: m.context_used,
      })))
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load history")
    }
  }, [])

  const handleSend = useCallback(async (question: string) => {
    if (!question.trim()) return
    setError(null)
    setMessages((prev) => [...prev, { role: "user", content: question }])
    setLoading(true)
    try {
      const response = await sendMessage(question, sessionIdRef.current || undefined)
      setCurrentSessionId(response.session_id)
      sessionIdRef.current = response.session_id
      setMessages((prev) => [...prev, {
        role: "assistant",
        content: response.answer,
        sources: response.sources,
      }])
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to send message")
      setMessages((prev) => [...prev, {
        role: "assistant",
        content: "[ERROR] Failed to get response. Please try again.",
      }])
    } finally {
      setLoading(false)
    }
  }, [])

  return { messages, loading, error, sessionId: currentSessionId, send: handleSend, loadHistory }
}

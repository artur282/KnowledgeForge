import { useEffect, useRef } from "react"
import { ChatBubble } from "./ChatBubble"
import type { SourceInfo } from "../../types"

interface Message {
  role: "user" | "assistant"
  content: string
  sources?: SourceInfo[]
}

interface ChatLogProps {
  messages: Message[]
  loading: boolean
}

export function ChatLog({ messages, loading }: ChatLogProps) {
  const bottomRef = useRef<HTMLDivElement>(null)

  useEffect(
    function scrollToBottom() {
      bottomRef.current?.scrollIntoView({ behavior: "smooth" })
    },
    [messages],
  )

  if (messages.length === 0 && !loading) {
    return (
      <div className="flex-1 flex items-center justify-center">
        <div className="text-center">
          <span className="font-body text-sm text-text-muted">
            // INIT_SESSION
          </span>
          <p className="font-body text-xs text-text-ghost mt-2">
            $ enter a question to begin
          </p>
        </div>
      </div>
    )
  }

  return (
    <div className="flex-1 overflow-y-auto space-y-4 p-4">
      {messages.map(function renderMessage(msg, i) {
        return (
          <ChatBubble
            key={i}
            role={msg.role}
            content={msg.content}
            sources={msg.sources}
          />
        )
      })}
      {loading && (
        <div className="flex items-start gap-3">
          <div className="bg-bg-surface border border-border-subtle rounded-md px-4 py-3">
            <span className="inline-block w-2 h-4 bg-accent-primary rounded-sm animate-cursor-blink" />
          </div>
        </div>
      )}
      <div ref={bottomRef} />
    </div>
  )
}

import { useMemo } from "react"
import type { SourceInfo } from "../../types"
import { SourceBadge } from "./SourceBadge"

interface ChatBubbleProps {
  role: "user" | "assistant"
  content: string
  sources?: SourceInfo[]
}

export function ChatBubble({ role, content, sources }: ChatBubbleProps) {
  const isUser = role === "user"
  const timestamp = useMemo(() => new Date().toLocaleTimeString("en-US", {
    hour12: false,
    hour: "2-digit",
    minute: "2-digit",
    second: "2-digit",
  }), [])

  return (
    <div className={`flex gap-3 ${isUser ? "justify-end" : "justify-start"}`}>
      <div className={`max-w-[80%] ${isUser ? "order-1" : ""}`}>
        <div className="flex items-center gap-2 mb-1">
          <span className="font-body text-2xs text-text-muted">[{timestamp}]</span>
          <span
            className={`font-body text-xs font-semibold ${isUser ? "text-accent-primary" : "text-info"}`}
          >
            {isUser ? "$ USER" : "> ASSISTANT"}
          </span>
        </div>
        <div
          className={`p-4 rounded-md font-body text-sm leading-relaxed ${
            isUser
              ? "bg-accent-bg border border-accent-dim/30 text-text-primary"
              : "bg-bg-surface border border-border-subtle text-text-primary"
          }`}
        >
          <p className="whitespace-pre-wrap">{content}</p>
        </div>
        {!isUser && sources && sources.length > 0 && (
          <div className="flex flex-wrap gap-1.5 mt-2">
            {sources.map(function renderSource(s, i) {
              return <SourceBadge key={i} source={s} />
            })}
          </div>
        )}
      </div>
    </div>
  )
}

import { useChat } from "../hooks/useChat"
import { PanelCard } from "../components/common/PanelCard"
import { ChatLog } from "../components/chat/ChatLog"
import { ChatInput } from "../components/chat/ChatInput"

export function Chat() {
  const { messages, loading, error, sessionId, send } = useChat()

  return (
    <div
      className="animate-reveal-up flex flex-col"
      style={{ height: "calc(100vh - 160px)" }}
    >
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h1 className="font-body text-lg font-bold text-accent-primary tracking-wider uppercase mb-1">
            <span className="text-text-muted">// </span>CHAT
          </h1>
          {sessionId && (
            <span className="font-body text-2xs text-text-muted">
              SESSION: {sessionId.slice(0, 8)}...
            </span>
          )}
        </div>
      </div>

      {error && (
        <div className="mb-4 px-4 py-2 bg-error/10 border border-error/20 rounded text-error text-xs font-body">
          [!] {error}
        </div>
      )}

      <PanelCard index="01" title="TERMINAL" className="flex flex-col flex-1">
        <ChatLog messages={messages} loading={loading} />
        <div className="border-t border-border-ghost pt-3">
          <ChatInput onSend={send} disabled={loading} />
        </div>
      </PanelCard>
    </div>
  )
}

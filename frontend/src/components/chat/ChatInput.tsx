import { useState } from "react"
import { Send } from "lucide-react"

interface ChatInputProps {
  onSend: (message: string) => void
  disabled?: boolean
}

export function ChatInput({ onSend, disabled }: ChatInputProps) {
  const [value, setValue] = useState("")

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    if (!value.trim() || disabled) return
    onSend(value.trim())
    setValue("")
  }

  return (
    <form
      onSubmit={handleSubmit}
      className="flex items-center gap-3 bg-bg-surface border border-border-default rounded-md px-4 py-3 focus-within:border-accent-primary focus-within:shadow-[0_0_0_3px_var(--color-accent-bg)] transition-all"
    >
      <span className="text-accent-primary font-body text-sm">$</span>
      <input
        type="text"
        value={value}
        onChange={function handleChange(e) {
          setValue(e.target.value)
        }}
        placeholder="type your question..."
        disabled={disabled}
        className="flex-1 bg-transparent border-none outline-none font-body text-sm text-text-primary placeholder:text-text-muted"
      />
      <button
        type="submit"
        disabled={!value.trim() || disabled}
        className="p-1.5 text-text-muted hover:text-accent-primary transition-colors disabled:opacity-30"
        aria-label="Send message"
      >
        <Send className="w-4 h-4" />
      </button>
    </form>
  )
}

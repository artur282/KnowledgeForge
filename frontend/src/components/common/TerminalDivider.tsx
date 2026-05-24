interface TerminalDividerProps {
  label?: string
}

export function TerminalDivider({ label }: TerminalDividerProps) {
  if (!label) {
    return (
      <div
        className="w-full h-px my-16"
        style={{
          background:
            "linear-gradient(90deg, transparent 0%, var(--color-border-default) 20%, var(--color-accent-dim) 50%, var(--color-border-default) 80%, transparent 100%)",
        }}
      />
    )
  }

  return (
    <div className="flex items-center gap-4 my-16">
      <div className="flex-1 h-px bg-gradient-to-r from-transparent to-border-default" />
      <span className="font-body text-2xs text-text-muted tracking-widest uppercase flex-shrink-0">
        {label}
      </span>
      <div className="flex-1 h-px bg-gradient-to-l from-transparent to-border-default" />
    </div>
  )
}

import type { ReactNode } from "react"

interface PanelCardProps {
  index: string
  title: string
  children: ReactNode
  className?: string
  controls?: ReactNode
}

export function PanelCard({
  index,
  title,
  children,
  className = "",
  controls,
}: PanelCardProps) {
  return (
    <div
      className={`bg-bg-surface border border-border-subtle rounded-md overflow-hidden hover:border-border-default transition-colors ${className}`}
    >
      <div className="flex items-center justify-between px-5 py-4 border-b border-border-ghost">
        <h2 className="font-body text-sm font-bold text-accent-primary tracking-wider uppercase">
          <span className="text-text-muted font-normal mr-2">[{index}]</span>
          {title}
        </h2>
        {controls && (
          <div className="flex items-center gap-1">{controls}</div>
        )}
      </div>
      <div className="p-5">{children}</div>
    </div>
  )
}

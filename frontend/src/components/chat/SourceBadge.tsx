import type { SourceInfo } from "../../types"

interface SourceBadgeProps {
  source: SourceInfo
}

export function SourceBadge({ source }: SourceBadgeProps) {
  const shortId = source.doc_id.slice(0, 8)

  return (
    <span className="inline-flex items-center gap-1.5 px-2 py-0.5 bg-bg-surface-hover border border-border-subtle rounded-sm text-2xs font-body text-text-muted">
      <span className="text-accent-dim">doc:</span>
      {shortId}
      <span className="text-text-ghost">|</span>
      <span className="text-accent-dim">ch:</span>
      {source.chunk_index}
      <span className="text-text-ghost">|</span>
      <span className="text-accent-primary">
        {(source.score * 100).toFixed(0)}%
      </span>
    </span>
  )
}

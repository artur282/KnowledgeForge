import type { SearchResult } from "../../types"

interface ResultCardProps {
  result: SearchResult
}

export function ResultCard({ result }: ResultCardProps) {
  const scorePct = (result.score * 100).toFixed(1)

  return (
    <div className="bg-bg-surface border border-border-subtle rounded-md p-4 hover:border-border-default transition-colors">
      <div className="flex items-center justify-between mb-2">
        <div className="flex items-center gap-2">
          <span className="font-body text-xs text-accent-primary font-semibold tracking-wider">
            {result.filename}
          </span>
          <span className="font-body text-2xs text-text-muted">
            [CHUNK_{result.chunk_index}]
          </span>
        </div>
        <span className="font-body text-xs text-text-secondary tabular-nums">
          <span className="text-text-muted">MATCH: </span>
          <span
            className={
              Number(scorePct) > 80
                ? "text-success"
                : Number(scorePct) > 50
                  ? "text-warning"
                  : "text-text-secondary"
            }
          >
            {scorePct}%
          </span>
        </span>
      </div>
      <p className="font-body text-sm text-text-secondary leading-relaxed line-clamp-3">
        {result.content}
      </p>
    </div>
  )
}

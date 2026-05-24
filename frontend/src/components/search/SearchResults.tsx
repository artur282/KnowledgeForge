import { ResultCard } from "./ResultCard"
import type { SearchResult } from "../../types"

interface SearchResultsProps {
  results: SearchResult[]
  loading: boolean
}

export function SearchResults({ results, loading }: SearchResultsProps) {
  if (loading) {
    return (
      <div className="space-y-3">
        {[1, 2, 3].map(function renderSkeleton(i) {
          return (
            <div
              key={i}
              className="bg-bg-surface border border-border-subtle rounded-md p-4 animate-pulse"
            >
              <div className="h-3 w-32 bg-bg-surface-hover rounded mb-2" />
              <div className="h-4 w-full bg-bg-surface-hover rounded" />
            </div>
          )
        })}
      </div>
    )
  }

  if (results.length === 0) {
    return (
      <div className="text-center py-16">
        <span className="font-body text-sm text-text-muted">
          // ENTER_QUERY_TO_SEARCH
        </span>
      </div>
    )
  }

  return (
    <div className="space-y-3">
      <div className="flex items-center gap-2 mb-2">
        <span className="font-body text-xs text-text-muted">
          &gt; {results.length} result{results.length !== 1 ? "s" : ""} found
        </span>
      </div>
      {results.map(function renderResult(result) {
        return (
          <ResultCard
            key={`${result.doc_id}-${result.chunk_index}`}
            result={result}
          />
        )
      })}
    </div>
  )
}

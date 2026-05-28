import { useEffect } from "react"
import { useSearch } from "../hooks/useSearch"
import { PanelCard } from "../components/common/PanelCard"
import { SearchBar } from "../components/search/SearchBar"
import { SearchResults } from "../components/search/SearchResults"

export function Search() {
  const { query, setQuery, debouncedQuery, results, suggestions, setSuggestions, loading, error, search, fetchSuggestions } = useSearch()

  useEffect(function fetchSuggestionsOnDebounce() {
    if (debouncedQuery.length >= 2) {
      fetchSuggestions(debouncedQuery)
    } else {
      setSuggestions([])
    }
  }, [debouncedQuery, fetchSuggestions])

  return (
    <div className="animate-reveal-up">
      <div className="mb-6">
        <h1 className="font-body text-lg font-bold text-accent-primary tracking-wider uppercase mb-2">
          <span className="text-text-muted">// </span>HYBRID_SEARCH
        </h1>
        <span className="font-body text-2xs text-text-ghost tracking-wider">
          pgvector + BM25 + RRF_K=60
        </span>
      </div>
      <PanelCard index="01" title="QUERY">
        <SearchBar value={query} onChange={setQuery} onSearch={search} suggestions={suggestions} loading={loading} />
      </PanelCard>
      {error && (
        <div className="mt-4 px-4 py-2 bg-error/10 border border-error/20 rounded text-error text-xs font-body">
          [!] {error}
        </div>
      )}
      <div className="mt-6">
        <SearchResults results={results} loading={loading} />
      </div>
    </div>
  )
}

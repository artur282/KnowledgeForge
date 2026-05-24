import { useSearch } from "../hooks/useSearch"
import { PanelCard } from "../components/common/PanelCard"
import { SearchBar } from "../components/search/SearchBar"
import { SearchResults } from "../components/search/SearchResults"

export function Search() {
  const { query, setQuery, results, suggestions, loading, search, fetchSuggestions } = useSearch()

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
        <SearchBar
          value={query}
          onChange={function handleQueryChange(value: string) {
            setQuery(value)
            fetchSuggestions(value)
          }}
          onSearch={search}
          suggestions={suggestions}
          loading={loading}
        />
      </PanelCard>

      <div className="mt-6">
        <SearchResults results={results} loading={loading} />
      </div>
    </div>
  )
}

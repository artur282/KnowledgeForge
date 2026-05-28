import { useState, useCallback } from "react"
import { search, getSuggestions } from "../api/search"
import { useDebounce } from "./useDebounce"
import type { SearchResult } from "../types"

export function useSearch() {
  const [query, setQuery] = useState("")
  const [results, setResults] = useState<SearchResult[]>([])
  const [suggestions, setSuggestions] = useState<string[]>([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const debouncedQuery = useDebounce(query, 300)

  const handleSearch = useCallback(async (q: string, k: number = 5) => {
    setError(null)
    setLoading(true)
    try {
      const response = await search(q, k)
      setResults(response.results)
    } catch (err) {
      setError(err instanceof Error ? err.message : "Search failed")
      setResults([])
    } finally {
      setLoading(false)
    }
  }, [])

  const fetchSuggestions = useCallback(async (q: string) => {
    if (q.length < 2) { setSuggestions([]); return }
    try {
      const response = await getSuggestions(q)
      setSuggestions(response.suggestions)
    } catch {
      setSuggestions([])
    }
  }, [])

  return { query, setQuery, debouncedQuery, results, suggestions, setSuggestions, loading, error, search: handleSearch, fetchSuggestions }
}

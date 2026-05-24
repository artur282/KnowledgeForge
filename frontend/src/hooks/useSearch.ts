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

  const debouncedQuery = useDebounce(query, 150)

  const handleSearch = useCallback(async (q: string, k: number = 5) => {
    setError(null)
    setLoading(true)
    const response = await search(q, k)
    setResults(response.results)
    setLoading(false)
  }, [])

  const fetchSuggestions = useCallback(async (q: string) => {
    if (q.length < 2) {
      setSuggestions([])
      return
    }
    const response = await getSuggestions(q)
    setSuggestions(response.suggestions)
  }, [])

  return {
    query,
    setQuery,
    debouncedQuery,
    results,
    suggestions,
    loading,
    error,
    search: handleSearch,
    fetchSuggestions,
  }
}

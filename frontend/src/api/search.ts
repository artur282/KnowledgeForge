import { apiRequest } from "../lib/api"
import type { SearchResponse, SuggestResponse } from "../types"

export function search(query: string, k: number = 5) {
  return apiRequest<SearchResponse>("/search", {
    method: "POST",
    body: { query, k },
  })
}

export function getSuggestions(q: string) {
  return apiRequest<SuggestResponse>("/search/suggest", {
    params: { q },
  })
}

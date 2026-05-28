export interface DocumentResponse {
  id: string
  filename: string
  content_hash?: string
  status: "pending" | "processing" | "ready" | "error"
  uploaded_at: string
}

export interface DocumentUploadResponse {
  status: string
  document_id: string | null
}

export interface DocumentListResponse {
  documents: DocumentResponse[]
  total: number
}

export interface SearchResult {
  doc_id: string
  chunk_index: number
  content: string
  score: number
  filename: string
  metadata: Record<string, unknown>
}

export interface SearchResponse {
  results: SearchResult[]
  total: number
}

export interface SuggestResponse {
  suggestions: string[]
}

export interface SourceInfo {
  doc_id: string
  chunk_index: number
  score: number
}

export interface ChatResponse {
  answer: string
  sources: SourceInfo[]
  session_id: string
}

export interface ChatMessage {
  id: string
  session_id: string
  role: "user" | "assistant"
  content: string
  context_used: SourceInfo[]
  created_at: string
}

export interface ChatHistoryResponse {
  session_id: string
  messages: ChatMessage[]
}

export interface McpTool {
  name: string
  description: string
  parameters: unknown
}

export interface EvalRunRequest {
  name: string
  dataset_path?: string
}

export interface EvalRunResponse {
  report_id: string
  name: string
  faithfulness: number | null
  answer_relevancy: number | null
  context_precision: number | null
  context_recall: number | null
  created_at: string
}

export interface EvalReportItem {
  id: string
  name: string
  faithfulness: number | null
  answer_relevancy: number | null
  context_precision: number | null
  created_at: string
}

export interface EvalReportsResponse {
  reports: EvalReportItem[]
}

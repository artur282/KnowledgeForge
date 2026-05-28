import { apiRequest } from "../lib/api"
import type { DocumentResponse, DocumentUploadResponse, DocumentListResponse } from "../types"

export function uploadDocument(file: File) {
  const formData = new FormData()
  formData.append("file", file)
  return apiRequest<DocumentUploadResponse>("/documents", {
    method: "POST",
    body: formData,
  })
}

export function getDocument(id: string) {
  return apiRequest<DocumentResponse>(`/documents/${id}`)
}

export function deleteDocument(id: string) {
  return apiRequest<void>(`/documents/${id}`, { method: "DELETE" })
}

export function listDocuments() {
  return apiRequest<DocumentListResponse>("/documents")
}

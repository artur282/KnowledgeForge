import { useState, useCallback } from "react"
import { uploadDocument, getDocument, deleteDocument } from "../api/documents"
import type { DocumentResponse } from "../types"

export function useDocuments() {
  const [documents, setDocuments] = useState<DocumentResponse[]>([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const pendingDocs = documents.filter(
    (d) => d.status === "pending" || d.status === "processing",
  )
  const readyDocs = documents.filter((d) => d.status === "ready")
  const errorDocs = documents.filter((d) => d.status === "error")

  const handleUpload = useCallback(async (file: File) => {
    setError(null)
    setLoading(true)
    const result = await uploadDocument(file)
    if (result.document_id) {
      const doc = await getDocument(result.document_id)
      setDocuments((prev) => [doc, ...prev])
    }
    setLoading(false)
  }, [])

  const handleDelete = useCallback(async (id: string) => {
    setError(null)
    await deleteDocument(id)
    setDocuments((prev) => prev.filter((d) => d.id !== id))
  }, [])

  return {
    documents,
    pendingDocs,
    readyDocs,
    errorDocs,
    loading,
    error,
    upload: handleUpload,
    delete: handleDelete,
  }
}

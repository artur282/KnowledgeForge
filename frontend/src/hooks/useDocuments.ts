import { useState, useCallback, useEffect } from "react"
import { uploadDocument, getDocument, deleteDocument, listDocuments } from "../api/documents"
import type { DocumentResponse } from "../types"

export function useDocuments() {
  const [documents, setDocuments] = useState<DocumentResponse[]>([])
  const [loading, setLoading] = useState(false)
  const [fetching, setFetching] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const pendingDocs = documents.filter((d) => d.status === "pending" || d.status === "processing")
  const readyDocs = documents.filter((d) => d.status === "ready")
  const errorDocs = documents.filter((d) => d.status === "error")

  useEffect(function fetchDocuments() {
    listDocuments()
      .then((res) => setDocuments(res.documents))
      .catch((err) => setError(err instanceof Error ? err.message : "Failed to load documents"))
      .finally(() => setFetching(false))
  }, [])

  const handleUpload = useCallback(async (file: File) => {
    setError(null)
    setLoading(true)
    try {
      const result = await uploadDocument(file)
      if (result.document_id) {
        const doc = await getDocument(result.document_id)
        setDocuments((prev) => [doc, ...prev])
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : "Upload failed")
      throw err
    } finally {
      setLoading(false)
    }
  }, [])

  const handleDelete = useCallback(async (id: string) => {
    setError(null)
    try {
      await deleteDocument(id)
      setDocuments((prev) => prev.filter((d) => d.id !== id))
    } catch (err) {
      setError(err instanceof Error ? err.message : "Delete failed")
      throw err
    }
  }, [])

  return { documents, pendingDocs, readyDocs, errorDocs, loading, fetching, error, upload: handleUpload, delete: handleDelete }
}

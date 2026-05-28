import { Trash2 } from "lucide-react"
import { StatusBadge } from "../common/StatusBadge"
import type { DocumentResponse } from "../../types"

interface DocumentTableProps {
  documents: DocumentResponse[]
  onDelete: (id: string) => void
  loading?: boolean
}

export function DocumentTable({ documents, onDelete, loading }: DocumentTableProps) {
  if (loading) {
    return (
      <div className="overflow-x-auto">
        <table className="w-full border-collapse font-body text-sm">
          <thead>
            <tr>
              <th className="px-4 py-3 text-left text-text-muted text-xs font-medium tracking-widest uppercase border-b border-border-default">
                FILENAME
              </th>
              <th className="px-4 py-3 text-left text-text-muted text-xs font-medium tracking-widest uppercase border-b border-border-default">
                STATUS
              </th>
              <th className="px-4 py-3 text-left text-text-muted text-xs font-medium tracking-widest uppercase border-b border-border-default">
                HASH
              </th>
              <th className="px-4 py-3 text-right text-text-muted text-xs font-medium tracking-widest uppercase border-b border-border-default">
                ACTIONS
              </th>
            </tr>
          </thead>
          <tbody>
            {[1, 2, 3].map((i) => (
              <tr key={i} className="border-b border-border-ghost">
                <td className="px-4 py-3"><div className="h-4 w-40 bg-bg-surface-hover rounded animate-pulse" /></td>
                <td className="px-4 py-3"><div className="h-4 w-16 bg-bg-surface-hover rounded animate-pulse" /></td>
                <td className="px-4 py-3"><div className="h-4 w-24 bg-bg-surface-hover rounded animate-pulse" /></td>
                <td className="px-4 py-3 text-right"><div className="h-4 w-8 bg-bg-surface-hover rounded animate-pulse ml-auto" /></td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    )
  }

  if (documents.length === 0) {
    return (
      <div className="text-center py-12">
        <span className="font-body text-sm text-text-muted">
          // NO_DOCUMENTS_FOUND
        </span>
      </div>
    )
  }

  return (
    <div className="overflow-x-auto">
      <table className="w-full border-collapse font-body text-sm">
        <thead>
          <tr>
            <th className="px-4 py-3 text-left text-text-muted text-xs font-medium tracking-widest uppercase border-b border-border-default">
              FILENAME
            </th>
            <th className="px-4 py-3 text-left text-text-muted text-xs font-medium tracking-widest uppercase border-b border-border-default">
              STATUS
            </th>
            <th className="px-4 py-3 text-left text-text-muted text-xs font-medium tracking-widest uppercase border-b border-border-default">
              HASH
            </th>
            <th className="px-4 py-3 text-right text-text-muted text-xs font-medium tracking-widest uppercase border-b border-border-default">
              ACTIONS
            </th>
          </tr>
        </thead>
        <tbody>
          {documents.map(function renderDocRow(doc) {
            return (
              <tr
                key={doc.id}
                className="border-b border-border-ghost hover:bg-bg-surface-hover transition-colors"
              >
                <td className="px-4 py-3 text-text-primary tabular-nums">
                  {doc.filename}
                </td>
                <td className="px-4 py-3">
                  <StatusBadge
                    status={
                      doc.status as
                        | "pending"
                        | "processing"
                        | "ready"
                        | "error"
                    }
                  />
                </td>
                <td className="px-4 py-3 text-text-muted text-xs font-mono">
                  {(doc.content_hash || "—").slice(0, 12)}...
                </td>
                <td className="px-4 py-3 text-right">
                  <button
                    onClick={function handleDelete() {
                      onDelete(doc.id)
                    }}
                    className="p-1.5 text-text-muted hover:text-error transition-colors rounded hover:bg-error/10"
                    aria-label="Delete document"
                  >
                    <Trash2 className="w-4 h-4" />
                  </button>
                </td>
              </tr>
            )
          })}
        </tbody>
      </table>
    </div>
  )
}

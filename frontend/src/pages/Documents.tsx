import { useDocuments } from "../hooks/useDocuments"
import { PanelCard } from "../components/common/PanelCard"
import { FileUpload } from "../components/common/FileUpload"
import { TerminalDivider } from "../components/common/TerminalDivider"
import { DocumentTable } from "../components/documents/DocumentTable"
import { toast } from "sonner"

export function Documents() {
  const { documents, loading, fetching, error, upload, delete: deleteDoc } = useDocuments()

  async function handleUpload(file: File) {
    try {
      await upload(file)
      toast.success(`[$ UPLOAD_OK] ${file.name}`)
    } catch {
      toast.error(`[! UPLOAD_FAILED] ${file.name}`)
    }
  }

  async function handleDelete(id: string) {
    try {
      await deleteDoc(id)
      toast.success("[$ DELETE_OK] Document removed")
    } catch {
      toast.error("[! DELETE_FAILED]")
    }
  }

  return (
    <div className="animate-reveal-up">
      <div className="mb-6">
        <h1 className="font-body text-lg font-bold text-accent-primary tracking-wider uppercase mb-2">
          <span className="text-text-muted">// </span>DOCUMENTS
        </h1>
        <span className="font-body text-2xs text-text-ghost tracking-wider">
          &lt; REF:0x4F2A &gt;
        </span>
      </div>

      <PanelCard index="01" title="UPLOAD">
        <FileUpload onUpload={handleUpload} disabled={loading} />
      </PanelCard>

      <TerminalDivider label="INDEX" />

      <PanelCard index="02" title="REPOSITORY">
        {error && (
          <div className="mb-4 px-4 py-2 bg-error/10 border border-error/20 rounded text-error text-xs font-body">
            [!] {error}
          </div>
        )}
        <DocumentTable documents={documents} onDelete={handleDelete} loading={fetching} />
      </PanelCard>
    </div>
  )
}

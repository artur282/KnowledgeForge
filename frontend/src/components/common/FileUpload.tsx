import { useCallback, useState } from "react"
import { Upload } from "lucide-react"

const ACCEPTED_TYPES = [
  "application/pdf",
  "text/plain",
  "text/markdown",
  "text/csv",
  "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
]
const MAX_SIZE_MB = 50

function validateFile(file: File): string | null {
  if (ACCEPTED_TYPES.length > 0 && !ACCEPTED_TYPES.includes(file.type)) {
    return `Unsupported file type: ${file.type || "unknown"}`
  }
  if (file.size > MAX_SIZE_MB * 1024 * 1024) {
    return `File too large: ${(file.size / 1024 / 1024).toFixed(1)}MB (max ${MAX_SIZE_MB}MB)`
  }
  return null
}

interface FileUploadProps {
  onUpload: (file: File) => Promise<void>
  disabled?: boolean
}

export function FileUpload({ onUpload, disabled }: FileUploadProps) {
  const [dragging, setDragging] = useState(false)
  const [validationError, setValidationError] = useState<string | null>(null)

  const handleDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault()
    setDragging(true)
  }, [])

  const handleDragLeave = useCallback((e: React.DragEvent) => {
    e.preventDefault()
    setDragging(false)
  }, [])

  const handleDrop = useCallback(
    (e: React.DragEvent) => {
      e.preventDefault()
      setDragging(false)
      const file = e.dataTransfer.files[0]
      if (file) {
        const error = validateFile(file)
        if (error) {
          setValidationError(error)
          return
        }
        setValidationError(null)
        onUpload(file)
      }
    },
    [onUpload],
  )

  function handleChange(e: React.ChangeEvent<HTMLInputElement>) {
    const file = e.target.files?.[0]
    if (file) {
      const error = validateFile(file)
      if (error) {
        setValidationError(error)
        return
      }
      setValidationError(null)
      onUpload(file)
    }
  }

  return (
    <label
      onDragOver={handleDragOver}
      onDragLeave={handleDragLeave}
      onDrop={handleDrop}
      className={`flex flex-col items-center justify-center gap-3 p-10 border-2 border-dashed rounded-lg cursor-pointer transition-all duration-150 ${
        dragging
          ? "border-accent-primary bg-accent-bg"
          : "border-border-default hover:border-accent-dim hover:bg-bg-surface-hover"
      } ${disabled ? "opacity-50 pointer-events-none" : ""}`}
    >
      <Upload
        className={`w-8 h-8 ${dragging ? "text-accent-primary" : "text-text-muted"}`}
      />
      <span className="font-body text-sm text-text-muted tracking-wide">
        $ DROP_FILE_HERE{" "}
        <span className="text-text-ghost">// or click to browse</span>
      </span>
      <input
        type="file"
        className="hidden"
        onChange={handleChange}
        disabled={disabled}
      />
      {validationError && (
        <span className="font-body text-xs text-error mt-1">
          {validationError}
        </span>
      )}
    </label>
  )
}

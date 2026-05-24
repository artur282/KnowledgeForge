import { useCallback, useState } from "react"
import { Upload } from "lucide-react"

interface FileUploadProps {
  onUpload: (file: File) => Promise<void>
  disabled?: boolean
}

export function FileUpload({ onUpload, disabled }: FileUploadProps) {
  const [dragging, setDragging] = useState(false)

  function handleDrag(over: boolean) {
    return (e: React.DragEvent) => {
      e.preventDefault()
      setDragging(over)
    }
  }

  const handleDrop = useCallback(
    (e: React.DragEvent) => {
      e.preventDefault()
      setDragging(false)
      const file = e.dataTransfer.files[0]
      if (file) onUpload(file)
    },
    [onUpload],
  )

  function handleChange(e: React.ChangeEvent<HTMLInputElement>) {
    const file = e.target.files?.[0]
    if (file) onUpload(file)
  }

  return (
    <label
      onDragOver={handleDrag(true)}
      onDragLeave={handleDrag(false)}
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
    </label>
  )
}

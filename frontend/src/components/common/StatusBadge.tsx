import { cn } from "../../lib/utils"

type Status = "pending" | "processing" | "ready" | "error"

const STATUS_STYLES: Record<Status, string> = {
  pending: "bg-transparent text-text-muted border-border-default",
  processing:
    "bg-warning/10 text-warning border-warning/20 animate-glow-pulse",
  ready: "bg-success/10 text-success border-success/20",
  error: "bg-error/10 text-error border-error/20",
}

interface StatusBadgeProps {
  status: Status
  className?: string
}

export function StatusBadge({ status, className }: StatusBadgeProps) {
  return (
    <span
      className={cn(
        "inline-flex items-center gap-1.5 font-body text-2xs font-medium tracking-widest uppercase px-2 py-0.5 rounded-sm border",
        STATUS_STYLES[status],
        className,
      )}
    >
      <span
        className={cn("w-1.5 h-1.5 rounded-full", {
          "bg-text-muted": status === "pending",
          "bg-warning": status === "processing",
          "bg-success": status === "ready",
          "bg-error": status === "error",
        })}
      />
      {status}
    </span>
  )
}

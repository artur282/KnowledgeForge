import { NavLink, useLocation } from "react-router-dom"
import { Diamond } from "lucide-react"

const ROUTE_LABELS: Record<string, string> = {
  "/documents": "DOCUMENTS",
  "/search": "SEARCH",
  "/chat": "CHAT",
  "/mcp": "MCP",
  "/eval": "EVALUATION",
}

export function Navbar() {
  const location = useLocation()
  const pathSegments = location.pathname.split("/").filter(Boolean)
  const currentLabel = ROUTE_LABELS[location.pathname] || "TERMINAL"

  return (
    <nav className="flex items-center justify-between px-6 py-3 bg-bg-primary/85 backdrop-blur-xl border-b border-border-ghost sticky top-0 z-50">
      <div className="flex items-center gap-4">
        <NavLink to="/" className="flex items-center gap-2 no-underline">
          <Diamond className="w-5 h-5 text-accent-primary drop-shadow-[0_0_8px_var(--color-accent-bg)]" />
          <span className="font-display font-bold text-sm text-text-bright tracking-wider">
            KNOWLEDGEFORGE
          </span>
          <span className="text-2xs text-text-muted border border-border-subtle rounded-sm px-1.5 py-px">
            v0.1
          </span>
        </NavLink>
        <span className="text-text-muted text-xs">~</span>
        {pathSegments.length > 0 ? (
          <span className="flex items-center gap-1 text-xs font-body">
            <span className="text-text-muted">/</span>
            <span className="text-accent-primary italic font-semibold">
              {currentLabel.toLowerCase()}
            </span>
          </span>
        ) : (
          <span className="text-xs text-text-muted">/index</span>
        )}
      </div>
      <div className="flex items-center gap-4">
        <div className="flex items-center gap-2">
          <span className="inline-block w-2 h-2 rounded-full bg-success shadow-[0_0_8px_rgba(57,255,20,0.5)] animate-status-pulse" />
          <span className="text-xs text-text-secondary tracking-wider">
            SYS:ONLINE
          </span>
        </div>
      </div>
    </nav>
  )
}

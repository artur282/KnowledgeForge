import { useState, useEffect } from "react"
import { listMcpTools } from "../api/mcp"
import { PanelCard } from "../components/common/PanelCard"
import type { McpTool } from "../types"

export function Mcp() {
  const [tools, setTools] = useState<McpTool[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(
    function loadTools() {
      listMcpTools()
        .then(function handleSuccess(toolsList) {
          setTools(toolsList)
        })
        .catch(function handleError(err) {
          setError(err instanceof Error ? err.message : "Failed to load MCP tools")
        })
        .finally(function handleFinally() {
          setLoading(false)
        })
    },
    [],
  )

  return (
    <div className="animate-reveal-up">
      <div className="mb-6">
        <h1 className="font-body text-lg font-bold text-accent-primary tracking-wider uppercase mb-2">
          <span className="text-text-muted">// </span>MCP_TOOLS
        </h1>
        <span className="font-body text-2xs text-text-ghost tracking-wider">
          Model Context Protocol -- registered server tools
        </span>
      </div>

      {error && (
        <div className="mb-4 px-4 py-2 bg-error/10 border border-error/20 rounded text-error text-xs font-body">
          [!] {error}
        </div>
      )}

      <PanelCard index="01" title="REGISTERED_TOOLS">
        {loading ? (
          <div className="space-y-3">
            {[1, 2].map(function renderSkeleton(i) {
              return (
                <div
                  key={i}
                  className="p-4 border border-border-subtle rounded-md animate-pulse"
                >
                  <div className="h-3 w-32 bg-bg-surface-hover rounded mb-2" />
                  <div className="h-4 w-full bg-bg-surface-hover rounded" />
                </div>
              )
            })}
          </div>
        ) : tools.length === 0 ? (
          <p className="font-body text-sm text-text-muted">
            // NO_TOOLS_REGISTERED
          </p>
        ) : (
          <div className="grid gap-3">
            {tools.map(function renderTool(tool) {
              return (
                <div
                  key={tool.name}
                  className="p-4 bg-bg-surface-raised border border-border-subtle rounded-md hover:border-accent-dim transition-colors"
                >
                  <h3 className="font-body text-sm font-semibold text-accent-primary mb-1">
                    <span className="text-text-muted mr-2">[TOOL]</span>
                    {tool.name}
                  </h3>
                  <p className="font-body text-xs text-text-secondary">
                    {tool.description}
                  </p>
                </div>
              )
            })}
          </div>
        )}
      </PanelCard>
    </div>
  )
}

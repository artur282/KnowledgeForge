import { apiRequest } from "../lib/api"
import type { McpTool } from "../types"

export function listMcpTools() {
  return apiRequest<McpTool[]>("/mcp/tools")
}

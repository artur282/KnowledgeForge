import { NavLink } from "react-router-dom"
import {
  FileText,
  Search,
  MessageSquare,
  Wrench,
  BarChart3,
} from "lucide-react"

const NAV_ITEMS = [
  { to: "/documents", label: "DOCUMENTS", icon: FileText, index: "01" },
  { to: "/search", label: "SEARCH", icon: Search, index: "02" },
  { to: "/chat", label: "CHAT", icon: MessageSquare, index: "03" },
  { to: "/mcp", label: "MCP_TOOLS", icon: Wrench, index: "04" },
  { to: "/eval", label: "EVALUATION", icon: BarChart3, index: "05" },
]

export function Sidebar() {
  return (
    <aside className="w-[240px] flex-shrink-0 bg-bg-surface border-r border-border-ghost flex flex-col py-6">
      <div className="px-4 mb-6">
        <span className="text-2xs text-text-ghost tracking-widest uppercase">
          // CORE MODULES
        </span>
      </div>
      <nav className="flex flex-col gap-1 px-3">
        {NAV_ITEMS.map((item) => {
          const Icon = item.icon
          return (
            <NavLink
              key={item.to}
              to={item.to}
              className={({ isActive }) =>
                `flex items-center gap-3 px-3 py-2.5 rounded-md text-sm font-body transition-all duration-150 ${
                  isActive
                    ? "bg-accent-bg text-accent-primary italic font-semibold border-l-2 border-accent-primary"
                    : "text-text-muted hover:text-text-primary hover:bg-bg-surface-hover border-l-2 border-transparent"
                }`
              }
            >
              <span className="text-xs text-text-ghost font-normal w-6 tabular-nums">
                [{item.index}]
              </span>
              <Icon className="w-4 h-4 flex-shrink-0" />
              <span className="text-xs tracking-wider">{item.label}</span>
            </NavLink>
          )
        })}
      </nav>
    </aside>
  )
}

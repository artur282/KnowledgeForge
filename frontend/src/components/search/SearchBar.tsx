import { Search as SearchIcon } from "lucide-react"

interface SearchBarProps {
  value: string
  onChange: (value: string) => void
  onSearch: (query: string) => void
  suggestions: string[]
  loading?: boolean
}

export function SearchBar({ value, onChange, onSearch, suggestions, loading }: SearchBarProps) {
  function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    if (value.trim()) onSearch(value)
  }

  return (
    <div className="relative">
      <form onSubmit={handleSubmit} className="flex items-center gap-3 bg-bg-surface border border-border-default rounded-md px-4 py-3 focus-within:border-accent-primary focus-within:shadow-[0_0_0_3px_var(--color-accent-bg)] transition-all">
        <span className="text-accent-primary font-body text-sm">$</span>
        <input
          type="text"
          value={value}
          onChange={(e) => onChange(e.target.value)}
          placeholder="enter search query..."
          className="flex-1 bg-transparent border-none outline-none font-body text-sm text-text-primary placeholder:text-text-muted"
        />
        <button
          type="submit"
          disabled={!value.trim() || loading}
          className="p-1.5 text-text-muted hover:text-accent-primary transition-colors disabled:opacity-30"
          aria-label="Search"
        >
          <SearchIcon className="w-4 h-4" />
        </button>
      </form>
      {suggestions.length > 0 && (
        <div className="absolute top-full left-0 right-0 mt-1 bg-bg-surface-raised border border-border-subtle rounded-md overflow-hidden z-10">
          {suggestions.map((s, i) => (
            <button
              key={i}
              onClick={() => { onChange(s); onSearch(s) }}
              className="block w-full text-left px-4 py-2 text-xs font-body text-text-secondary hover:bg-bg-surface-hover hover:text-text-primary transition-colors"
            >
              {s}
            </button>
          ))}
        </div>
      )}
    </div>
  )
}

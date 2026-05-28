import { Outlet, useLocation } from "react-router-dom"
import { ErrorBoundary, type FallbackProps } from "react-error-boundary"
import { Navbar } from "./Navbar"
import { Sidebar } from "./Sidebar"
import { Footer } from "./Footer"

function ErrorFallback({ error }: FallbackProps) {
  return (
    <div className="p-6 text-center">
      <h2 className="font-body text-lg text-error mb-2">[! SYSTEM_ERROR]</h2>
      <pre className="font-body text-xs text-text-muted">{error instanceof Error ? error.message : String(error)}</pre>
      <button
        onClick={() => window.location.reload()}
        className="mt-4 px-4 py-2 bg-accent-primary text-bg-primary rounded text-sm"
      >
        $ RELOAD
      </button>
    </div>
  )
}

export function Layout() {
  const location = useLocation()

  return (
    <div className="flex flex-col min-h-screen">
      <Navbar />
      <div className="flex flex-1">
        <Sidebar />
        <main className="flex-1 p-8 overflow-auto">
          <ErrorBoundary FallbackComponent={ErrorFallback} resetKeys={[location.pathname]}>
            <Outlet />
          </ErrorBoundary>
        </main>
      </div>
      <Footer />
    </div>
  )
}

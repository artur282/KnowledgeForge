import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom"
import { Toaster } from "./components/ui/sonner"
import { Layout } from "./components/layout/Layout"
import { Documents } from "./pages/Documents"
import { Search } from "./pages/Search"
import { Chat } from "./pages/Chat"
import { Mcp } from "./pages/Mcp"
import { Eval } from "./pages/Eval"

export function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route element={<Layout />}>
          <Route index element={<Navigate to="/documents" replace />} />
          <Route path="/documents" element={<Documents />} />
          <Route path="/search" element={<Search />} />
          <Route path="/chat" element={<Chat />} />
          <Route path="/mcp" element={<Mcp />} />
          <Route path="/eval" element={<Eval />} />
        </Route>
      </Routes>
      <Toaster
        position="bottom-right"
        toastOptions={{
          className:
            "font-body text-xs bg-bg-surface-raised border border-border-default text-text-primary",
        }}
      />
    </BrowserRouter>
  )
}

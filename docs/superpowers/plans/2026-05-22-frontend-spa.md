# KnowledgeForge Frontend SPA -- Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a React SPA with Terminal/Cyberpunk aesthetic that exposes all KnowledgeForge backend functionality through 5 pages (Documents, Search, Chat, MCP, Eval).

**Architecture:** Vite + React 18 + TypeScript + Tailwind CSS v4.1 + shadcn/ui. Pages connect to `http://localhost:8000` REST API via typed fetch modules. State managed through custom hooks with functional setState patterns. No auth.

**Tech Stack:** React 18, Vite 6, TypeScript 5, Tailwind CSS 4, shadcn/ui, react-hook-form, zod, sonner, @tanstack/react-table, lucide-react, react-router-dom

---

## File Structure

```
frontend/
  package.json
  vite.config.ts
  tsconfig.json
  tsconfig.app.json
  tsconfig.node.json
  index.html
  src/
    main.tsx                       # ReactDOM render + Router
    App.tsx                        # Route definitions
    index.css                      # Tailwind + cyberpunk tokens + textures + animations
    lib/
      api.ts                       # Base HTTP client (fetch wrapper)
      cn.ts                        # clsx + tailwind-merge utility
    types/
      index.ts                     # All TypeScript interfaces
    api/
      documents.ts                 # POST/GET/DELETE /documents
      search.ts                    # POST /search, GET /search/suggest
      chat.ts                      # POST /chat, GET /chat/{id}/history
      mcp.ts                       # GET /mcp/tools
      eval.ts                      # POST /eval/run, GET /eval/reports
    hooks/
      useDocuments.ts              # Document list + upload + delete
      useSearch.ts                 # Search query + results + suggestions
      useChat.ts                   # Chat messages + send + session mgmt
      useDebounce.ts               # Generic debounce hook
    components/
      layout/
        Layout.tsx                 # Main wrapper: Navbar + Sidebar + content + Footer
        Navbar.tsx                 # Filesystem breadcrumb + status dot + brand
        Sidebar.tsx                # [NN] PAGE navigation, active highlight
        Footer.tsx                 # System metadata footer
      common/
        PanelCard.tsx              # [01] TITLE card with window dots + corner brackets
        StatusBadge.tsx            # Semantic badge: READY/ERROR/PENDING/PROCESSING
        TerminalDivider.tsx        # Gradient fade divider with optional label
        FileUpload.tsx             # Drag & drop file upload zone
      search/
        SearchBar.tsx              # Input with autocomplete suggestions dropdown
        SearchResults.tsx          # Results list container
        ResultCard.tsx             # Single result: filename, chunk, score bar
      chat/
        ChatBubble.tsx             # User ($) / Assistant (>) message bubble
        ChatInput.tsx              # $ prompt input
        ChatLog.tsx                # Scrollable message container + cursor blink
        SourceBadge.tsx            # Source badge: doc_id + chunk + score
      documents/
        DocumentTable.tsx          # Table with filename, status badge, delete button
      ui/                          # shadcn/ui -- installed via CLI
        button.tsx, input.tsx, card.tsx, badge.tsx, dialog.tsx,
        table.tsx, tabs.tsx, separator.tsx, sheet.tsx, sonner.tsx
    pages/
      Documents.tsx                # Upload + document list
      Search.tsx                   # Search bar + results
      Chat.tsx                     # Chat log + input
      Mcp.tsx                      # Tool cards listing
      Eval.tsx                     # Run eval button + reports table
```

---

### Task 1: Project Scaffold

**Files:**
- Create: `frontend/package.json`
- Create: `frontend/vite.config.ts`
- Create: `frontend/tsconfig.json`
- Create: `frontend/tsconfig.app.json`
- Create: `frontend/tsconfig.node.json`
- Create: `frontend/index.html`

- [ ] **Step 1: Scaffold with Vite**

```bash
cd C:\Users\Luis\Documents\Desarrollo\KnowledgeForge
npm create vite@latest frontend -- --template react-ts
cd frontend
```

Expected: directory `frontend/` created with template files.

- [ ] **Step 2: Install dependencies**

```bash
cd C:\Users\Luis\Documents\Desarrollo\KnowledgeForge\frontend
npm install react-router-dom lucide-react clsx tailwind-merge class-variance-authority sonner @tanstack/react-table react-hook-form zod @hookform/resolvers
npm install -D tailwindcss @tailwindcss/vite postcss
```

Expected: `npm install` completes without errors.

- [ ] **Step 3: Install shadcn/ui**

```bash
npx shadcn@latest init -d
```

Expected: `components.json` created. CSS variables added. `src/lib/cn.ts` created.

- [ ] **Step 4: Verify scaffold builds**

```bash
npm run build
```

Expected: Build completes. `dist/` created.

- [ ] **Step 5: Commit**

```bash
git add frontend/
git commit -m "feat: scaffold frontend with Vite, React, Tailwind, shadcn/ui"
```

---

### Task 2: Design Tokens & Global CSS

**Files:**
- Write: `frontend/src/index.css` (replace scaffolded content)

- [ ] **Step 1: Write complete design token CSS with cyberpunk textures, typography, and animations**

Write `frontend/src/index.css`:

```css
@import "tailwindcss";
@import "https://fonts.googleapis.com/css2?family=Departure+Mono&family=Share+Tech+Mono&family=VT323&display=swap";

@theme {
  --font-display: "Departure Mono", monospace;
  --font-body: "Share Tech Mono", monospace;
  --font-accent: "VT323", monospace;

  --color-void: #030508;
  --color-bg-primary: #0B0D0F;
  --color-bg-surface: #12151A;
  --color-bg-surface-raised: #181C22;
  --color-bg-surface-hover: #1E222A;

  --color-border-ghost: rgba(255, 255, 255, 0.04);
  --color-border-subtle: #1E2028;
  --color-border-default: #282D38;
  --color-border-strong: #363C4A;

  --color-accent-primary: #39FF14;
  --color-accent-mid: #2BD600;
  --color-accent-dim: #1B8A00;
  --color-accent-bg: rgba(57, 255, 20, 0.07);
  --color-accent-glow: rgba(57, 255, 20, 0.25);

  --color-text-bright: #F0F2F5;
  --color-text-primary: #C8CCD4;
  --color-text-secondary: #7A8394;
  --color-text-muted: #4A5568;
  --color-text-ghost: #2D3548;

  --color-success: #39FF14;
  --color-error: #FF2E63;
  --color-warning: #FFB000;
  --color-info: #0AFFEF;

  --radius-sm: 3px;
  --radius-md: 6px;
  --radius-lg: 10px;
}

@layer base {
  *,
  *::before,
  *::after {
    box-sizing: border-box;
    margin: 0;
    padding: 0;
  }

  html {
    scroll-behavior: smooth;
  }

  body {
    font-family: var(--font-body);
    font-size: 0.875rem;
    line-height: 1.5;
    color: var(--color-text-primary);
    background-color: var(--color-bg-primary);
    -webkit-font-smoothing: antialiased;
    overflow-x: hidden;
  }

  ::-webkit-scrollbar { width: 5px; height: 5px; }
  ::-webkit-scrollbar-track { background: transparent; }
  ::-webkit-scrollbar-thumb { background: var(--color-border-default); border-radius: 9999px; }
  ::-webkit-scrollbar-thumb:hover { background: var(--color-text-muted); }

  ::selection {
    background: var(--color-accent-bg);
    color: var(--color-accent-primary);
  }
}

@layer utilities {
  .bg-grid {
    background-image:
      linear-gradient(rgba(255, 255, 255, 0.015) 1px, transparent 1px),
      linear-gradient(90deg, rgba(255, 255, 255, 0.015) 1px, transparent 1px);
    background-size: 40px 40px;
  }

  .bg-scanlines::before {
    content: '';
    position: fixed;
    inset: 0;
    pointer-events: none;
    z-index: 9998;
    background: repeating-linear-gradient(
      0deg, transparent, transparent 2px,
      rgba(0, 0, 0, 0.15) 2px, rgba(0, 0, 0, 0.15) 4px
    );
  }

  .bg-noise {
    position: relative;
  }

  .bg-noise::after {
    content: '';
    position: fixed;
    inset: 0;
    opacity: 0.035;
    pointer-events: none;
    z-index: 9999;
    background-image: url("data:image/svg+xml,%3Csvg viewBox='0 0 256 256' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='noise'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23noise)'/%3E%3C/svg%3E");
    background-repeat: repeat;
    background-size: 256px 256px;
  }

  .glow-text {
    text-shadow: 0 0 20px var(--color-accent-bg), 0 0 60px rgba(57, 255, 20, 0.08);
  }

  .border-glow {
    box-shadow: 0 0 20px var(--color-accent-bg), 0 0 60px rgba(57, 255, 20, 0.08);
  }
}

@keyframes cursor-blink {
  0%, 50% { opacity: 1; }
  51%, 100% { opacity: 0; }
}

@keyframes glow-pulse {
  0%, 100% { box-shadow: 0 0 5px var(--color-accent-bg); }
  50% { box-shadow: 0 0 20px var(--color-accent-bg), 0 0 60px rgba(57, 255, 20, 0.08); }
}

@keyframes status-pulse {
  0%, 100% { transform: scale(1); box-shadow: 0 0 0 0 var(--color-accent-bg); }
  50% { transform: scale(1.2); box-shadow: 0 0 0 6px transparent; }
}

@keyframes reveal-up {
  from { opacity: 0; transform: translateY(24px); filter: blur(4px); }
  to { opacity: 1; transform: translateY(0); filter: blur(0); }
}

.animate-cursor-blink { animation: cursor-blink 1s step-end infinite; }
.animate-glow-pulse { animation: glow-pulse 3s ease-in-out infinite; }
.animate-status-pulse { animation: status-pulse 3s ease-in-out infinite; }
.animate-reveal-up { animation: reveal-up 0.6s cubic-bezier(0.16, 1, 0.3, 1) both; }

@media (prefers-reduced-motion: reduce) {
  .bg-scanlines::before { display: none; }
  .animate-cursor-blink { animation: none; opacity: 1; }
  .animate-glow-pulse { animation: none; }
  .animate-status-pulse { animation: none; }
  .animate-reveal-up { animation: none; opacity: 1; transform: none; filter: none; }
}
```

- [ ] **Step 2: Update index.html with cyberpunk fonts and base styles**

Write `frontend/index.html`:

```html
<!doctype html>
<html lang="en" class="bg-noise bg-scanlines">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <meta name="description" content="KnowledgeForge -- Enterprise knowledge management terminal" />
    <title>KNOWLEDGEFORGE // v0.1</title>
    <link rel="icon" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 32 32'><text y='28' font-size='28'>◆</text></svg>" />
  </head>
  <body class="bg-grid">
    <div id="root"></div>
    <script type="module" src="/src/main.tsx"></script>
  </body>
</html>
```

- [ ] **Step 3: Verify CSS builds**

```bash
npm run build
```

Expected: Build completes without CSS errors.

- [ ] **Step 4: Commit**

```bash
git add frontend/src/index.css frontend/index.html
git commit -m "feat: add cyberpunk design tokens, textures, and animations"
```

---

### Task 3: Types & API Layer

**Files:**
- Write: `frontend/src/lib/api.ts`
- Write: `frontend/src/lib/cn.ts`
- Write: `frontend/src/types/index.ts`
- Write: `frontend/src/api/documents.ts`
- Write: `frontend/src/api/search.ts`
- Write: `frontend/src/api/chat.ts`
- Write: `frontend/src/api/mcp.ts`
- Write: `frontend/src/api/eval.ts`

- [ ] **Step 1: Write cn utility**

Write `frontend/src/lib/cn.ts`:

```typescript
import { clsx, type ClassValue } from "clsx";
import { twMerge } from "tailwind-merge";

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}
```

- [ ] **Step 2: Write base API client**

Write `frontend/src/lib/api.ts`:

```typescript
const BASE_URL = "http://localhost:8000";

interface RequestOptions {
  method?: string;
  body?: unknown;
  params?: Record<string, string>;
}

export async function apiRequest<T>(path: string, options: RequestOptions = {}): Promise<T> {
  const { method = "GET", body, params } = options;

  let url = `${BASE_URL}${path}`;
  if (params) {
    const searchParams = new URLSearchParams(params);
    url += `?${searchParams.toString()}`;
  }

  const headers: Record<string, string> = {};
  if (body && !(body instanceof FormData)) {
    headers["Content-Type"] = "application/json";
  }

  const response = await fetch(url, {
    method,
    headers,
    body: body instanceof FormData ? body : body ? JSON.stringify(body) : undefined,
  });

  if (!response.ok) {
    const errorText = await response.text();
    throw new Error(errorText || `Request failed: ${response.status}`);
  }

  if (response.status === 204) return undefined as T;

  return response.json();
}
```

- [ ] **Step 3: Write TypeScript types**

Write `frontend/src/types/index.ts`:

```typescript
export interface Document {
  id: string;
  filename: string;
  content_hash: string;
  status: "pending" | "processing" | "ready" | "error";
  uploaded_at: string;
}

export interface DocumentUploadResponse {
  status: "queued";
  document_id: string;
}

export interface SearchResult {
  doc_id: string;
  chunk_index: number;
  content: string;
  score: number;
  filename: string;
  metadata: Record<string, string>;
}

export interface SearchResponse {
  results: SearchResult[];
  total: number;
}

export interface SourceInfo {
  doc_id: string;
  chunk_index: number;
  score: number;
}

export interface ChatResponse {
  answer: string;
  sources: SourceInfo[];
  session_id: string;
}

export interface ChatMessage {
  id: string;
  session_id: string;
  role: "user" | "assistant";
  content: string;
  context_used: SourceInfo[];
  created_at: string;
}

export interface ChatHistoryResponse {
  session_id: string;
  messages: ChatMessage[];
}

export interface McpTool {
  name: string;
  description: string;
}

export interface McpToolsResponse {
  tools: McpTool[];
}

export interface EvalMetric {
  faithfulness: number;
  answer_relevancy: number;
  context_precision: number;
}

export interface EvalReport {
  id: string;
  dataset: string;
  metrics: EvalMetric;
  created_at: string;
}

export interface EvalReportsResponse {
  reports: EvalReport[];
}
```

- [ ] **Step 4: Write API modules**

Write `frontend/src/api/documents.ts`:

```typescript
import { apiRequest } from "../lib/api";
import type { Document, DocumentUploadResponse } from "../types";

export function uploadDocument(file: File): Promise<DocumentUploadResponse> {
  const formData = new FormData();
  formData.append("file", file);
  return apiRequest<DocumentUploadResponse>("/documents", {
    method: "POST",
    body: formData,
  });
}

export function getDocument(id: string): Promise<Document> {
  return apiRequest<Document>(`/documents/${id}`);
}

export function deleteDocument(id: string): Promise<void> {
  return apiRequest<void>(`/documents/${id}`, { method: "DELETE" });
}
```

Write `frontend/src/api/search.ts`:

```typescript
import { apiRequest } from "../lib/api";
import type { SearchResponse } from "../types";

export function search(query: string, k: number = 5): Promise<SearchResponse> {
  return apiRequest<SearchResponse>("/search", {
    method: "POST",
    body: { query, k },
  });
}

export function getSuggestions(q: string): Promise<{ suggestions: string[] }> {
  return apiRequest<{ suggestions: string[] }>("/search/suggest", {
    params: { q },
  });
}
```

Write `frontend/src/api/chat.ts`:

```typescript
import { apiRequest } from "../lib/api";
import type { ChatResponse, ChatHistoryResponse } from "../types";

export function sendMessage(question: string, sessionId?: string): Promise<ChatResponse> {
  return apiRequest<ChatResponse>("/chat", {
    method: "POST",
    body: { question, session_id: sessionId },
  });
}

export function getChatHistory(sessionId: string): Promise<ChatHistoryResponse> {
  return apiRequest<ChatHistoryResponse>(`/chat/${sessionId}/history`);
}
```

Write `frontend/src/api/mcp.ts`:

```typescript
import { apiRequest } from "../lib/api";
import type { McpToolsResponse } from "../types";

export function listMcpTools(): Promise<McpToolsResponse> {
  return apiRequest<McpToolsResponse>("/mcp/tools");
}
```

Write `frontend/src/api/eval.ts`:

```typescript
import { apiRequest } from "../lib/api";
import type { EvalReportsResponse } from "../types";

export function runEvaluation(): Promise<{ status: string }> {
  return apiRequest<{ status: string }>("/eval/run", { method: "POST" });
}

export function listEvalReports(): Promise<EvalReportsResponse> {
  return apiRequest<EvalReportsResponse>("/eval/reports");
}
```

- [ ] **Step 5: Verify TypeScript compiles**

```bash
npx tsc --noEmit
```

Expected: No TypeScript errors.

- [ ] **Step 6: Commit**

```bash
git add frontend/src/lib/ frontend/src/types/ frontend/src/api/
git commit -m "feat: add API client, types, and endpoint modules"
```

---

### Task 4: Layout Shell

**Files:**
- Write: `frontend/src/components/layout/Navbar.tsx`
- Write: `frontend/src/components/layout/Sidebar.tsx`
- Write: `frontend/src/components/layout/Footer.tsx`
- Write: `frontend/src/components/layout/Layout.tsx`

- [ ] **Step 1: Write Navbar component**

Write `frontend/src/components/layout/Navbar.tsx`:

```typescript
import { NavLink, useLocation } from "react-router-dom";
import { Diamond } from "lucide-react";

const ROUTE_LABELS: Record<string, string> = {
  "/documents": "DOCUMENTS",
  "/search": "SEARCH",
  "/chat": "CHAT",
  "/mcp": "MCP",
  "/eval": "EVALUATION",
};

export function Navbar() {
  const location = useLocation();
  const pathSegments = location.pathname.split("/").filter(Boolean);
  const currentLabel = ROUTE_LABELS[location.pathname] || "TERMINAL";

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
          <span className="text-xs text-text-secondary tracking-wider">SYS:ONLINE</span>
        </div>
      </div>
    </nav>
  );
}
```

- [ ] **Step 2: Write Sidebar component**

Write `frontend/src/components/layout/Sidebar.tsx`:

```typescript
import { NavLink } from "react-router-dom";
import { FileText, Search, MessageSquare, Wrench, BarChart3 } from "lucide-react";

const NAV_ITEMS = [
  { to: "/documents", label: "DOCUMENTS", icon: FileText, index: "01" },
  { to: "/search", label: "SEARCH", icon: Search, index: "02" },
  { to: "/chat", label: "CHAT", icon: MessageSquare, index: "03" },
  { to: "/mcp", label: "MCP_TOOLS", icon: Wrench, index: "04" },
  { to: "/eval", label: "EVALUATION", icon: BarChart3, index: "05" },
];

export function Sidebar() {
  return (
    <aside className="w-[240px] flex-shrink-0 bg-bg-surface border-r border-border-ghost flex flex-col py-6">
      <div className="px-4 mb-6">
        <span className="text-2xs text-text-ghost tracking-widest uppercase">// CORE MODULES</span>
      </div>
      <nav className="flex flex-col gap-1 px-3">
        {NAV_ITEMS.map((item) => {
          const Icon = item.icon;
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
          );
        })}
      </nav>
    </aside>
  );
}
```

- [ ] **Step 3: Write Footer component**

Write `frontend/src/components/layout/Footer.tsx`:

```typescript
export function Footer() {
  return (
    <footer className="px-6 py-3 text-center font-body text-xs text-text-muted tracking-widest border-t border-border-ghost">
      // SYS.v0.1 | RTT:12ms | (c) KnowledgeForge Terminal
    </footer>
  );
}
```

- [ ] **Step 4: Write Layout component**

Write `frontend/src/components/layout/Layout.tsx`:

```typescript
import { Outlet } from "react-router-dom";
import { Navbar } from "./Navbar";
import { Sidebar } from "./Sidebar";
import { Footer } from "./Footer";

export function Layout() {
  return (
    <div className="flex flex-col min-h-screen">
      <Navbar />
      <div className="flex flex-1">
        <Sidebar />
        <main className="flex-1 p-8 overflow-auto">
          <Outlet />
        </main>
      </div>
      <Footer />
    </div>
  );
}
```

- [ ] **Step 5: Verify TypeScript compiles**

```bash
npx tsc --noEmit
```

Expected: No errors.

- [ ] **Step 6: Commit**

```bash
git add frontend/src/components/layout/
git commit -m "feat: add layout shell (Navbar, Sidebar, Footer, Layout)"
```

---

### Task 5: Common Components & shadcn/ui

**Files:**
- Write: `frontend/src/components/common/PanelCard.tsx`
- Write: `frontend/src/components/common/StatusBadge.tsx`
- Write: `frontend/src/components/common/TerminalDivider.tsx`
- Write: `frontend/src/components/common/FileUpload.tsx`
- Create: `frontend/src/components/ui/button.tsx` (shadcn)
- Create: `frontend/src/components/ui/input.tsx` (shadcn)
- Create: `frontend/src/components/ui/card.tsx` (shadcn)
- Create: `frontend/src/components/ui/badge.tsx` (shadcn)
- Create: `frontend/src/components/ui/dialog.tsx` (shadcn)
- Create: `frontend/src/components/ui/table.tsx` (shadcn)
- Create: `frontend/src/components/ui/tabs.tsx` (shadcn)
- Create: `frontend/src/components/ui/separator.tsx` (shadcn)
- Create: `frontend/src/components/ui/sheet.tsx` (shadcn)
- Create: `frontend/src/components/ui/sonner.tsx` (shadcn)

Add shadcn base file: `src/lib/cn.ts` already exists from Task 3.

- [ ] **Step 1: Install shadcn/ui components**

```bash
npx shadcn@latest add button input card badge dialog table tabs separator sheet sonner --yes
```

Expected: Components created in `frontend/src/components/ui/`.

- [ ] **Step 2: Write PanelCard component**

Write `frontend/src/components/common/PanelCard.tsx`:

```typescript
import type { ReactNode } from "react";

interface PanelCardProps {
  index: string;
  title: string;
  children: ReactNode;
  className?: string;
  controls?: ReactNode;
}

export function PanelCard({ index, title, children, className = "", controls }: PanelCardProps) {
  return (
    <div className={`bg-bg-surface border border-border-subtle rounded-md overflow-hidden hover:border-border-default transition-colors ${className}`}>
      <div className="flex items-center justify-between px-5 py-4 border-b border-border-ghost">
        <h2 className="font-body text-sm font-bold text-accent-primary tracking-wider uppercase">
          <span className="text-text-muted font-normal mr-2">[{index}]</span>
          {title}
        </h2>
        {controls && <div className="flex items-center gap-1">{controls}</div>}
      </div>
      <div className="p-5">{children}</div>
    </div>
  );
}
```

- [ ] **Step 3: Write StatusBadge component**

Write `frontend/src/components/common/StatusBadge.tsx`:

```typescript
import { cn } from "../../lib/cn";

type Status = "pending" | "processing" | "ready" | "error";

const STATUS_STYLES: Record<Status, string> = {
  pending: "bg-transparent text-text-muted border-border-default",
  processing: "bg-warning/10 text-warning border-warning/20 animate-glow-pulse",
  ready: "bg-success/10 text-success border-success/20",
  error: "bg-error/10 text-error border-error/20",
};

interface StatusBadgeProps {
  status: Status;
  className?: string;
}

export function StatusBadge({ status, className }: StatusBadgeProps) {
  return (
    <span
      className={cn(
        "inline-flex items-center gap-1.5 font-body text-2xs font-medium tracking-widest uppercase px-2 py-0.5 rounded-sm border",
        STATUS_STYLES[status],
        className
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
  );
}
```

- [ ] **Step 4: Write TerminalDivider component**

Write `frontend/src/components/common/TerminalDivider.tsx`:

```typescript
interface TerminalDividerProps {
  label?: string;
}

export function TerminalDivider({ label }: TerminalDividerProps) {
  if (!label) {
    return (
      <div
        className="w-full h-px my-16"
        style={{
          background: "linear-gradient(90deg, transparent 0%, var(--color-border-default) 20%, var(--color-accent-dim) 50%, var(--color-border-default) 80%, transparent 100%)",
        }}
      />
    );
  }

  return (
    <div className="flex items-center gap-4 my-16">
      <div className="flex-1 h-px bg-gradient-to-r from-transparent to-border-default" />
      <span className="font-body text-2xs text-text-muted tracking-widest uppercase flex-shrink-0">
        {label}
      </span>
      <div className="flex-1 h-px bg-gradient-to-l from-transparent to-border-default" />
    </div>
  );
}
```

- [ ] **Step 5: Write FileUpload component**

Write `frontend/src/components/common/FileUpload.tsx`:

```typescript
import { useCallback, useState } from "react";
import { Upload } from "lucide-react";

interface FileUploadProps {
  onUpload: (file: File) => Promise<void>;
  disabled?: boolean;
}

export function FileUpload({ onUpload, disabled }: FileUploadProps) {
  const [dragging, setDragging] = useState(false);

  function handleDrag(over: boolean) {
    return (e: React.DragEvent) => {
      e.preventDefault();
      setDragging(over);
    };
  }

  const handleDrop = useCallback(
    (e: React.DragEvent) => {
      e.preventDefault();
      setDragging(false);
      const file = e.dataTransfer.files[0];
      if (file) onUpload(file);
    },
    [onUpload]
  );

  function handleChange(e: React.ChangeEvent<HTMLInputElement>) {
    const file = e.target.files?.[0];
    if (file) onUpload(file);
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
      <Upload className={`w-8 h-8 ${dragging ? "text-accent-primary" : "text-text-muted"}`} />
      <span className="font-body text-sm text-text-muted tracking-wide">
        $ DROP_FILE_HERE <span className="text-text-ghost">// or click to browse</span>
      </span>
      <input type="file" className="hidden" onChange={handleChange} disabled={disabled} />
    </label>
  );
}
```

- [ ] **Step 6: Verify TypeScript compiles**

```bash
npx tsc --noEmit
```

Expected: No errors. (May need to fix shadcn imports -- adapt if needed.)

- [ ] **Step 7: Commit**

```bash
git add frontend/src/components/common/ frontend/src/components/ui/
git commit -m "feat: add common components (PanelCard, StatusBadge, TerminalDivider, FileUpload) and shadcn/ui"
```

---

### Task 6: Hooks

**Files:**
- Write: `frontend/src/hooks/useDebounce.ts`
- Write: `frontend/src/hooks/useDocuments.ts`
- Write: `frontend/src/hooks/useSearch.ts`
- Write: `frontend/src/hooks/useChat.ts`

- [ ] **Step 1: Write useDebounce hook**

Write `frontend/src/hooks/useDebounce.ts`:

```typescript
import { useState, useEffect } from "react";

export function useDebounce<T>(value: T, delay: number): T {
  const [debouncedValue, setDebouncedValue] = useState<T>(value);

  useEffect(
    function updateDebouncedValue() {
      const timer = setTimeout(function setValue() {
        setDebouncedValue(value);
      }, delay);
      return function clearTimer() {
        clearTimeout(timer);
      };
    },
    [value, delay]
  );

  return debouncedValue;
}
```

- [ ] **Step 2: Write useDocuments hook**

Write `frontend/src/hooks/useDocuments.ts`:

```typescript
import { useState, useCallback } from "react";
import { uploadDocument, getDocument, deleteDocument } from "../api/documents";
import type { Document } from "../types";

export function useDocuments() {
  const [documents, setDocuments] = useState<Document[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const pendingDocs = documents.filter((d) => d.status === "pending" || d.status === "processing");
  const readyDocs = documents.filter((d) => d.status === "ready");
  const errorDocs = documents.filter((d) => d.status === "error");

  const handleUpload = useCallback(async (file: File) => {
    setError(null);
    setLoading(true);
    const result = await uploadDocument(file);
    const doc = await getDocument(result.document_id);
    setDocuments((prev) => [doc, ...prev]);
    setLoading(false);
  }, []);

  const handleDelete = useCallback(async (id: string) => {
    setError(null);
    await deleteDocument(id);
    setDocuments((prev) => prev.filter((d) => d.id !== id));
  }, []);

  return {
    documents,
    pendingDocs,
    readyDocs,
    errorDocs,
    loading,
    error,
    upload: handleUpload,
    delete: handleDelete,
  };
}
```

- [ ] **Step 3: Write useSearch hook**

Write `frontend/src/hooks/useSearch.ts`:

```typescript
import { useState, useCallback } from "react";
import { search, getSuggestions } from "../api/search";
import { useDebounce } from "./useDebounce";
import type { SearchResult } from "../types";

export function useSearch() {
  const [query, setQuery] = useState("");
  const [results, setResults] = useState<SearchResult[]>([]);
  const [suggestions, setSuggestions] = useState<string[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const debouncedQuery = useDebounce(query, 150);

  const handleSearch = useCallback(async (q: string, k: number = 5) => {
    setError(null);
    setLoading(true);
    const response = await search(q, k);
    setResults(response.results);
    setLoading(false);
  }, []);

  const fetchSuggestions = useCallback(async (q: string) => {
    if (q.length < 2) {
      setSuggestions([]);
      return;
    }
    const response = await getSuggestions(q);
    setSuggestions(response.suggestions);
  }, []);

  return {
    query,
    setQuery,
    debouncedQuery,
    results,
    suggestions,
    loading,
    error,
    search: handleSearch,
    fetchSuggestions,
  };
}
```

- [ ] **Step 4: Write useChat hook**

Write `frontend/src/hooks/useChat.ts`:

```typescript
import { useState, useCallback, useRef } from "react";
import { sendMessage, getChatHistory } from "../api/chat";
import type { ChatMessage, SourceInfo } from "../types";

interface DisplayMessage {
  role: "user" | "assistant";
  content: string;
  sources?: SourceInfo[];
}

export function useChat(sessionId?: string) {
  const [messages, setMessages] = useState<DisplayMessage[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [currentSessionId, setCurrentSessionId] = useState<string | null>(sessionId || null);
  const sessionIdRef = useRef(sessionId || null);

  const loadHistory = useCallback(async (sid: string) => {
    setError(null);
    const history = await getChatHistory(sid);
    setMessages(
      history.messages.map(function mapMessage(m: ChatMessage): DisplayMessage {
        return {
          role: m.role,
          content: m.content,
          sources: m.context_used,
        };
      })
    );
  }, []);

  const handleSend = useCallback(async (question: string) => {
    if (!question.trim()) return;

    setError(null);
    setMessages(function addUserMessage(prev) {
      return [...prev, { role: "user", content: question }];
    });
    setLoading(true);

    const response = await sendMessage(question, sessionIdRef.current || undefined);
    setCurrentSessionId(response.session_id);
    sessionIdRef.current = response.session_id;

    setMessages(function addAssistantMessage(prev) {
      return [
        ...prev,
        { role: "assistant", content: response.answer, sources: response.sources },
      ];
    });
    setLoading(false);
  }, []);

  return {
    messages,
    loading,
    error,
    sessionId: currentSessionId,
    send: handleSend,
    loadHistory,
  };
}
```

- [ ] **Step 5: Verify TypeScript compiles**

```bash
npx tsc --noEmit
```

Expected: No errors.

- [ ] **Step 6: Commit**

```bash
git add frontend/src/hooks/
git commit -m "feat: add hooks (useDocuments, useSearch, useChat, useDebounce)"
```

---

### Task 7: Documents Page

**Files:**
- Write: `frontend/src/components/documents/DocumentTable.tsx`
- Write: `frontend/src/pages/Documents.tsx`

- [ ] **Step 1: Write DocumentTable component**

Write `frontend/src/components/documents/DocumentTable.tsx`:

```typescript
import { Trash2 } from "lucide-react";
import { StatusBadge } from "../common/StatusBadge";
import type { Document } from "../../types";

interface DocumentTableProps {
  documents: Document[];
  onDelete: (id: string) => void;
}

export function DocumentTable({ documents, onDelete }: DocumentTableProps) {
  if (documents.length === 0) {
    return (
      <div className="text-center py-12">
        <span className="font-body text-sm text-text-muted">// NO_DOCUMENTS_FOUND</span>
      </div>
    );
  }

  return (
    <div className="overflow-x-auto">
      <table className="w-full border-collapse font-body text-sm">
        <thead>
          <tr>
            <th className="px-4 py-3 text-left text-text-muted text-xs font-medium tracking-widest uppercase border-b border-border-default">
              FILENAME
            </th>
            <th className="px-4 py-3 text-left text-text-muted text-xs font-medium tracking-widest uppercase border-b border-border-default">
              STATUS
            </th>
            <th className="px-4 py-3 text-left text-text-muted text-xs font-medium tracking-widest uppercase border-b border-border-default">
              HASH
            </th>
            <th className="px-4 py-3 text-right text-text-muted text-xs font-medium tracking-widest uppercase border-b border-border-default">
              ACTIONS
            </th>
          </tr>
        </thead>
        <tbody>
          {documents.map(function renderDocRow(doc) {
            return (
              <tr
                key={doc.id}
                className="border-b border-border-ghost hover:bg-bg-surface-hover transition-colors"
              >
                <td className="px-4 py-3 text-text-primary tabular-nums">{doc.filename}</td>
                <td className="px-4 py-3">
                  <StatusBadge status={doc.status} />
                </td>
                <td className="px-4 py-3 text-text-muted text-xs font-mono">
                  {doc.content_hash.slice(0, 12)}...
                </td>
                <td className="px-4 py-3 text-right">
                  <button
                    onClick={function handleDelete() { onDelete(doc.id); }}
                    className="p-1.5 text-text-muted hover:text-error transition-colors rounded hover:bg-error/10"
                    aria-label="Delete document"
                  >
                    <Trash2 className="w-4 h-4" />
                  </button>
                </td>
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
}
```

- [ ] **Step 2: Write Documents page**

Write `frontend/src/pages/Documents.tsx`:

```typescript
import { useDocuments } from "../hooks/useDocuments";
import { PanelCard } from "../components/common/PanelCard";
import { FileUpload } from "../components/common/FileUpload";
import { TerminalDivider } from "../components/common/TerminalDivider";
import { DocumentTable } from "../components/documents/DocumentTable";
import { toast } from "sonner";

export function Documents() {
  const { documents, loading, error, upload, delete: deleteDoc } = useDocuments();

  async function handleUpload(file: File) {
    try {
      await upload(file);
      toast.success(`[$ UPLOAD_OK] ${file.name}`);
    } catch {
      toast.error(`[! UPLOAD_FAILED] ${file.name}`);
    }
  }

  async function handleDelete(id: string) {
    try {
      await deleteDoc(id);
      toast.success("[$ DELETE_OK] Document removed");
    } catch {
      toast.error("[! DELETE_FAILED]");
    }
  }

  return (
    <div className="animate-reveal-up">
      <div className="mb-6">
        <h1 className="font-body text-lg font-bold text-accent-primary tracking-wider uppercase mb-2">
          <span className="text-text-muted">// </span>DOCUMENTS
        </h1>
        <span className="font-body text-2xs text-text-ghost tracking-wider">&lt; REF:0x4F2A &gt;</span>
      </div>

      <PanelCard index="01" title="UPLOAD">
        <FileUpload onUpload={handleUpload} disabled={loading} />
      </PanelCard>

      <TerminalDivider label="INDEX" />

      <PanelCard index="02" title="REPOSITORY">
        {error && (
          <div className="mb-4 px-4 py-2 bg-error/10 border border-error/20 rounded text-error text-xs font-body">
            [!] {error}
          </div>
        )}
        <DocumentTable documents={documents} onDelete={handleDelete} />
      </PanelCard>
    </div>
  );
}
```

- [ ] **Step 3: Verify TypeScript compiles**

```bash
npx tsc --noEmit
```

Expected: No errors.

- [ ] **Step 4: Commit**

```bash
git add frontend/src/components/documents/ frontend/src/pages/Documents.tsx
git commit -m "feat: add Documents page with upload and table"
```

---

### Task 8: Search Page

**Files:**
- Write: `frontend/src/components/search/SearchBar.tsx`
- Write: `frontend/src/components/search/ResultCard.tsx`
- Write: `frontend/src/components/search/SearchResults.tsx`
- Write: `frontend/src/pages/Search.tsx`

- [ ] **Step 1: Write SearchBar component**

Write `frontend/src/components/search/SearchBar.tsx`:

```typescript
import { useEffect } from "react";
import { Search as SearchIcon } from "lucide-react";

interface SearchBarProps {
  value: string;
  onChange: (value: string) => void;
  onSearch: (query: string) => void;
  suggestions: string[];
  loading?: boolean;
}

export function SearchBar({ value, onChange, onSearch, suggestions, loading }: SearchBarProps) {
  useEffect(
    function handleEnterKey() {
      function onKeyDown(e: KeyboardEvent) {
        if (e.key === "Enter" && value.trim()) {
          onSearch(value);
        }
      }
      document.addEventListener("keydown", onKeyDown);
      return function cleanup() {
        document.removeEventListener("keydown", onKeyDown);
      };
    },
    [value, onSearch]
  );

  return (
    <div className="relative">
      <div className="flex items-center gap-3 bg-bg-surface border border-border-default rounded-md px-4 py-3 focus-within:border-accent-primary focus-within:shadow-[0_0_0_3px_var(--color-accent-bg)] transition-all">
        <span className="text-accent-primary font-body text-sm">$</span>
        <input
          type="text"
          value={value}
          onChange={function handleChange(e) { onChange(e.target.value); }}
          placeholder="enter search query..."
          className="flex-1 bg-transparent border-none outline-none font-body text-sm text-text-primary placeholder:text-text-muted"
        />
        <button
          onClick={function handleClick() { onSearch(value); }}
          disabled={!value.trim() || loading}
          className="p-1.5 text-text-muted hover:text-accent-primary transition-colors disabled:opacity-30"
          aria-label="Search"
        >
          <SearchIcon className="w-4 h-4" />
        </button>
      </div>
      {suggestions.length > 0 && (
        <div className="absolute top-full left-0 right-0 mt-1 bg-bg-surface-raised border border-border-subtle rounded-md overflow-hidden z-10">
          {suggestions.map(function renderSuggestion(s, i) {
            return (
              <button
                key={i}
                onClick={function handleSuggestionClick() {
                  onChange(s);
                  onSearch(s);
                }}
                className="block w-full text-left px-4 py-2 text-xs font-body text-text-secondary hover:bg-bg-surface-hover hover:text-text-primary transition-colors"
              >
                {s}
              </button>
            );
          })}
        </div>
      )}
    </div>
  );
}
```

- [ ] **Step 2: Write ResultCard component**

Write `frontend/src/components/search/ResultCard.tsx`:

```typescript
import type { SearchResult } from "../../types";

interface ResultCardProps {
  result: SearchResult;
}

export function ResultCard({ result }: ResultCardProps) {
  const scorePct = (result.score * 100).toFixed(1);

  return (
    <div className="bg-bg-surface border border-border-subtle rounded-md p-4 hover:border-border-default transition-colors">
      <div className="flex items-center justify-between mb-2">
        <div className="flex items-center gap-2">
          <span className="font-body text-xs text-accent-primary font-semibold tracking-wider">
            {result.filename}
          </span>
          <span className="font-body text-2xs text-text-muted">
            [CHUNK_{result.chunk_index}]
          </span>
        </div>
        <span className="font-body text-xs text-text-secondary tabular-nums">
          <span className="text-text-muted">MATCH: </span>
          <span className={Number(scorePct) > 80 ? "text-success" : Number(scorePct) > 50 ? "text-warning" : "text-text-secondary"}>
            {scorePct}%
          </span>
        </span>
      </div>
      <p className="font-body text-sm text-text-secondary leading-relaxed line-clamp-3">
        {result.content}
      </p>
    </div>
  );
}
```

- [ ] **Step 3: Write SearchResults component**

Write `frontend/src/components/search/SearchResults.tsx`:

```typescript
import { ResultCard } from "./ResultCard";
import type { SearchResult } from "../../types";

interface SearchResultsProps {
  results: SearchResult[];
  loading: boolean;
}

export function SearchResults({ results, loading }: SearchResultsProps) {
  if (loading) {
    return (
      <div className="space-y-3">
        {[1, 2, 3].map(function renderSkeleton(i) {
          return (
            <div key={i} className="bg-bg-surface border border-border-subtle rounded-md p-4 animate-pulse">
              <div className="h-3 w-32 bg-bg-surface-hover rounded mb-2" />
              <div className="h-4 w-full bg-bg-surface-hover rounded" />
            </div>
          );
        })}
      </div>
    );
  }

  if (results.length === 0) {
    return (
      <div className="text-center py-16">
        <span className="font-body text-sm text-text-muted">// ENTER_QUERY_TO_SEARCH</span>
      </div>
    );
  }

  return (
    <div className="space-y-3">
      <div className="flex items-center gap-2 mb-2">
        <span className="font-body text-xs text-text-muted">
          &gt; {results.length} result{results.length !== 1 ? "s" : ""} found
        </span>
      </div>
      {results.map(function renderResult(result, i) {
        return <ResultCard key={`${result.doc_id}-${result.chunk_index}`} result={result} />;
      })}
    </div>
  );
}
```

- [ ] **Step 4: Write Search page**

Write `frontend/src/pages/Search.tsx`:

```typescript
import { useSearch } from "../hooks/useSearch";
import { PanelCard } from "../components/common/PanelCard";
import { SearchBar } from "../components/search/SearchBar";
import { SearchResults } from "../components/search/SearchResults";

export function Search() {
  const { query, setQuery, results, suggestions, loading, search, fetchSuggestions } = useSearch();

  return (
    <div className="animate-reveal-up">
      <div className="mb-6">
        <h1 className="font-body text-lg font-bold text-accent-primary tracking-wider uppercase mb-2">
          <span className="text-text-muted">// </span>HYBRID_SEARCH
        </h1>
        <span className="font-body text-2xs text-text-ghost tracking-wider">
          pgvector + BM25 + RRF_K=60
        </span>
      </div>

      <PanelCard index="01" title="QUERY">
        <SearchBar
          value={query}
          onChange={function handleQueryChange(value: string) {
            setQuery(value);
            fetchSuggestions(value);
          }}
          onSearch={search}
          suggestions={suggestions}
          loading={loading}
        />
      </PanelCard>

      <div className="mt-6">
        <SearchResults results={results} loading={loading} />
      </div>
    </div>
  );
}
```

- [ ] **Step 5: Verify TypeScript compiles**

```bash
npx tsc --noEmit
```

Expected: No errors.

- [ ] **Step 6: Commit**

```bash
git add frontend/src/components/search/ frontend/src/pages/Search.tsx
git commit -m "feat: add Search page with autocomplete and results"
```

---

### Task 9: Chat Page

**Files:**
- Write: `frontend/src/components/chat/ChatBubble.tsx`
- Write: `frontend/src/components/chat/ChatInput.tsx`
- Write: `frontend/src/components/chat/ChatLog.tsx`
- Write: `frontend/src/components/chat/SourceBadge.tsx`
- Write: `frontend/src/pages/Chat.tsx`

- [ ] **Step 1: Write ChatBubble component**

Write `frontend/src/components/chat/ChatBubble.tsx`:

```typescript
import type { SourceInfo } from "../../types";
import { SourceBadge } from "./SourceBadge";

interface ChatBubbleProps {
  role: "user" | "assistant";
  content: string;
  sources?: SourceInfo[];
}

export function ChatBubble({ role, content, sources }: ChatBubbleProps) {
  const isUser = role === "user";
  const now = new Date().toLocaleTimeString("en-US", { hour12: false });

  return (
    <div className={`flex gap-3 ${isUser ? "justify-end" : "justify-start"}`}>
      <div className={`max-w-[80%] ${isUser ? "order-1" : ""}`}>
        <div className="flex items-center gap-2 mb-1">
          <span className="font-body text-2xs text-text-muted">[{now}]</span>
          <span className={`font-body text-xs font-semibold ${isUser ? "text-accent-primary" : "text-info"}`}>
            {isUser ? "$ USER" : "> ASSISTANT"}
          </span>
        </div>
        <div
          className={`p-4 rounded-md font-body text-sm leading-relaxed ${
            isUser
              ? "bg-accent-bg border border-accent-dim/30 text-text-primary"
              : "bg-bg-surface border border-border-subtle text-text-primary"
          }`}
        >
          <p className="whitespace-pre-wrap">{content}</p>
        </div>
        {!isUser && sources && sources.length > 0 && (
          <div className="flex flex-wrap gap-1.5 mt-2">
            {sources.map(function renderSource(s, i) {
              return <SourceBadge key={i} source={s} />;
            })}
          </div>
        )}
      </div>
    </div>
  );
}
```

- [ ] **Step 2: Write ChatInput component**

Write `frontend/src/components/chat/ChatInput.tsx`:

```typescript
import { useState } from "react";
import { Send } from "lucide-react";

interface ChatInputProps {
  onSend: (message: string) => void;
  disabled?: boolean;
}

export function ChatInput({ onSend, disabled }: ChatInputProps) {
  const [value, setValue] = useState("");

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!value.trim() || disabled) return;
    onSend(value.trim());
    setValue("");
  }

  return (
    <form onSubmit={handleSubmit} className="flex items-center gap-3 bg-bg-surface border border-border-default rounded-md px-4 py-3 focus-within:border-accent-primary focus-within:shadow-[0_0_0_3px_var(--color-accent-bg)] transition-all">
      <span className="text-accent-primary font-body text-sm">$</span>
      <input
        type="text"
        value={value}
        onChange={function handleChange(e) { setValue(e.target.value); }}
        placeholder="type your question..."
        disabled={disabled}
        className="flex-1 bg-transparent border-none outline-none font-body text-sm text-text-primary placeholder:text-text-muted"
      />
      <button
        type="submit"
        disabled={!value.trim() || disabled}
        className="p-1.5 text-text-muted hover:text-accent-primary transition-colors disabled:opacity-30"
        aria-label="Send message"
      >
        <Send className="w-4 h-4" />
      </button>
    </form>
  );
}
```

- [ ] **Step 3: Write ChatLog component**

Write `frontend/src/components/chat/ChatLog.tsx`:

```typescript
import { useEffect, useRef } from "react";
import { ChatBubble } from "./ChatBubble";
import type { SourceInfo } from "../../types";

interface Message {
  role: "user" | "assistant";
  content: string;
  sources?: SourceInfo[];
}

interface ChatLogProps {
  messages: Message[];
  loading: boolean;
}

export function ChatLog({ messages, loading }: ChatLogProps) {
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(
    function scrollToBottom() {
      bottomRef.current?.scrollIntoView({ behavior: "smooth" });
    },
    [messages]
  );

  if (messages.length === 0 && !loading) {
    return (
      <div className="flex-1 flex items-center justify-center">
        <div className="text-center">
          <span className="font-body text-sm text-text-muted">// INIT_SESSION</span>
          <p className="font-body text-xs text-text-ghost mt-2">$ enter a question to begin</p>
        </div>
      </div>
    );
  }

  return (
    <div className="flex-1 overflow-y-auto space-y-4 p-4">
      {messages.map(function renderMessage(msg, i) {
        return (
          <ChatBubble key={i} role={msg.role} content={msg.content} sources={msg.sources} />
        );
      })}
      {loading && (
        <div className="flex items-start gap-3">
          <div className="bg-bg-surface border border-border-subtle rounded-md px-4 py-3">
            <span className="inline-block w-2 h-4 bg-accent-primary rounded-sm animate-cursor-blink" />
          </div>
        </div>
      )}
      <div ref={bottomRef} />
    </div>
  );
}
```

- [ ] **Step 4: Write SourceBadge component**

Write `frontend/src/components/chat/SourceBadge.tsx`:

```typescript
import type { SourceInfo } from "../../types";

interface SourceBadgeProps {
  source: SourceInfo;
}

export function SourceBadge({ source }: SourceBadgeProps) {
  const shortId = source.doc_id.slice(0, 8);

  return (
    <span className="inline-flex items-center gap-1.5 px-2 py-0.5 bg-bg-surface-hover border border-border-subtle rounded-sm text-2xs font-body text-text-muted">
      <span className="text-accent-dim">doc:</span>
      {shortId}
      <span className="text-text-ghost">|</span>
      <span className="text-accent-dim">ch:</span>
      {source.chunk_index}
      <span className="text-text-ghost">|</span>
      <span className="text-accent-primary">{(source.score * 100).toFixed(0)}%</span>
    </span>
  );
}
```

- [ ] **Step 5: Write Chat page**

Write `frontend/src/pages/Chat.tsx`:

```typescript
import { useChat } from "../hooks/useChat";
import { PanelCard } from "../components/common/PanelCard";
import { ChatLog } from "../components/chat/ChatLog";
import { ChatInput } from "../components/chat/ChatInput";

export function Chat() {
  const { messages, loading, sessionId, send } = useChat();

  return (
    <div className="animate-reveal-up flex flex-col" style={{ height: "calc(100vh - 160px)" }}>
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h1 className="font-body text-lg font-bold text-accent-primary tracking-wider uppercase mb-1">
            <span className="text-text-muted">// </span>CHAT
          </h1>
          {sessionId && (
            <span className="font-body text-2xs text-text-muted">
              SESSION: {sessionId.slice(0, 8)}...
            </span>
          )}
        </div>
      </div>

      <PanelCard index="01" title="TERMINAL" className="flex flex-col flex-1">
        <ChatLog messages={messages} loading={loading} />
        <div className="border-t border-border-ghost pt-3">
          <ChatInput onSend={send} disabled={loading} />
        </div>
      </PanelCard>
    </div>
  );
}
```

- [ ] **Step 6: Verify TypeScript compiles**

```bash
npx tsc --noEmit
```

Expected: No errors.

- [ ] **Step 7: Commit**

```bash
git add frontend/src/components/chat/ frontend/src/pages/Chat.tsx
git commit -m "feat: add Chat page with session history and sources"
```

---

### Task 10: MCP & Eval Pages

**Files:**
- Write: `frontend/src/pages/Mcp.tsx`
- Write: `frontend/src/pages/Eval.tsx`

- [ ] **Step 1: Write MCP page**

Write `frontend/src/pages/Mcp.tsx`:

```typescript
import { useState, useEffect } from "react";
import { listMcpTools } from "../api/mcp";
import { PanelCard } from "../components/common/PanelCard";
import type { McpTool } from "../types";

export function Mcp() {
  const [tools, setTools] = useState<McpTool[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(
    function loadTools() {
      listMcpTools()
        .then(function handleSuccess(response) {
          setTools(response.tools);
        })
        .finally(function handleFinally() {
          setLoading(false);
        });
    },
    []
  );

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

      <PanelCard index="01" title="REGISTERED_TOOLS">
        {loading ? (
          <div className="space-y-3">
            {[1, 2].map(function renderSkeleton(i) {
              return (
                <div key={i} className="p-4 border border-border-subtle rounded-md animate-pulse">
                  <div className="h-3 w-32 bg-bg-surface-hover rounded mb-2" />
                  <div className="h-4 w-full bg-bg-surface-hover rounded" />
                </div>
              );
            })}
          </div>
        ) : tools.length === 0 ? (
          <p className="font-body text-sm text-text-muted">// NO_TOOLS_REGISTERED</p>
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
                  <p className="font-body text-xs text-text-secondary">{tool.description}</p>
                </div>
              );
            })}
          </div>
        )}
      </PanelCard>
    </div>
  );
}
```

- [ ] **Step 2: Write Eval page**

Write `frontend/src/pages/Eval.tsx`:

```typescript
import { useState, useCallback } from "react";
import { runEvaluation, listEvalReports } from "../api/eval";
import { PanelCard } from "../components/common/PanelCard";
import type { EvalReport } from "../types";
import { toast } from "sonner";

export function Eval() {
  const [reports, setReports] = useState<EvalReport[]>([]);
  const [running, setRunning] = useState(false);

  useEffect(
    function loadReportsOnMount() {
      listEvalReports().then(function handleSuccess(response) {
        setReports(response.reports);
      });
    },
    []
  );

  async function handleRun() {
    setRunning(true);
    await runEvaluation();
    toast.success("[$ EVAL_COMPLETE] Report generated");
    const response = await listEvalReports();
    setReports(response.reports);
    setRunning(false);
  }

  return (
    <div className="animate-reveal-up">
      <div className="mb-6">
        <h1 className="font-body text-lg font-bold text-accent-primary tracking-wider uppercase mb-2">
          <span className="text-text-muted">// </span>EVALUATION
        </h1>
        <span className="font-body text-2xs text-text-ghost tracking-wider">
          RAGAS -- faithfulness, answer_relevancy, context_precision
        </span>
      </div>

      <PanelCard index="01" title="RUN_EVALUATION">
        <button
          onClick={handleRun}
          disabled={running}
          className="font-body text-sm font-medium tracking-wider uppercase px-6 py-3 bg-accent-primary text-bg-primary rounded-md hover:shadow-[0_0_20px_var(--color-accent-bg),0_0_60px_rgba(57,255,20,0.08)] transition-all disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {running ? (
            <span className="flex items-center gap-2">
              <span className="inline-block w-2 h-4 bg-bg-primary rounded-sm animate-cursor-blink" />
              RUNNING...
            </span>
          ) : (
            "$ EXECUTE_EVALUATION"
          )}
        </button>
      </PanelCard>

      <div className="mt-6">
        <PanelCard index="02" title="REPORTS">
          {reports.length === 0 ? (
            <p className="font-body text-sm text-text-muted">
              // NO_REPORTS -- run evaluation to generate
            </p>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full border-collapse font-body text-sm">
                <thead>
                  <tr>
                    <th className="px-4 py-3 text-left text-text-muted text-xs font-medium tracking-widest uppercase border-b border-border-default">
                      DATASET
                    </th>
                    <th className="px-4 py-3 text-right text-text-muted text-xs font-medium tracking-widest uppercase border-b border-border-default">
                      FAITHFULNESS
                    </th>
                    <th className="px-4 py-3 text-right text-text-muted text-xs font-medium tracking-widest uppercase border-b border-border-default">
                      RELEVANCY
                    </th>
                    <th className="px-4 py-3 text-right text-text-muted text-xs font-medium tracking-widest uppercase border-b border-border-default">
                      PRECISION
                    </th>
                  </tr>
                </thead>
                <tbody>
                  {reports.map(function renderReport(report) {
                    return (
                      <tr key={report.id} className="border-b border-border-ghost hover:bg-bg-surface-hover">
                        <td className="px-4 py-3 text-text-primary">{report.dataset}</td>
                        <td className="px-4 py-3 text-right tabular-nums text-success">
                          {(report.metrics.faithfulness * 100).toFixed(1)}%
                        </td>
                        <td className="px-4 py-3 text-right tabular-nums text-info">
                          {(report.metrics.answer_relevancy * 100).toFixed(1)}%
                        </td>
                        <td className="px-4 py-3 text-right tabular-nums text-warning">
                          {(report.metrics.context_precision * 100).toFixed(1)}%
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          )}
        </PanelCard>
      </div>
    </div>
  );
}
```

- [ ] **Step 3: Verify TypeScript compiles**

```bash
npx tsc --noEmit
```

Expected: No errors.

- [ ] **Step 4: Commit**

```bash
git add frontend/src/pages/Mcp.tsx frontend/src/pages/Eval.tsx
git commit -m "feat: add MCP and Eval pages"
```

---

### Task 11: Routing, App Entry & Final Integration

**Files:**
- Write: `frontend/src/App.tsx`
- Write: `frontend/src/main.tsx`
- Modify: `frontend/vite.config.ts`

- [ ] **Step 1: Write App component with routes**

Write `frontend/src/App.tsx`:

```typescript
import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import { Toaster } from "./components/ui/sonner";
import { Layout } from "./components/layout/Layout";
import { Documents } from "./pages/Documents";
import { Search } from "./pages/Search";
import { Chat } from "./pages/Chat";
import { Mcp } from "./pages/Mcp";
import { Eval } from "./pages/Eval";

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
          className: "font-body text-xs bg-bg-surface-raised border border-border-default text-text-primary",
        }}
      />
    </BrowserRouter>
  );
}
```

- [ ] **Step 2: Write main entry point**

Write `frontend/src/main.tsx`:

```typescript
import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import { App } from "./App";
import "./index.css";

createRoot(document.getElementById("root")!).render(
  <StrictMode>
    <App />
  </StrictMode>
);
```

- [ ] **Step 3: Configure Vite proxy for backend**

The existing `frontend/vite.config.ts` should be updated. Write `frontend/vite.config.ts`:

```typescript
import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import tailwindcss from "@tailwindcss/vite";

export default defineConfig({
  plugins: [react(), tailwindcss()],
  server: {
    port: 5173,
    proxy: {
      "/api": {
        target: "http://localhost:8000",
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api/, ""),
      },
    },
  },
});
```

- [ ] **Step 4: Build and verify**

```bash
npm run build
```

Expected: Build succeeds with no errors. `dist/` created.

- [ ] **Step 5: Verify TypeScript compiles**

```bash
npx tsc --noEmit
```

Expected: No errors.

- [ ] **Step 6: Commit**

```bash
git add frontend/src/App.tsx frontend/src/main.tsx frontend/vite.config.ts
git commit -m "feat: wire up routing, App shell, and Vite config"
```

---

### Task 12: Final Integration Test (Manual)

- [ ] **Step 1: Start backend services**

```bash
docker compose up -d postgres elasticsearch
docker compose up app
```

Expected: Backend running on `http://localhost:8000`. Health check at `GET /health` returns 200.

- [ ] **Step 2: Start frontend dev server**

```bash
cd frontend
npm run dev
```

Expected: Vite dev server on `http://localhost:5173`.

- [ ] **Step 3: Test Documents page**

1. Navigate to `http://localhost:5173/documents`
2. Upload a `.txt` file via drag & drop or browse
3. Verify document appears in table with status badge
4. Delete document and verify it disappears

- [ ] **Step 4: Test Search page**

1. Navigate to `http://localhost:5173/search`
2. Type query and press Enter
3. Verify results display with filename, chunk snippet, and match score
4. Verify autocomplete suggestions appear as you type

- [ ] **Step 5: Test Chat page**

1. Navigate to `http://localhost:5173/chat`
2. Type a question and press Enter
3. Verify assistant response with sources
4. Verify session ID appears in header

- [ ] **Step 6: Test MCP page**

1. Navigate to `http://localhost:5173/mcp`
2. Verify both tools listed: `search_knowledge` and `summarize_document`

- [ ] **Step 7: Test Eval page**

1. Navigate to `http://localhost:5173/eval`
2. Click `$ EXECUTE_EVALUATION`
3. Verify report generated (may fail if no documents ingested -- that's expected)

- [ ] **Step 8: Test responsive layout**

1. Resize browser to mobile width (< 768px)
2. Verify layout is usable (sidebar will be TODO for responsive -- basic layout works)
3. Resize back to desktop

- [ ] **Step 9: Commit if any changes needed**

```bash
git add -A
git commit -m "fix: integration adjustments after manual testing"
```

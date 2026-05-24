# KnowledgeForge Frontend SPA -- Design Spec (v2)

## Overview

React SPA con estética **Terminal/Cyberpunk** (Phosphor Green) que expone toda la funcionalidad del backend. Sin auth, single-user, conectado a `http://localhost:8000`.

## Stack

- React 18+ + Vite + TypeScript (strict)
- Tailwind CSS v4.1+
- shadcn/ui (button, input, card, table, dialog, toast, badge, tabs, navigation-menu)
- react-hook-form + zod (formularios)
- sonner (toasts)
- @tanstack/react-table (tablas de datos)
- Google Fonts: Departure Mono, Share Tech Mono, VT323

## Design System: Terminal Cyberpunk

### Personalidad
**"Corporate Sci-Fi Ops Center"** -- datos densos, limpio pero futurista, verde phosphor como acento primario.

### Paleta
```
Fondo base:      #0B0D0F
Fondo surface:   #12151A
Borde:           #1E2028 (ghost) / #282D38 (default)
Texto body:      #C8CCD4 (gris azulado frío)
Texto muted:     #4A5568
Acento primary:  #39FF14 (Phosphor Green)
Acento glow:     0 0 20px rgba(57,255,20,0.25)
Semantic success: #39FF14 | error: #FF2E63 | warning: #FFB000 | info: #0AFFEF
```

### Tipografía (Combo "Hacker Underground")
- Display/Hero: `Departure Mono` (títulos grandes, logos)
- Body: `Share Tech Mono` (texto principal, datos, tablas)
- Accent: `VT323` (badges, logs, timestamps)

### Atmósfera Visual
- Grid HUD de fondo (40px, opacidad 0.015)
- Noise texture overlay (SVG feTurbulence, opacidad 0.035)
- Scanlines horizontales (cada 4px)
- Scrollbar personalizada oscura
- Selección de texto con color phosphor

### Animaciones
- Page reveal staggered (0s, 0.1s, 0.2s...)
- Cursor blink para terminal (1s step-end)
- Glow pulse en hover de cards/buttons
- Status dot pulse (3s ease-in-out)
- Reveal-up con blur (curva ease-out-expo)

### Convenciones de Nomenclatura
- Títulos de sección: `UPPER_SNAKE_CASE`
- Navegación: `~/ category / section / active_page`
- Prefijos: `$` para comandos, `//` para comentarios, `[01]` para paneles
- Badges de estado: `[ONLINE]`, `[READY]`, `[ERROR]`

## Layout

```
+-- Navbar Terminal -------------------------------------------+
| ◆ KNOWLEDGEFORGE v0.1    [ONLINE]  ~/ category / page        |
+--------+-----------------------------------------------------+
|SIDEBAR |  MAIN CONTENT                                       |
|        |                                                     |
| [01]   |  // PAGE_TITLE                                      |
| DOCS   |  < REF:0x4F2A >                                     |
|        |                                                     |
| [02]   |  +-- Panel Card ----------------------------------+ |
| SEARCH |  | [01] SECTION_NAME                     [tab][tab]| |
|        |  |                                                | |
| [03]   |  |  Content area with terminal aesthetic          | |
| CHAT   |  |                                                | |
|        |  +------------------------------------------------+ |
| [04]   |                                                     |
| MCP    |                                                     |
|        |                                                     |
| [05]   |                                                     |
| EVAL   |                                                     |
+--------+-----------------------------------------------------+
| // SYS.v0.1 | RTT:12ms | (c) KnowledgeForge Terminal           |
+---------------------------------------------------------------+
```

## Routes

| Route | Page | Endpoints |
|-------|------|-----------|
| `/` | Redirect to `/documents` | -- |
| `/documents` | Document ingestion & management | POST/GET/DELETE `/documents` |
| `/search` | Hybrid search + autocomplete | POST `/search`, GET `/search/suggest` |
| `/chat` | RAG chat + session history | POST `/chat`, GET `/chat/{id}/history` |
| `/mcp` | MCP tools listing | GET `/mcp/tools` |
| `/eval` | RAGAS evaluation + reports | POST `/eval/run`, GET `/eval/reports` |

## Componentes Clave (estilo terminal)

### Navbar
- Ruta tipo filesystem: `~/ knowledgeforge / documents /`
- Brand: `◆ KNOWLEDGEFORGE` con versión `v0.1`
- Status dot `[ONLINE]` con pulso verde
- Glassmorphism oscuro (backdrop-filter blur)
- Bordes con gradiente que se desvanece

### Sidebar
- Numeración `[01]` a `[05]` para cada ítem
- Item activo en verde phosphor con italic
- Ítems inactivos en gris muted con hover sutil
- Texto en `UPPER_SNAKE_CASE`

### Panel Cards
- Borde sutil (#1E2028), se ilumina en hover
- Título con `[01] SECTION_NAME` en phosphor green
- Window dots decorativos opcionales (rojo, amarillo, verde)
- Corner brackets en secciones importantes

### Data Tables
- Headers en UPPERCASE con tracking exagerado
- Filas zebra oscuras con hover highlight
- Valores con color semántico (success verde, error rojo, warning ámbar)
- Borde izquierdo coloreado por tipo de dato
- Números en tabular-nums monoespaciados

### Buttons
- Primary: fondo phosphor, texto negro, glow en hover
- Outline: borde phosphor dim, sin fondo, glow en hover
- Ghost: transparente, texto muted, hover surface
- Texto en UPPERCASE con tracking wide

### Inputs
- Fondo surface (#12151A), borde default (#282D38)
- Focus: borde phosphor + glow ring
- Placeholder en muted con estilo italic
- Prefijo `$` o `▸` opcional

### Chat
- Mensajes estilo log panel con timestamps
- User: prefijo `$` en phosphor
- Assistant: prefijo `>` en cyan info
- Sources: badges con doc_id y score
- Cursor blink al final

### Status Badges
- `[READY]`: verde phosphor
- `[PROCESSING]`: ámbar warning con pulso
- `[ERROR]`: crimson alert
- `[PENDING]`: gris muted

## Pages

### Documents (`pages/Documents.tsx`)
- FileUpload con drag & drop (borde punteado phosphor en hover)
- Tabla de documentos con status badges
- Botón delete con confirmación dialog
- Empty state: `// NO_DOCUMENTS_FOUND` con icono

### Search (`pages/Search.tsx`)
- Input con autocomplete (suggestions tipo dropdown terminal)
- Result cards con filename, chunk snippet, score bar
- Score mostrado como `[MATCH: 0.87]`
- Empty state: `// ENTER_QUERY_TO_SEARCH`

### Chat (`pages/Chat.tsx`)
- Log panel con mensajes estilo terminal
- Input con `$` prompt
- Session ID mostrado como `SESS: a1b2c3...`
- Sources expandibles abajo de cada respuesta
- Loading: cursor blink animado

### MCP (`pages/Mcp.tsx`)
- Cards por herramienta con nombre + descripción
- Formato: `[TOOL] search_knowledge -- Hybrid search...`

### Eval (`pages/Eval.tsx`)
- Botón `RUN_EVALUATION` con glow en hover
- Tabla de reportes con métricas (faithfulness, relevancy, precision)
- Métricas con color semántico y progress bars

## Estructura de Archivos

```
frontend/
  src/
    api/                # Funciones fetch tipadas
      documents.ts
      search.ts
      chat.ts
      mcp.ts
      eval.ts
    components/
      ui/               # shadcn/ui (button, input, card, table, dialog, toast, badge, tabs)
      layout/
        Navbar.tsx
        Sidebar.tsx
        Layout.tsx
        Footer.tsx
      common/
        PanelCard.tsx      # Card con [NN] TITLE
        StatusBadge.tsx    # Badges semánticos
        SearchBar.tsx      # Input con autocomplete
        FileUpload.tsx     # Drop zone
        TerminalDivider.tsx
      chat/
        ChatBubble.tsx
        ChatInput.tsx
        ChatLog.tsx
      search/
        SearchResults.tsx
        ResultCard.tsx
      documents/
        DocumentCard.tsx
        DocumentTable.tsx
    pages/
      Documents.tsx
      Search.tsx
      Chat.tsx
      Mcp.tsx
      Eval.tsx
    hooks/
      useDocuments.ts
      useSearch.ts
      useChat.ts
    lib/
      api.ts             # Cliente HTTP base
      cn.ts              # Utility clsx + tailwind-merge
      tokens.css         # CSS variables del design system
    types/
      index.ts           # Interfaces TypeScript
  index.html
  package.json
  vite.config.ts
  tailwind.config.ts
  tsconfig.json
```

## Hooks (con React Best Practices)

### useDocuments()
- `documents`, `uploadDocument(file)`, `deleteDocument(id)`, `refresh()`
- loading/error states
- Derived `pendingDocs`, `readyDocs`, `failedDocs` computados en render (no useEffect)

### useSearch()
- `query`, `results`, `suggestions`, `search(query, k?, filters?)`
- Debounce 300ms en búsqueda (custom hook useDebounce)
- Suggestions con debounce 150ms

### useChat(sessionId?)
- `messages`, `sendMessage(question)`, `loading`
- Session ID management (localStorage + URL param)
- Message list con useMemo para evitar re-renders innecesarios

## Principios React (frontend-react-best-practices)

- **Functional setState**: callbacks estables sin dependencias de array
- **Derived state in render**: sin useEffect para derivar estado
- **Lazy state init**: valores costosos inicializados con `useState(() => ...)`
- **Named functions in useEffect**: debugging claro
- **Primitive dependencies**: suscribirse a `user.id` no a `user` entero
- **Error boundaries**: en cada sección de feature
- **Composition over boolean props**: componentes explícitos, no flags
- **No barrel imports**: imports directos para reducir bundle
- **useTransition**: para navegación y búsqueda no urgentes

## Accesibilidad

- Focus visible en todos los inputs y botones (ring phosphor)
- ARIA labels en iconos y botones sin texto
- Keyboard navigation en sidebar y modales
- `prefers-reduced-motion`: desactivar animaciones y scanlines
- Contraste WCAG AA: texto primario sobre fondo (#C8CCD4 sobre #0B0D0F = 13:1)
- Roles semánticos: `<main>`, `<nav>`, `<header>`, `<footer>`

## Responsive (Mobile-First)

```
Base (mobile <768px):
  - Sidebar colapsa a menú tipo sheet (shadcn Sheet)
  - Navbar compacto: solo logo + hamburger + status dot
  - Tablas con scroll horizontal
  - Cards full-width

Desktop (>=1024px):
  - Sidebar fijo izquierdo (240px)
  - Navbar con ruta filesystem completa
  - Grid de 2-3 columnas donde aplique
```

## Error Handling

- Toast (sonner) para errores de API con mensaje descriptivo
- Error state con retry button en cada página
- 404: `// RESOURCE_NOT_FOUND < REF:0x404 >`
- Network error: status dot cambia a `[OFFLINE]` rojo

## Loading States

- Skeleton loaders con animación pulse (mismo color que surface-hover)
- Chat loading: cursor blink `▌` parpadeante
- Upload progress: progress bar phosphor
- Spinner: glyph `◆` rotando con glow

## Excluido (v1)

- Autenticación
- Dark/light toggle (siempre dark)
- i18n
- PWA
- Tests E2E

# Componentes — Terminal/Cyberpunk Design System

Patrones HTML + CSS con personalidad. Cada componente tiene elementos decorativos
que lo hacen memorable: corner brackets, data annotations, glow effects, y
detalles que ningún dark theme genérico tendría.

Todos los componentes usan las variables de `design-tokens.md`.

---

## Tabla de Contenidos

1. [Terminal Navbar](#1-terminal-navbar)
2. [Panel Card](#2-panel-card)
3. [Data Table](#3-data-table)
4. [Log Panel](#4-log-panel)
5. [Status Indicators](#5-status-indicators)
6. [Sidebar](#6-sidebar)
7. [Buttons](#7-buttons)
8. [Inputs](#8-inputs)
9. [Badges y Tags](#9-badges-y-tags)
10. [Feature Cards](#10-feature-cards)
11. [Stats Cards](#11-stats-cards)
12. [CTA Section](#12-cta-section)
13. [Corner Brackets (Decorativo)](#13-corner-brackets)
14. [Data Annotations (Decorativo)](#14-data-annotations)
15. [Section Dividers](#15-section-dividers)
16. [Footer Terminal](#16-footer-terminal)

---

## 1. Terminal Navbar

Barra de navegación con ruta tipo filesystem y status del sistema.
El navbar tiene un fondo con backdrop-filter para un efecto glassmorphism
oscuro al hacer scroll.

```html
<nav class="term-nav">
  <div class="term-nav__route">
    <span class="term-nav__sep">~/</span>
    <a href="#" class="term-nav__seg">trading</a>
    <span class="term-nav__sep">/</span>
    <a href="#" class="term-nav__seg">monitor</a>
    <span class="term-nav__sep">/</span>
    <span class="term-nav__seg term-nav__seg--active">live_feed</span>
  </div>

  <div class="term-nav__status">
    <span class="status-dot status-dot--live"></span>
    <span class="term-nav__label">SYS:ONLINE</span>
    <span class="term-nav__meta">RTT:12ms</span>
  </div>
</nav>
```

```css
.term-nav {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: var(--space-3) var(--space-6);
  background: rgba(11, 13, 15, 0.85);
  backdrop-filter: blur(16px) saturate(180%);
  border-bottom: 1px solid var(--border-ghost);
  position: sticky;
  top: 0;
  z-index: var(--z-sticky);
  font-family: var(--font-body);
  font-size: var(--text-sm);
}

.term-nav__route {
  display: flex;
  align-items: center;
  gap: 2px;
}

.term-nav__sep { color: var(--text-muted); }

.term-nav__seg {
  color: var(--text-secondary);
  text-decoration: none;
  padding: 2px 4px;
  border-radius: var(--radius-sm);
  transition: color var(--transition-fast);
}

.term-nav__seg:hover {
  color: var(--text-primary);
  background: var(--bg-surface-hover);
}

/* Segmento activo: color de acento + italic */
.term-nav__seg--active {
  color: var(--accent-primary);
  font-style: italic;
  font-weight: var(--weight-semibold);
}

.term-nav__status {
  display: flex;
  align-items: center;
  gap: var(--space-3);
}

.term-nav__label {
  color: var(--text-secondary);
  letter-spacing: var(--tracking-wider);
  font-size: var(--text-xs);
}

.term-nav__meta {
  color: var(--text-muted);
  letter-spacing: var(--tracking-wider);
  font-size: var(--text-xs);
}
```

**Variante navbar con logo (landing pages):**

```html
<nav class="term-nav term-nav--branded">
  <div class="term-nav__brand">
    <span class="term-nav__glyph">◆</span>
    <span class="term-nav__name">SYSTEM_NAME</span>
    <span class="term-nav__ver">v2.4</span>
  </div>

  <div class="term-nav__links">
    <a href="#" class="term-nav__link term-nav__link--active">DASHBOARD</a>
    <a href="#" class="term-nav__link">MODULES</a>
    <a href="#" class="term-nav__link">NETWORK</a>
    <a href="#" class="term-nav__link">LOGS</a>
  </div>

  <div class="term-nav__actions">
    <button class="term-btn term-btn--primary">INIT_SESSION</button>
  </div>
</nav>
```

```css
.term-nav__brand {
  display: flex;
  align-items: center;
  gap: var(--space-2);
}

.term-nav__glyph {
  color: var(--accent-primary);
  font-size: var(--text-lg);
  filter: drop-shadow(var(--accent-glow));
}

.term-nav__name {
  font-family: var(--font-display);
  font-weight: var(--weight-bold);
  font-size: var(--text-base);
  color: var(--text-bright);
  letter-spacing: var(--tracking-wide);
}

.term-nav__ver {
  font-size: var(--text-2xs);
  color: var(--text-muted);
  padding: 1px 6px;
  border: 1px solid var(--border-subtle);
  border-radius: var(--radius-sm);
}

.term-nav__link {
  color: var(--text-secondary);
  font-family: var(--font-body);
  font-size: var(--text-sm);
  letter-spacing: var(--tracking-wider);
  padding: var(--space-2) var(--space-3);
  transition: color var(--transition-fast);
}

.term-nav__link:hover { color: var(--text-bright); }

.term-nav__link--active {
  color: var(--accent-primary);
  position: relative;
}

/* Underline animada en link activo */
.term-nav__link--active::after {
  content: '';
  position: absolute;
  bottom: -2px;
  left: 0;
  width: 100%;
  height: 1px;
  background: var(--accent-primary);
  box-shadow: var(--accent-glow);
}
```

---

## 2. Panel Card

Panel con numeración `[01]`, borde sutil, y opcionalmente corner brackets decorativos.

```html
<div class="term-panel">
  <div class="term-panel__head">
    <h2 class="term-panel__title">
      <span class="term-panel__idx">[01]</span>
      PRICE_CHART
    </h2>
    <div class="term-panel__controls">
      <button class="term-tab">1m</button>
      <button class="term-tab term-tab--active">5m</button>
      <button class="term-tab">15m</button>
    </div>
  </div>
  <div class="term-panel__body">
    <!-- Contenido -->
  </div>
</div>
```

```css
.term-panel {
  background: var(--bg-surface);
  border: 1px solid var(--border-subtle);
  border-radius: var(--radius-md);
  overflow: hidden;
  transition: border-color var(--transition-base);
}

/* Hover: borde se ilumina sutilmente */
.term-panel:hover {
  border-color: var(--border-default);
}

.term-panel__head {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: var(--space-4) var(--space-5);
  border-bottom: 1px solid var(--border-ghost);
}

.term-panel__title {
  font-family: var(--font-body);
  font-size: var(--text-sm);
  font-weight: var(--weight-bold);
  color: var(--accent-primary);
  letter-spacing: var(--tracking-wider);
  text-transform: uppercase;
}

.term-panel__idx {
  color: var(--text-muted);
  margin-right: var(--space-2);
  font-weight: var(--weight-normal);
}

.term-panel__body {
  padding: var(--space-5);
}

/* Tabs de control */
.term-tab {
  font-family: var(--font-body);
  font-size: var(--text-xs);
  color: var(--text-muted);
  background: transparent;
  border: 1px solid var(--border-subtle);
  border-radius: var(--radius-sm);
  padding: var(--space-1) var(--space-3);
  cursor: pointer;
  transition: all var(--transition-fast);
}

.term-tab:hover {
  color: var(--text-primary);
  border-color: var(--border-default);
}

.term-tab--active {
  background: var(--accent-primary);
  color: var(--text-inverse);
  border-color: var(--accent-primary);
}

/* Variante: panel con window dots decorativos */
.term-panel__dots {
  display: flex;
  gap: 5px;
}

.term-panel__dot {
  width: 8px;
  height: 8px;
  border-radius: var(--radius-full);
}

.term-panel__dot--r { background: #FF5F57; }
.term-panel__dot--y { background: #FEBC2E; }
.term-panel__dot--g { background: #28C840; }
```

---

## 3. Data Table

Tabla estilo terminal con valores coloreados por semántica. Las filas
tienen un borde izquierdo con color del dot indicator.

```html
<table class="term-table">
  <thead>
    <tr>
      <th>ASSET_ID</th>
      <th>ALLOCATION</th>
      <th>ENTRY_PRICE</th>
      <th>CURRENT</th>
      <th>DELTA_%</th>
    </tr>
  </thead>
  <tbody>
    <tr class="term-table__row--positive">
      <td>■ BTC_USD</td>
      <td>1.4502</td>
      <td>$42,100.00</td>
      <td>$64,291.50</td>
      <td class="term-val--up">+52.7%</td>
    </tr>
    <tr class="term-table__row--negative">
      <td>■ SOL_USD</td>
      <td>145.00</td>
      <td>$120.50</td>
      <td>$112.40</td>
      <td class="term-val--down">-6.7%</td>
    </tr>
  </tbody>
</table>
```

```css
.term-table {
  width: 100%;
  border-collapse: collapse;
  font-family: var(--font-body);
  font-size: var(--text-sm);
}

.term-table thead th {
  padding: var(--space-3) var(--space-4);
  text-align: left;
  color: var(--text-muted);
  font-weight: var(--weight-medium);
  font-size: var(--text-xs);
  letter-spacing: var(--tracking-widest);
  text-transform: uppercase;
  border-bottom: 1px solid var(--border-default);
}

.term-table tbody td {
  padding: var(--space-3) var(--space-4);
  color: var(--text-primary);
  border-bottom: 1px solid var(--border-ghost);
  font-variant-numeric: tabular-nums;
}

.term-table tbody tr {
  transition: background var(--transition-fast);
}

.term-table tbody tr:hover {
  background: var(--bg-surface-hover);
}

/* Borde izquierdo coloreado en filas de datos */
.term-table__row--positive td:first-child {
  border-left: 2px solid var(--semantic-success);
  padding-left: var(--space-3);
}

.term-table__row--negative td:first-child {
  border-left: 2px solid var(--semantic-error);
  padding-left: var(--space-3);
}

/* Valores con color semántico */
.term-val--up { color: var(--semantic-success); font-weight: var(--weight-semibold); }
.term-val--down { color: var(--semantic-error); font-weight: var(--weight-semibold); }
.term-val--neutral { color: var(--text-secondary); }
```

---

## 4. Log Panel

Panel de logs con timestamps y niveles de severidad. Incluye cursor
parpadeante al final y scroll automático.

```html
<div class="term-log">
  <div class="term-log__line">
    <span class="term-log__ts">[10:04:21]</span>
    <span class="term-log__pfx">$</span>
    <span class="term-log__msg">Connecting to WSS endpoint...</span>
  </div>
  <div class="term-log__line">
    <span class="term-log__ts">[10:04:22]</span>
    <span class="term-log__pfx">$</span>
    <span class="term-log__msg">
      <span class="term-log__lvl term-log__lvl--info">INFO:</span>
      Connection established. Authenticating...
    </span>
  </div>
  <div class="term-log__line">
    <span class="term-log__ts">[10:04:45]</span>
    <span class="term-log__pfx">$</span>
    <span class="term-log__msg">
      <span class="term-log__lvl term-log__lvl--ok">SUCCESS:</span>
      Token verified. Access level: ROOT.
    </span>
  </div>
  <div class="term-log__line">
    <span class="term-log__ts">[10:05:12]</span>
    <span class="term-log__pfx">$</span>
    <span class="term-log__msg">
      <span class="term-log__lvl term-log__lvl--warn">WARN:</span>
      Minor slippage detected on order ID #88492
    </span>
  </div>
  <div class="term-log__cursor"></div>
</div>
```

```css
.term-log {
  padding: var(--space-4) var(--space-5);
  font-family: var(--font-body);
  font-size: var(--text-sm);
  line-height: var(--leading-relaxed);
  max-height: 300px;
  overflow-y: auto;
}

.term-log__line {
  display: flex;
  gap: var(--space-2);
  padding: 3px 0;
}

.term-log__ts {
  color: var(--text-muted);
  flex-shrink: 0;
  font-size: var(--text-xs);
}

.term-log__pfx {
  color: var(--accent-primary);
  flex-shrink: 0;
}

.term-log__msg { color: var(--text-secondary); }

/* Niveles de severidad */
.term-log__lvl--info { color: var(--semantic-info); }
.term-log__lvl--ok { color: var(--semantic-success); font-weight: var(--weight-bold); }
.term-log__lvl--warn { color: var(--semantic-warning); font-weight: var(--weight-bold); }
.term-log__lvl--err { color: var(--semantic-error); font-weight: var(--weight-bold); }

/* Cursor parpadeante */
.term-log__cursor {
  width: 7px;
  height: 14px;
  background: var(--accent-primary);
  animation: cursor-blink 1s step-end infinite;
  margin-top: var(--space-2);
  border-radius: 1px;
}
```

---

## 5. Status Indicators

```html
<!-- Dots de estado -->
<span class="status-dot status-dot--live"></span>
<span class="status-dot status-dot--dead"></span>
<span class="status-dot status-dot--warn"></span>

<!-- Dot con label -->
<div class="status-row">
  <span class="status-dot status-dot--live"></span>
  <span class="status-row__label">CONNECTED</span>
</div>

<!-- Progress bar -->
<div class="term-progress">
  <span class="term-progress__label">DATALINK_LOAD</span>
  <div class="term-progress__track">
    <div class="term-progress__fill" style="width: 87%"></div>
  </div>
  <span class="term-val--up">87%</span>
</div>
```

```css
.status-dot {
  display: inline-block;
  width: 7px;
  height: 7px;
  border-radius: var(--radius-full);
  flex-shrink: 0;
}

.status-dot--live {
  background: var(--semantic-success);
  box-shadow: 0 0 8px rgba(57, 255, 20, 0.5);
  animation: status-pulse 3s ease-in-out infinite;
}

.status-dot--dead {
  background: var(--semantic-error);
  box-shadow: 0 0 8px rgba(255, 46, 99, 0.4);
}

.status-dot--warn {
  background: var(--semantic-warning);
  box-shadow: 0 0 8px rgba(255, 176, 0, 0.4);
}

.status-row {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  font-family: var(--font-body);
  font-size: var(--text-sm);
}

.status-row__label {
  color: var(--accent-primary);
  letter-spacing: var(--tracking-wider);
}

.term-progress {
  display: flex;
  align-items: center;
  gap: var(--space-3);
  font-family: var(--font-body);
  font-size: var(--text-sm);
}

.term-progress__label {
  color: var(--text-secondary);
  letter-spacing: var(--tracking-wider);
  min-width: 120px;
  font-size: var(--text-xs);
}

.term-progress__track {
  flex: 1;
  height: 3px;
  background: var(--border-default);
  border-radius: var(--radius-full);
  overflow: hidden;
}

.term-progress__fill {
  height: 100%;
  background: var(--accent-primary);
  border-radius: var(--radius-full);
  box-shadow: var(--accent-glow);
  transition: width var(--transition-slow);
}
```

---

## 6-9. Sidebar, Buttons, Inputs, Badges

Misma filosofía: monospace, oscuro, acentos semánticos. Los patrones
CSS son similares a los componentes anteriores. Puntos clave:

### Buttons

```css
.term-btn {
  font-family: var(--font-body);
  font-size: var(--text-sm);
  font-weight: var(--weight-medium);
  letter-spacing: var(--tracking-wider);
  padding: var(--space-2) var(--space-5);
  border-radius: var(--radius-md);
  cursor: pointer;
  transition: all var(--transition-base);
  text-transform: uppercase;
  border: none;
}

.term-btn--primary {
  background: var(--accent-primary);
  color: var(--text-inverse);
  border: 1px solid var(--accent-primary);
}

.term-btn--primary:hover {
  box-shadow: var(--accent-glow);
  filter: brightness(0.9);
}

.term-btn--outline {
  background: transparent;
  color: var(--accent-primary);
  border: 1px solid var(--accent-dim);
}

.term-btn--outline:hover {
  background: var(--accent-bg);
  border-color: var(--accent-primary);
  box-shadow: var(--accent-glow);
}

.term-btn--ghost {
  background: transparent;
  color: var(--text-secondary);
  border: 1px solid transparent;
}

.term-btn--ghost:hover {
  color: var(--text-bright);
  background: var(--bg-surface-hover);
}
```

### Inputs

```css
.term-input {
  font-family: var(--font-body);
  font-size: var(--text-sm);
  color: var(--text-primary);
  background: var(--bg-surface);
  border: 1px solid var(--border-default);
  border-radius: var(--radius-md);
  padding: var(--space-3) var(--space-4);
  outline: none;
  transition: all var(--transition-fast);
  width: 100%;
}

.term-input::placeholder { color: var(--text-muted); }

.term-input:focus {
  border-color: var(--accent-primary);
  box-shadow: 0 0 0 3px var(--accent-bg);
}
```

### Badges

```css
.term-badge {
  font-family: var(--font-body);
  font-size: var(--text-2xs);
  font-weight: var(--weight-medium);
  letter-spacing: var(--tracking-widest);
  padding: 2px 8px;
  border-radius: var(--radius-sm);
  text-transform: uppercase;
}

.term-badge--ok {
  background: rgba(57, 255, 20, 0.1);
  color: var(--semantic-success);
  border: 1px solid rgba(57, 255, 20, 0.2);
}

.term-badge--err {
  background: rgba(255, 46, 99, 0.1);
  color: var(--semantic-error);
  border: 1px solid rgba(255, 46, 99, 0.2);
}

.term-badge--warn {
  background: rgba(255, 176, 0, 0.1);
  color: var(--semantic-warning);
  border: 1px solid rgba(255, 176, 0, 0.2);
}

.term-badge--info {
  background: rgba(10, 255, 239, 0.1);
  color: var(--semantic-info);
  border: 1px solid rgba(10, 255, 239, 0.2);
}
```

---

## 10. Feature Cards

Cards para features con prefijo de comentario y hover con glow.

```css
.term-feature {
  background: var(--bg-surface);
  border: 1px solid var(--border-subtle);
  border-radius: var(--radius-md);
  padding: var(--space-8) var(--space-6);
  transition: all var(--transition-base);
  position: relative;
}

/* Hover: borde brilla + card sube */
.term-feature:hover {
  border-color: var(--accent-dim);
  transform: translateY(-4px);
  box-shadow: var(--accent-glow);
}

.term-feature__icon {
  font-size: var(--text-2xl);
  margin-bottom: var(--space-5);
  color: var(--accent-primary);
  filter: drop-shadow(0 0 8px var(--accent-bg));
}

.term-feature__title {
  font-family: var(--font-display);
  font-size: var(--text-base);
  font-weight: var(--weight-bold);
  letter-spacing: var(--tracking-wider);
  color: var(--text-bright);
  margin-bottom: var(--space-3);
  text-transform: uppercase;
}

.term-feature__desc {
  font-family: var(--font-body);
  font-size: var(--text-sm);
  color: var(--text-secondary);
  line-height: var(--leading-relaxed);
}
```

---

## 11. Stats Cards

```css
.term-stat {
  background: var(--bg-surface);
  border: 1px solid var(--border-subtle);
  border-radius: var(--radius-md);
  padding: var(--space-5) var(--space-6);
  position: relative;
  overflow: hidden;
}

/* Glow decorativo en la esquina */
.term-stat::after {
  content: '';
  position: absolute;
  top: -20px;
  right: -20px;
  width: 80px;
  height: 80px;
  background: radial-gradient(circle, var(--accent-bg) 0%, transparent 70%);
  pointer-events: none;
}

.term-stat__label {
  font-family: var(--font-body);
  font-size: var(--text-xs);
  color: var(--text-muted);
  letter-spacing: var(--tracking-widest);
  text-transform: uppercase;
  margin-bottom: var(--space-3);
}

.term-stat__value {
  font-family: var(--font-display);
  font-size: var(--text-2xl);
  font-weight: var(--weight-heavy);
  color: var(--text-bright);
  letter-spacing: var(--tracking-tight);
  margin-bottom: var(--space-2);
}

.term-stat__delta {
  font-family: var(--font-body);
  font-size: var(--text-sm);
  color: var(--semantic-success);
}
```

---

## 12. CTA Section

```css
.term-cta {
  text-align: center;
  padding: var(--space-24) var(--space-8);
  background: var(--bg-surface);
  border: 1px solid var(--border-subtle);
  border-radius: var(--radius-lg);
  position: relative;
  overflow: hidden;
}

/* Grid HUD decorativo dentro del CTA */
.term-cta::before {
  content: '';
  position: absolute;
  inset: 0;
  background-image:
    linear-gradient(rgba(255,255,255,0.02) 1px, transparent 1px),
    linear-gradient(90deg, rgba(255,255,255,0.02) 1px, transparent 1px);
  background-size: 30px 30px;
  pointer-events: none;
}

.term-cta__icon {
  font-size: var(--text-3xl);
  color: var(--accent-primary);
  margin-bottom: var(--space-6);
  filter: drop-shadow(var(--accent-glow));
}

.term-cta__title {
  font-family: var(--font-display);
  font-size: var(--text-xl);
  font-weight: var(--weight-heavy);
  color: var(--text-bright);
  letter-spacing: var(--tracking-widest);
  margin-bottom: var(--space-4);
  position: relative;
}

.term-cta__text {
  font-family: var(--font-body);
  font-size: var(--text-base);
  color: var(--text-secondary);
  max-width: 480px;
  margin: 0 auto var(--space-8);
  line-height: var(--leading-relaxed);
  position: relative;
}
```

---

## 13. Corner Brackets (Decorativo)

Decoración con brackets en las esquinas de secciones. Agrega un toque
único de "interfaz de sci-fi" que ningún dark theme genérico tiene.

```html
<section class="corner-bracket">
  <h2>SECTION_TITLE</h2>
  <p>Content inside bracketed section</p>
</section>
```

```css
/* Brackets decorativos en las 4 esquinas */
.corner-bracket {
  position: relative;
  padding: var(--space-8);
}

.corner-bracket::before,
.corner-bracket::after {
  content: '';
  position: absolute;
  width: 16px;
  height: 16px;
  border-color: var(--accent-dim);
  border-style: solid;
  pointer-events: none;
}

/* Esquina superior izquierda */
.corner-bracket::before {
  top: 0;
  left: 0;
  border-width: 1px 0 0 1px;
}

/* Esquina inferior derecha */
.corner-bracket::after {
  bottom: 0;
  right: 0;
  border-width: 0 1px 1px 0;
}

/* Para las 4 esquinas, añadir un wrapper extra
   o usar un pseudo-elemento en un hijo */
```

---

## 14. Data Annotations (Decorativo)

Labels posicionados en absolute como si fueran metadata del sistema.

```html
<div class="data-anno-wrapper">
  <span class="data-anno data-anno--tl">< REF:0x4F2A ></span>
  <span class="data-anno data-anno--tr">// SYS.v4.2.1</span>

  <!-- Contenido principal -->
  <div class="content">...</div>
</div>
```

```css
.data-anno-wrapper {
  position: relative;
}

.data-anno {
  position: absolute;
  font-family: var(--font-body);
  font-size: var(--text-2xs);
  color: var(--text-ghost);
  letter-spacing: var(--tracking-wider);
  pointer-events: none;
  user-select: none;
}

.data-anno--tl { top: var(--space-2); left: var(--space-4); }
.data-anno--tr { top: var(--space-2); right: var(--space-4); }
.data-anno--bl { bottom: var(--space-2); left: var(--space-4); }
.data-anno--br { bottom: var(--space-2); right: var(--space-4); }
```

---

## 15. Section Dividers

Divisores entre secciones que se desvanecen a los lados.

```css
/* Línea con fade a los extremos */
.term-divider {
  width: 100%;
  height: 1px;
  background: linear-gradient(
    90deg,
    transparent 0%,
    var(--border-default) 20%,
    var(--accent-dim) 50%,
    var(--border-default) 80%,
    transparent 100%
  );
  margin: var(--space-16) 0;
}

/* Divider con label centrado */
.term-divider--labeled {
  display: flex;
  align-items: center;
  gap: var(--space-4);
  height: auto;
  background: none;
}

.term-divider--labeled::before,
.term-divider--labeled::after {
  content: '';
  flex: 1;
  height: 1px;
  background: linear-gradient(
    90deg,
    transparent,
    var(--border-default)
  );
}

.term-divider--labeled::after {
  background: linear-gradient(
    90deg,
    var(--border-default),
    transparent
  );
}

.term-divider__label {
  font-family: var(--font-body);
  font-size: var(--text-2xs);
  color: var(--text-muted);
  letter-spacing: var(--tracking-widest);
  text-transform: uppercase;
  flex-shrink: 0;
}
```

---

## 16. Footer Terminal

```css
.term-footer {
  padding: var(--space-4) var(--space-6);
  text-align: center;
  font-family: var(--font-body);
  font-size: var(--text-xs);
  color: var(--text-muted);
  letter-spacing: var(--tracking-widest);
  border-top: 1px solid var(--border-ghost);
}
```

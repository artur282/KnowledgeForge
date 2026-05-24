# Design Tokens — Terminal/Cyberpunk

Variables CSS y efectos de fondo que crean atmósfera visual. Este archivo
es el PRIMER recurso que se carga en cualquier proyecto.

## Variables CSS Root

```css
:root {
  /* ═══════════════════════════════════════════
     FONDOS Y SUPERFICIES
     No usar negro puro — tiene un tinte frío
     azulado que le da profundidad.
  ═══════════════════════════════════════════ */
  --bg-void: #030508;
  --bg-primary: #0B0D0F;
  --bg-surface: #12151A;
  --bg-surface-raised: #181C22;
  --bg-surface-hover: #1E222A;
  --bg-surface-active: #252A34;
  --bg-overlay: rgba(5, 8, 12, 0.92);

  /* ═══════════════════════════════════════════
     BORDES
     Con tinte azulado frío, no gris neutro.
  ═══════════════════════════════════════════ */
  --border-ghost: rgba(255, 255, 255, 0.04);
  --border-subtle: #1E2028;
  --border-default: #282D38;
  --border-strong: #363C4A;
  --border-accent: var(--accent-primary);

  /* ═══════════════════════════════════════════
     PALETAS DE ACENTO
     Elige UNA paleta por proyecto. No mezclar
     colores de diferentes paletas al azar.
  ═══════════════════════════════════════════ */

  /* Phosphor Green — clásico intenso */
  --green-bright: #39FF14;
  --green-mid: #2BD600;
  --green-dim: #1B8A00;
  --green-bg: rgba(57, 255, 20, 0.07);
  --green-glow: 0 0 20px rgba(57, 255, 20, 0.25),
                0 0 60px rgba(57, 255, 20, 0.08);

  /* Cyan Protocol — frío, analítico */
  --cyan-bright: #0AFFEF;
  --cyan-mid: #08C4BA;
  --cyan-dim: #067A73;
  --cyan-bg: rgba(10, 255, 239, 0.07);
  --cyan-glow: 0 0 20px rgba(10, 255, 239, 0.25),
               0 0 60px rgba(10, 255, 239, 0.08);

  /* Amber Terminal — retro cálido */
  --amber-bright: #FFB000;
  --amber-mid: #CC8D00;
  --amber-dim: #806000;
  --amber-bg: rgba(255, 176, 0, 0.07);
  --amber-glow: 0 0 20px rgba(255, 176, 0, 0.25),
                0 0 60px rgba(255, 176, 0, 0.08);

  /* Crimson Alert — urgencia, trading */
  --crimson-bright: #FF2E63;
  --crimson-mid: #CC2550;
  --crimson-dim: #801732;
  --crimson-bg: rgba(255, 46, 99, 0.07);
  --crimson-glow: 0 0 20px rgba(255, 46, 99, 0.25),
                  0 0 60px rgba(255, 46, 99, 0.08);

  /* Violet Synthwave — sci-fi gaming */
  --violet-bright: #BF40FF;
  --violet-mid: #9933CC;
  --violet-dim: #602080;
  --violet-bg: rgba(191, 64, 255, 0.07);
  --violet-glow: 0 0 20px rgba(191, 64, 255, 0.25),
                 0 0 60px rgba(191, 64, 255, 0.08);

  /* Mint Arctic — fintech premium */
  --mint-bright: #00FFAB;
  --mint-mid: #00CC89;
  --mint-dim: #008058;
  --mint-bg: rgba(0, 255, 171, 0.07);
  --mint-glow: 0 0 20px rgba(0, 255, 171, 0.25),
               0 0 60px rgba(0, 255, 171, 0.08);

  /* ═══════════════════════════════════════════
     ACENTO ACTIVO
     Asigna una paleta como la primaria.
     Cambia solo estos aliases por proyecto.
  ═══════════════════════════════════════════ */
  --accent-primary: var(--green-bright);
  --accent-mid: var(--green-mid);
  --accent-dim: var(--green-dim);
  --accent-bg: var(--green-bg);
  --accent-glow: var(--green-glow);

  /* Colores semánticos fijos (no cambian por paleta) */
  --semantic-success: #39FF14;
  --semantic-error: #FF2E63;
  --semantic-warning: #FFB000;
  --semantic-info: #0AFFEF;
  --semantic-neutral: #8B95A5;

  /* ═══════════════════════════════════════════
     TEXTO
     Gris azulado, nunca blanco puro ni gris
     neutro — tiene que sentirse "frío".
  ═══════════════════════════════════════════ */
  --text-bright: #F0F2F5;
  --text-primary: #C8CCD4;
  --text-secondary: #7A8394;
  --text-muted: #4A5568;
  --text-ghost: #2D3548;
  --text-accent: var(--accent-primary);
  --text-inverse: #0B0D0F;

  /* ═══════════════════════════════════════════
     TIPOGRAFÍA
     3 niveles: display, body, accent.
     Ver typography.md para combos completos.
  ═══════════════════════════════════════════ */
  --font-display: 'Space Grotesk', 'Departure Mono', monospace;
  --font-body: 'Share Tech Mono', 'IBM Plex Mono', monospace;
  --font-accent: 'VT323', 'Silkscreen', monospace;

  /* Escala tipográfica */
  --text-2xs: 0.5rem;      /* 8px */
  --text-xs: 0.625rem;     /* 10px */
  --text-sm: 0.75rem;      /* 12px */
  --text-base: 0.875rem;   /* 14px */
  --text-md: 1rem;          /* 16px */
  --text-lg: 1.25rem;      /* 20px */
  --text-xl: 1.5rem;       /* 24px */
  --text-2xl: 2rem;        /* 32px */
  --text-3xl: 2.5rem;      /* 40px */
  --text-4xl: 3.5rem;      /* 56px */
  --text-5xl: 4.5rem;      /* 72px */

  --weight-light: 300;
  --weight-normal: 400;
  --weight-medium: 500;
  --weight-semibold: 600;
  --weight-bold: 700;
  --weight-heavy: 800;
  --weight-black: 900;

  --leading-none: 1;
  --leading-tight: 1.15;
  --leading-snug: 1.3;
  --leading-normal: 1.5;
  --leading-relaxed: 1.7;

  --tracking-tighter: -0.04em;
  --tracking-tight: -0.02em;
  --tracking-normal: 0;
  --tracking-wide: 0.05em;
  --tracking-wider: 0.1em;
  --tracking-widest: 0.2em;
  --tracking-mega: 0.35em;

  /* ═══════════════════════════════════════════
     ESPACIADO
  ═══════════════════════════════════════════ */
  --space-px: 1px;
  --space-1: 0.25rem;
  --space-2: 0.5rem;
  --space-3: 0.75rem;
  --space-4: 1rem;
  --space-5: 1.25rem;
  --space-6: 1.5rem;
  --space-8: 2rem;
  --space-10: 2.5rem;
  --space-12: 3rem;
  --space-16: 4rem;
  --space-20: 5rem;
  --space-24: 6rem;
  --space-32: 8rem;

  /* ═══════════════════════════════════════════
     BORDES Y RADIOS
  ═══════════════════════════════════════════ */
  --radius-none: 0;
  --radius-sm: 3px;
  --radius-md: 6px;
  --radius-lg: 10px;
  --radius-xl: 16px;
  --radius-full: 9999px;

  /* ═══════════════════════════════════════════
     SOMBRAS Y EFECTOS
  ═══════════════════════════════════════════ */
  --shadow-sm: 0 1px 3px rgba(0, 0, 0, 0.5);
  --shadow-md: 0 4px 16px rgba(0, 0, 0, 0.6);
  --shadow-lg: 0 8px 32px rgba(0, 0, 0, 0.7);
  --shadow-inner: inset 0 1px 0 rgba(255, 255, 255, 0.03);
  --shadow-border-glow: inset 0 0 0 1px var(--accent-bg),
                        0 0 0 1px var(--accent-bg);

  /* ═══════════════════════════════════════════
     TRANSICIONES
  ═══════════════════════════════════════════ */
  --ease-out-expo: cubic-bezier(0.16, 1, 0.3, 1);
  --ease-in-out-quint: cubic-bezier(0.83, 0, 0.17, 1);
  --transition-fast: 0.15s var(--ease-out-expo);
  --transition-base: 0.25s var(--ease-out-expo);
  --transition-slow: 0.4s var(--ease-out-expo);
  --transition-slower: 0.6s var(--ease-in-out-quint);

  /* ═══════════════════════════════════════════
     Z-INDEX
  ═══════════════════════════════════════════ */
  --z-below: -1;
  --z-base: 0;
  --z-above: 10;
  --z-dropdown: 100;
  --z-sticky: 200;
  --z-overlay: 300;
  --z-modal: 400;
  --z-tooltip: 500;
  --z-toast: 600;
}
```

## Texturas de Fondo (Atmósfera)

Estos efectos se aplican al `body` o a contenedores principales para dar
profundidad. Combinar 2-3 para crear atmósfera visual.

### Grid HUD (Patrón de coordenadas)

```css
/* Grid sutil de 40px que evoca un HUD sci-fi */
.bg-grid {
  background-image:
    linear-gradient(
      rgba(255, 255, 255, 0.02) 1px,
      transparent 1px
    ),
    linear-gradient(
      90deg,
      rgba(255, 255, 255, 0.02) 1px,
      transparent 1px
    );
  background-size: 40px 40px;
}

/* Variante: grid con acento en intersecciones */
.bg-grid-dots {
  background-image: radial-gradient(
    circle,
    rgba(255, 255, 255, 0.05) 1px,
    transparent 1px
  );
  background-size: 32px 32px;
}
```

### Noise Texture (Estática CRT)

```css
/* Noise SVG inline como filter — efecto granualdo sutil */
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
```

### Scanlines (Líneas de Monitor CRT)

```css
/* Scanlines horizontales semitransparentes */
.bg-scanlines::before {
  content: '';
  position: fixed;
  inset: 0;
  pointer-events: none;
  z-index: 9998;
  background: repeating-linear-gradient(
    0deg,
    transparent,
    transparent 2px,
    rgba(0, 0, 0, 0.15) 2px,
    rgba(0, 0, 0, 0.15) 4px
  );
}
```

### Radial Glow (Iluminación CRT)

```css
/* Glow radial gigante como si un monitor iluminara */
.bg-radial-glow {
  background: radial-gradient(
    ellipse 60% 50% at 50% 30%,
    var(--accent-bg) 0%,
    transparent 70%
  );
}
```

### Vignette (Oscurecimiento de bordes)

```css
/* Oscurecimiento tipo viñeta de monitor viejo */
.bg-vignette::after {
  content: '';
  position: fixed;
  inset: 0;
  pointer-events: none;
  z-index: 9997;
  background: radial-gradient(
    ellipse at center,
    transparent 50%,
    rgba(0, 0, 0, 0.5) 100%
  );
}
```

### Ejemplo: Combinando Texturas

```css
/* body con grid + noise + scanlines + vignette */
body {
  background-color: var(--bg-primary);
  /* Grid HUD de fondo */
  background-image:
    linear-gradient(rgba(255, 255, 255, 0.015) 1px, transparent 1px),
    linear-gradient(90deg, rgba(255, 255, 255, 0.015) 1px, transparent 1px);
  background-size: 40px 40px;
}

/* Lo pongo todo junto con clases en <body class="bg-noise bg-scanlines bg-vignette"> */
```

## Animaciones Keyframes

```css
/* Cursor parpadeante tipo terminal */
@keyframes cursor-blink {
  0%, 50% { opacity: 1; }
  51%, 100% { opacity: 0; }
}

/* Pulsación de glow neón */
@keyframes glow-pulse {
  0%, 100% { box-shadow: 0 0 5px var(--accent-bg); }
  50% { box-shadow: var(--accent-glow); }
}

/* Scan line individual que cruza la pantalla */
@keyframes scan-sweep {
  0% { top: -5%; opacity: 0; }
  10% { opacity: 1; }
  90% { opacity: 1; }
  100% { top: 105%; opacity: 0; }
}

/* Typing reveal: texto se revela de izquierda a derecha */
@keyframes typing-reveal {
  from { width: 0; }
  to { width: 100%; }
}

/* Cursor de typing */
@keyframes blink-caret {
  from, to { border-color: transparent; }
  50% { border-color: var(--accent-primary); }
}

/* Fade in desde abajo con curva premium */
@keyframes reveal-up {
  from {
    opacity: 0;
    transform: translateY(24px);
    filter: blur(4px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
    filter: blur(0);
  }
}

/* Fade in lateral (para elementos de sidebar) */
@keyframes reveal-left {
  from {
    opacity: 0;
    transform: translateX(-20px);
  }
  to {
    opacity: 1;
    transform: translateX(0);
  }
}

/* Glitch rápido para textos hero */
@keyframes glitch-flicker {
  0%, 92% { opacity: 1; transform: translate(0); }
  93% { opacity: 0.8; transform: translate(-3px, 1px); }
  94% { opacity: 1; transform: translate(2px, -1px); }
  95% { opacity: 0.9; transform: translate(-1px, 2px); }
  96% { opacity: 1; transform: translate(1px, -2px); }
  97% { transform: translate(0); }
  100% { opacity: 1; transform: translate(0); }
}

/* Pulso de status dot */
@keyframes status-pulse {
  0%, 100% { transform: scale(1); box-shadow: 0 0 0 0 var(--accent-bg); }
  50% { transform: scale(1.2); box-shadow: 0 0 0 6px transparent; }
}

/* Counter/number incrementando */
@keyframes counter-up {
  from { opacity: 0; transform: translateY(8px); }
  to { opacity: 1; transform: translateY(0); }
}

/* Border glow animation para cards en hover */
@keyframes border-glow {
  0%, 100% { border-color: var(--border-subtle); }
  50% { border-color: var(--accent-dim); }
}
```

## Reset y Base Global

```css
*, *::before, *::after {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

html {
  font-size: 16px;
  scroll-behavior: smooth;
  /* Smooth scrollbar que no salta */
  scroll-padding-top: 80px;
}

body {
  font-family: var(--font-body);
  font-size: var(--text-base);
  line-height: var(--leading-normal);
  color: var(--text-primary);
  background-color: var(--bg-primary);
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  /* Prevenir scroll horizontal por elementos decorativos */
  overflow-x: hidden;
}

/* Scrollbar personalizada oscura */
::-webkit-scrollbar {
  width: 5px;
  height: 5px;
}

::-webkit-scrollbar-track {
  background: transparent;
}

::-webkit-scrollbar-thumb {
  background: var(--border-default);
  border-radius: var(--radius-full);
}

::-webkit-scrollbar-thumb:hover {
  background: var(--text-muted);
}

/* Selección con color de acento */
::selection {
  background: var(--accent-bg);
  color: var(--accent-primary);
}

/* Links sin decoración por defecto */
a {
  color: inherit;
  text-decoration: none;
}

/* Imágenes responsive */
img {
  max-width: 100%;
  height: auto;
  display: block;
}
```

## Breakpoints

```css
/* Mobile first. Estos breakpoints controlan
   cuándo los paneles side-by-side se apilan. */
@media (max-width: 480px)  { /* Mobile S  */ }
@media (max-width: 768px)  { /* Mobile L  */ }
@media (max-width: 1024px) { /* Tablet    */ }
@media (max-width: 1440px) { /* Desktop S */ }
/* Desktop L: default (sin media query) */
```

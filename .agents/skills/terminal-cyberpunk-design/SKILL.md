---
name: terminal-cyberpunk-design
description: >
  Apply a Terminal/CLI + Cyberpunk hacker aesthetic to web interfaces.
  Use this skill whenever building dashboards, landing pages, admin panels,
  monitoring UIs, trading platforms, or any web interface that should look
  like a hacker terminal, command-line interface, dev tools, or cyberpunk UI.
  Also use when the user mentions "dark mode extremo", "estilo terminal",
  "estética hacker", "cyberpunk", "retro-computing", "CLI aesthetic",
  "dev tools style", "monospace design", or wants a premium dark interface
  with neon accents and code-like typography.
---

# Terminal / Cyberpunk Design System

Skill para construir interfaces web con estética de terminal de comandos fusionada
con diseño cyberpunk moderno. El resultado debe sentirse como una interfaz de
sistema operativo de ciencia ficción: oscura, precisa, técnica e **inolvidable**.

> **PRINCIPIO FUNDAMENTAL**: Este no es un dark theme genérico con fuente monospace.
> Es una experiencia visual que mezcla la nostalgia de monitores CRT de fósforo
> con interfaces de ciencia ficción nivel Blade Runner. Cada interfaz debe tener
> PERSONALIDAD — algo que alguien recuerde después de cerrar la pestaña.

## Design Thinking — Antes de Codear

Antes de escribir una sola línea, define:

1. **¿Qué tipo de terminal es?** No todas las terminales son iguales:
   - **Military-grade ops center**: Austero, datos densos, sin decoración superflua
   - **Hacker underground**: Glitchy, ruidoso, con textura y artefactos visuales
   - **Corporate sci-fi**: Limpio pero futurista (estilo Minority Report)
   - **Retro phosphor**: CRT viejo, scanlines heavies, amber o green phosphor
   - **Neural interface**: Orgánico-tech, formas suaves mezcladas con datos duros

2. **¿Cuál es el "one thing" memorable?** Cada diseño necesita UN elemento
   que lo haga inolvidable: un efecto glitch en el título, un grid de fondo
   animado, un prompt que parece real, scanlines que reaccionan al scroll.

3. **Paleta de acento**: No uses siempre verde matrix `#00FF41`. Elige una
   personalidad cromática que encaje con el proyecto:
   - **Phosphor Green** `#39FF14` — clásico pero intenso
   - **Cyan Protocol** `#0AFFEF` — frío, datos, análisis
   - **Amber Terminal** `#FFB000` — retro-computing puro, calidez
   - **Crimson Alert** `#FF2E63` — urgencia, trading, alertas
   - **Violet Synthwave** `#BF40FF` — sci-fi, gaming, entretenimiento
   - **Arctic Mint** `#00FFAB` — limpio, fintech, premium

## Pilares Visuales

### 1. Atmósfera — Nunca Fondos Planos

El fondo NO es solo `#0A0A0A`. Debe tener PROFUNDIDAD:

- **Grid sutil**: Un patrón de líneas finas que evoque paper de coordenadas
  o un HUD de ciencia ficción (con CSS `repeating-linear-gradient`)
- **Noise texture**: Textura granulada sutil via SVG filter (`feTurbulence`)
  que simula la estática de un monitor viejo
- **Scanline overlay**: Líneas horizontales semitransparentes via `repeating-
  linear-gradient` que cruzan toda la pantalla
- **Radial glow**: Un degradado radial enorme y tenue centrado en la sección
  principal, como si un monitor CRT iluminara desde atrás
- **Vignette**: Oscurecimiento en los bordes de la viewport como un monitor real

Combinar 2-3 de estos efectos da profundidad inmediata.

### 2. Tipografía — El Alma, No el Default

Lee `references/typography.md` para opciones detalladas. Los principios clave:

- **NUNCA** usar Inter, Roboto, Arial o system fonts — son genéricos
- Usa fuentes con CARÁCTER: `Departure Mono`, `VT323`, `Share Tech Mono`,
  `Silkscreen` para retro, `Space Grotesk` como display
- Mezcla pesos agresivamente: títulos en weight 800+ vs body en 300-400
- Los títulos pueden ser ENORMES (48-72px) con letter-spacing exagerado
- Experimenta con `text-transform`, `font-variant: small-caps`, kerning negativo

### 3. Elementos Decorativos Únicos

Estos micro-detalles separan un diseño memorable de uno genérico:

- **Corner brackets**: `[ ]` decorativos en las esquinas de las secciones
  (hechos con pseudoelementos `::before`/`::after`)
- **Data annotations**: Pequeños labels tipo `// SYS.v4.2` o `< REF:0x4F >`
  posicionados en absolute como si fueran metadata del sistema
- **Line numbers**: Numeración tipo editor de código al margen de las secciones
- **Scan indicators**: Barras de progreso decorativas que avanzan lentamente
- **Interference artifacts**: Pequeños glitches en bordes usando `clip-path`
  o `skew` transforms
- **ASCII art**: Logos o separadores en ASCII como los banners de CLI tools
- **Typing indicators**: Prefijos como `>_`, `$`, `root@` antes de textos clave

### 4. Colores — Syntax Highlighting Sofisticado

No es suficiente con verde y rojo. Crea un sistema cromático que emule
un scheme de editor de código completo:

```
Fondo base:         #0B0D0F (no negro puro — tiene un tinte frío)
Fondo surface:      #12151A (panel/card)
Borde:              #1E2028 (apenas perceptible)
Texto body:         #C8CCD4 (no blanco — un gris azulado)
Texto dim:          #4A5568 (muted con carácter)
```

Los acentos deben tener sentido semántico como tokens de un editor:

- **Keywords**: color primario (funciones, acciones)
- **Strings**: verde o amarillo (valores, datos)
- **Numbers**: naranja o cyan (métricas, stats)
- **Comments**: gris con italic (metadata, timestamps)
- **Errors**: rojo con background sutil (alertas)
- **Types**: púrpura (categorías, tags)

### 5. Layout — Romper la Cuadrícula

- Usa grids ASIMÉTRICOS: `grid-template-columns: 2fr 1fr` o `3fr 1.2fr`
- Elementos que OVERLAP entre secciones con `margin-top: -40px` y z-index
- Secciones con ángulo diagonal via `clip-path: polygon(...)` o `skewY(-2deg)`
- Espaciado GENEROSO entre secciones (120-160px) para crear respiración dramática
- Bordes izquerdos gruesos con accent color como indicadores de sección activa
- Dividers decorativos: líneas con gradiente que se desvanecen a los lados

### 6. Animaciones — Orquestadas, No Decorativas

- **Page reveal**: Los elementos aparecen en secuencia con `animation-delay`
  staggered (0s, 0.1s, 0.2s...), no todos de golpe
- **Glitch effect**: CSS-only con `clip-path` y `transform: translate` alternado
  en keyframes rápidos (para títulos hero)
- **Typing simulation**: `overflow: hidden` + `white-space: nowrap` + animación
  de ancho que revela el texto carácter a carácter
- **Hover states**: Al hacer hover en cards, el borde brilla con `box-shadow`
  animado y el fondo se ilumina sutilmente
- **Scroll-triggered**: Elementos que aparecen al scrollear (con IntersectionObserver)

## Convenciones de Nomenclatura Visual

| Elemento              | Formato                          | Ejemplo                        |
|-----------------------|----------------------------------|--------------------------------|
| Títulos de sección    | `UPPER_SNAKE_CASE`               | `PRICE_CHART`, `SYSTEM_LOGS`   |
| Navegación/rutas      | Rutas tipo filesystem            | `~ / trading / monitor / live` |
| Prefijos de sección   | Comentarios de código            | `// CORE MODULES`              |
| Comandos/prompts      | Prompt de terminal               | `$ claude --analyze codebase`  |
| Numeración de panels  | Corchetes con padding zero       | `[01]`, `[02]`, `[03]`        |
| Subtítulos técnicos   | Prefijo con `>`                  | `> NETWORK_STATUS`             |
| IDs de assets         | Snake_case con prefijo           | `BTC_USD`, `ASSET_ID`         |

## Referencias Detalladas

| Archivo                         | Cuándo leerlo                                          |
|---------------------------------|--------------------------------------------------------|
| `references/design-tokens.md`   | SIEMPRE al iniciar. Variables CSS, texturas, animaciones |
| `references/components.md`      | Al implementar componentes (cards, tables, logs, nav)    |
| `references/typography.md`      | Al configurar tipografía y convenciones de texto         |

## Ejemplo Funcional

`examples/landing-page.html` — Landing page completa con todos los principios
aplicados: texturas de fondo, tipografía con carácter, elementos decorativos,
animaciones orquestadas, layout asimétrico. Úsalo como punto de partida.

## Anti-Patrones — LO QUE NUNCA HACER

1. ❌ Fondo plano `#000000` o `#0A0A0A` sin textura ni profundidad
2. ❌ Fuentes genéricas: Inter, Roboto, Arial, system fonts
3. ❌ Solo verde matrix `#00FF41` como único acento
4. ❌ Grid simétrico de 3 columnas iguales sin variación
5. ❌ Cards idénticos con solo texto cambiado — cada card debe tener vida
6. ❌ Animaciones genéricas (`fadeIn`, `slideUp`) sin orquestación
7. ❌ Borders gruesos y obvios — deben ser sutiles o con gradiente
8. ❌ Diseño que se confunda con "cualquier dark theme"

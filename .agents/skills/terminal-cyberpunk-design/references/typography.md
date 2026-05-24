# Tipografía — Terminal/Cyberpunk Design System

La tipografía es el ADN visual de este estilo. No es "poner monospace y listo" —
es crear una experiencia textual que haga sentir al usuario dentro de un
sistema operativo de ciencia ficción.

> **REGLA DE ORO**: Nunca usar Inter, Roboto, Arial ni system fonts.
> Son las fuentes que todo AI genera por defecto. Son la antítesis de
> lo que buscamos.

---

## Fuentes con Carácter

### Tier 1 — Display / Hero (Títulos grandes)

Fuentes para impacto visual máximo en tamaños 32px+.

| Fuente            | Vibe                          | Google Fonts | Ideal para                   |
|-------------------|-------------------------------|:------------:|------------------------------|
| **Departure Mono**| Geométrico, futurista         | ✅           | Títulos hero, logos           |
| **Space Grotesk** | Tech moderno, angular         | ✅           | Headings grandes, CTA        |
| **Orbitron**      | Sci-fi puro, espacial         | ✅           | Dashboards, gaming           |
| **Silkscreen**    | Pixel art, retro 8-bit        | ✅           | Efecto retro extremo         |
| **Press Start 2P**| Arcade, pixel pesado          | ✅           | Juegos, retro computing      |
| **Syne Mono**     | Artístico, poco común         | ✅           | Diseños editoriales          |
| **Major Mono Display** | Monospace display única  | ✅           | Logos, banners terminales    |

### Tier 2 — Body Monospace (Texto principal)

Fuentes monoespaciadas para cuerpo de texto, datos, código, logs.

| Fuente            | Vibe                          | Google Fonts | Ideal para                   |
|-------------------|-------------------------------|:------------:|------------------------------|
| **Share Tech Mono**| Técnico, limpio              | ✅           | Body principal, datos        |
| **VT323**         | Monitor CRT vintage           | ✅           | Logs, output de terminal     |
| **IBM Plex Mono** | Profesional, IBM heritage     | ✅           | Corporativo sci-fi           |
| **Source Code Pro**| Legible, Adobe                | ✅           | Código, tablas de datos      |
| **Inconsolata**   | Elegante, programming         | ✅           | Texto largo monoespaciado    |
| **Fira Code**     | Ligaduras de código           | ✅           | Bloques de código reales     |
| **JetBrains Mono**| Estándar dev, muy legible     | ✅           | Fallback si nada más encaja  |

### Tier 3 — Complementarias Sans-serif

Solo para textos descriptivos largos donde la legibilidad extendida es crítica.
**Úsalas con moderación** — el 80%+ del texto debe ser monoespaciado.

| Fuente            | Vibe                          | Google Fonts |
|-------------------|-------------------------------|:------------:|
| **Space Grotesk** | Tech, angular                 | ✅           |
| **Outfit**        | Moderna, con carácter         | ✅           |
| **Geist**         | Vercel-inspired, clean tech   | ✅           |
| **DM Sans**       | Geométrica, profesional       | ✅           |
| **Plus Jakarta Sans** | Contemporánea, premium   | ✅           |

---

## Combinaciones Recomendadas

No mezcles a ciegas. Aquí hay combos probados que funcionan:

### Combo 1: "Hacker Underground"

```css
--font-display: 'VT323', monospace;              /* CRT retro */
--font-body: 'Share Tech Mono', monospace;        /* Clean técnico */
--font-accent: 'Silkscreen', monospace;           /* Pixel para badges */
```

```html
<link href="https://fonts.googleapis.com/css2?family=VT323&family=Share+Tech+Mono&family=Silkscreen&display=swap" rel="stylesheet">
```

### Combo 2: "Corporate Sci-fi"

```css
--font-display: 'Space Grotesk', sans-serif;      /* Angular moderno */
--font-body: 'IBM Plex Mono', monospace;           /* Profesional IBM */
--font-accent: 'Orbitron', sans-serif;             /* Sci-fi para stats */
```

```html
<link href="https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;600;700&family=IBM+Plex+Mono:wght@400;500;600&family=Orbitron:wght@700&display=swap" rel="stylesheet">
```

### Combo 3: "Trading Terminal"

```css
--font-display: 'Departure Mono', monospace;       /* Futurista limpio */
--font-body: 'Source Code Pro', monospace;          /* Números legibles */
--font-accent: 'Major Mono Display', monospace;    /* Logo y branding */
```

```html
<link href="https://fonts.googleapis.com/css2?family=Departure+Mono&family=Source+Code+Pro:wght@400;500;600;700&family=Major+Mono+Display&display=swap" rel="stylesheet">
```

### Combo 4: "Retro Phosphor"

```css
--font-display: 'Press Start 2P', monospace;       /* Arcade pesado */
--font-body: 'VT323', monospace;                   /* CRT vintage */
--font-accent: 'Syne Mono', monospace;             /* Artístico raro */
```

```html
<link href="https://fonts.googleapis.com/css2?family=Press+Start+2P&family=VT323&family=Syne+Mono&display=swap" rel="stylesheet">
```

---

## Escala Tipográfica

| Token        | Tamaño   | Uso típico                                          |
|--------------|----------|------------------------------------------------------|
| `--text-xs`  | 10px     | Data annotations, metadata decorativa, version tags  |
| `--text-sm`  | 12px     | Timestamps, log entries, datos de tabla, badges      |
| `--text-base`| 14px     | Texto principal, body general                        |
| `--text-md`  | 16px     | Subtítulos, labels de importancia media              |
| `--text-lg`  | 20px     | Títulos de panel `[01] SECTION_NAME`                 |
| `--text-xl`  | 24px     | Títulos de sección principal                         |
| `--text-2xl` | 32px     | Valores grandes (precios, stats)                     |
| `--text-3xl` | 40px     | Hero subtitle                                       |
| `--text-4xl` | 48-56px  | Hero headline principal                              |
| `--text-5xl` | 64-72px  | Hero headline IMPACTO                                |

### Pesos y Tratamientos

| Peso/Estilo    | Uso                                               |
|----------------|----------------------------------------------------|
| `300` light    | Texto decorativo, labels secundarios               |
| `400` regular  | Body, descripciones                                |
| `500` medium   | Headers de tabla, labels, badges                   |
| `600` semibold | Subtítulos, links activos                          |
| `700` bold     | Títulos de panel, headings                         |
| `800-900` heavy| Hero headlines, máximo impacto                     |
| `italic`       | Segmento activo en nav, meta-comentarios           |
| `small-caps`   | Labels premium, categorías                         |

---

## Convenciones de Formato

### Títulos y Secciones

```
FORMATO:   UPPER_SNAKE_CASE
PESO:      bold (700) o heavy (800-900)
TRACKING:  wide (0.05em) a exagerado (0.2em)
TAMAÑO:    --text-lg mínimo, pero no tengas miedo de ir ENORME
```

### Navegación / Rutas

```
FORMATO:   ~/ruta/tipo/filesystem
COLOR:     muted para separadores, accent para segmento activo
ITÁLICA:   en el segmento activo
```

### Datos Numéricos

```
FUENTE:    SIEMPRE monoespaciada (para alineación de cifras)
TAMAÑO:    Generoso — los números importantes deben DOMINAR la vista
TRACKING:  Más apretado (-0.02em) en números grandes
```

### Prefijos Técnicos

| Prefijo  | Uso                             | Ejemplo                        |
|----------|---------------------------------|--------------------------------|
| `$`      | Comando de terminal             | `$ EXECUTE BUY 0.250 BTC`     |
| `//`     | Comentario / título de sección  | `// CORE MODULES`             |
| `>`      | Prompt / subtítulo              | `> NETWORK_STATUS`            |
| `#`      | Root prompt                     | `root@node:~#`                |
| `▸` `›`  | Input / prompt de comando       | `▸ Enter command...`          |
| `->`     | Resultado / retorno             | `-> Connection established`   |
| `< >`    | Data annotation                 | `< REF:0x4F2A >`              |
| `[ ]`    | Decorativo / container          | `[ SECTOR_7G ]`               |

---

## Truco: Texto Glitch con CSS Puro

Para titulares hero, este efecto crea un glitch memorable:

```css
/* Wrapper con data-attribute para el texto */
.glitch-text {
  position: relative;
  font-family: var(--font-display);
  font-size: var(--text-4xl);
  font-weight: 800;
  letter-spacing: 0.15em;
  text-transform: uppercase;
}

/* Capa de glitch con pseudoelementos */
.glitch-text::before,
.glitch-text::after {
  content: attr(data-text);
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
}

.glitch-text::before {
  color: var(--accent-primary);
  animation: glitch-shift-1 3s infinite linear alternate-reverse;
  clip-path: polygon(0 0, 100% 0, 100% 35%, 0 35%);
  transform: translate(-2px, -1px);
}

.glitch-text::after {
  color: var(--accent-secondary);
  animation: glitch-shift-2 2.5s infinite linear alternate-reverse;
  clip-path: polygon(0 65%, 100% 65%, 100% 100%, 0 100%);
  transform: translate(2px, 1px);
}

@keyframes glitch-shift-1 {
  0%, 90% { transform: translate(0); }
  91% { transform: translate(-3px, 1px); }
  93% { transform: translate(2px, -1px); }
  95% { transform: translate(-1px, 2px); }
  97% { transform: translate(1px, -2px); }
  100% { transform: translate(0); }
}

@keyframes glitch-shift-2 {
  0%, 88% { transform: translate(0); }
  89% { transform: translate(3px, -1px); }
  92% { transform: translate(-2px, 1px); }
  95% { transform: translate(1px, -2px); }
  98% { transform: translate(-1px, 1px); }
  100% { transform: translate(0); }
}
```

```html
<h1 class="glitch-text" data-text="GATEWAY_TERMINAL">GATEWAY_TERMINAL</h1>
```

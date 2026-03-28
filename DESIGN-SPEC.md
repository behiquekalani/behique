# Behique Hub v3 — Design Spec
> Source: Ceiba (task-1773945848629-x3e2)

## Fonts
- **Body:** DotGothic16 (Google Fonts, monospace)
- **Headings:** UnifrakturMaguntia (Google Fonts, serif)

## Themes (CSS Variables)

### NEON (default)
- Text: `#00e88f` (green)
- Background: `#0a0c10` (black)
- Accent: `#00e5ff` (cyan)
- Cards: `#111620`

### MONO
- Text: `#cccccc` (grayscale)
- Background: `#080808`
- No glow effects

### VIVID
- Primary: `#00e5ff` (cyan)
- Secondary: `#ff0080` (magenta)
- Background: `#0a0014` (deep purple)

## Components
- Cards: dark bg, 1px rgba border, 6px border-radius, glitch hover effect
- VHS scanline overlay on `body::after`
- Quest/RPG style: XP bars, level badges, progress rings
- Mission cards with LEGEND/EPIC/HARD tags
- Navigation: sticky top bar, tab buttons, glow underline on active
- Grid layout: 3 columns for mission cards
- Status dots: online/offline indicators

## Rules
- No warm colors
- No marketplace look
- Everything dark, minimal, pixel-game aesthetic

## Reference
`~/behique/Ceiba/unified-hub.html`

---
title: "Ceiba Design System"
type: pattern
tags: [design, ui, aesthetic, standard]
created: 2026-03-17
relates_to_project: [Quest-Dashboard, Ceiba-HQ]
follows_pattern: [ceiba-design-system]
---

# Ceiba Design System v1.0
## The definitive Behique visual language

> "quest dashboard v3.0 looks so clean i want things to look like this the colors the style everything" — Kalani, 2026-03-17

---

## Color Palette

| Token | Value | Usage |
|-------|-------|-------|
| `--bg` | `#0a0c10` | Page background (near-black) |
| `--panel` | `#13161d` | Card/panel background |
| `--panel-hover` | `#1a1e28` | Hover state |
| `--border` | `#1e2330` | Default borders |
| `--border-bright` | `#2a3040` | Active/hover borders |
| `--green` | `#00ff6a` | Ceiba signature — active, online, success |
| `--green-dim` | `rgba(0,255,106,0.15)` | Green background tint |
| `--green-glow` | `rgba(0,255,106,0.6)` | Green glow/shadow |
| `--gold` | `#ffd700` | Completed, rewards, achievements |
| `--gold-dim` | `rgba(255,215,0,0.12)` | Gold background tint |
| `--amber` | `#ff9f1c` | Warnings, rewards text |
| `--cyan` | `#00e5ff` | Accent, headings, active tabs |
| `--cyan-dim` | `rgba(0,229,255,0.1)` | Cyan background tint |
| `--red` | `#ff3b3b` | Blockers, offline, errors, $0 |
| `--red-dim` | `rgba(255,59,59,0.12)` | Red background tint |
| `--purple` | `#b44dff` | Accountability, check-ins, bots |
| `--gray` | `#4a5060` | Locked, disabled |
| `--text` | `#d0d4dc` | Body text |
| `--text-dim` | `#6a7080` | Secondary text, labels |

## Typography

| Element | Font | Size | Notes |
|---------|------|------|-------|
| Headings | `'Press Start 2P', monospace` | 8-22px | Pixel font, letter-spacing: 2px |
| Body | `'VT323', monospace` | 1.2-1.5rem | Terminal font, line-height: 1.5 |
| Labels | Press Start 2P | 7-9px | Uppercase, letter-spacing: 1-2px |
| Stats | VT323 | 1.3rem | Monospace alignment |

Google Fonts import:
```html
<link href="https://fonts.googleapis.com/css2?family=Press+Start+2P&family=VT323&display=swap" rel="stylesheet">
```

## Panel Pattern

Every panel/card follows this structure:
- `border: 2px solid var(--border)`
- `background: var(--panel)`
- `padding: 16-20px`
- `position: relative` (for label)
- Floating label: `position: absolute; top: -10px; left: 14px; background: var(--panel); padding: 0 8px`
- Label font: Press Start 2P, 9px, letter-spacing: 2px
- Label color matches panel purpose (cyan for player, green for Ceiba, red for blockers, etc.)

## Status Indicators

- **Online**: green dot with `box-shadow: 0 0 8px var(--green-glow)` + pulse animation
- **Offline**: red dot with `box-shadow: 0 0 8px var(--red-dim)`
- **Degraded**: amber dot
- **Unknown**: gray dot

## Animations

- Scanline overlay: `repeating-linear-gradient(0deg, transparent 0 2px, rgba(0,0,0,0.06) 2px 4px)`
- Badge pulse: `box-shadow` oscillating between dim and glow
- Status pulse: opacity 0.4 → 0.8
- Progress bars: `transition: width 1.8s cubic-bezier(0.25, 0.46, 0.45, 0.94)`
- XP bars: green gradient with inset shadow

## Layout Rules

- Max width: 960px main content
- Sidebar: 320px fixed, sticky
- Mobile breakpoint: 900px (stack vertically)
- Small mobile: 500px
- Tab bar: bottom border 2px, active tab = cyan with text-shadow glow
- Gap between panels: 20px

## Key Principles

1. **Dark base** — nearly black, not gray
2. **Neon accents** — green/cyan/gold glow on dark, never flat colors
3. **Terminal feel** — monospace everything, scanlines, grid patterns
4. **Labeled panels** — every section has a floating label in its accent color
5. **Status is visible** — green = good, red = bad, amber = warning, always with glow
6. **No rounded corners** — sharp edges, 2px borders, pixel-perfect
7. **Animations are subtle** — pulse, glow, transitions. Never bouncy or playful.
8. **Data-dense** — show stats, numbers, real data. Not decorative filler.

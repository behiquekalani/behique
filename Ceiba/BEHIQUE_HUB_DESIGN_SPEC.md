# Behique Hub v3 Design Specification

## For: All machines (Cobo, Hutia, any future contributor)

## Design Philosophy
Clean, professional, minimal. Not flashy, not decorative. Functional first.
Think: dark IDE meets mission control. No warm earthy tones. No marketplace vibes.

## Color Palette

### Light Mode (primary)
| Token | Hex | Use |
|-------|-----|-----|
| Background | #f0f4f8 | Page/app background |
| Surface | #e2e8f0 | Cards, panels, containers |
| Accent Blue | #3070b0 | Primary actions, active states |
| Accent Teal | #2a8f7a | Success, online indicators |
| Text Primary | #1a2030 | Headings, body text |
| Text Secondary | #506078 | Labels, descriptions, muted text |
| Border | #b0c4d8 | Dividers, card borders |
| Highlight | #b8d8e8 | Hover states, selections |

### Dark Mode
| Token | Hex | Use |
|-------|-----|-----|
| Background | #0c1018 | Page/app background |
| Surface | #0a0e16 | Cards, panels |
| Accent Blue | #2a4878 | Primary actions |
| Accent Teal | #1a6858 | Success states |
| Text Primary | #c8d0e0 | Body text |
| Text Secondary | #7888a8 | Muted text |
| Border | #10141c | Dividers |
| Highlight | #0e1828 | Hover/selections |

### Department Colors
Each project department has a unique accent color:

| Department | Light Accent | Dark Accent | Icon |
|-----------|-------------|-------------|------|
| eBay Reselling | #e53e3e | #b83030 | box emoji |
| BehiqueBot | #3b82f6 | #2a60c0 | robot emoji |
| Ceiba System | #22c55e | #1a9048 | tree emoji |
| Content Pipeline | #8b5cf6 | #6a40c0 | film emoji |
| Infrastructure | #f59e0b | #c07a08 | wrench emoji |

## Typography
- Headings: System sans-serif (Inter if available, otherwise -apple-system, Segoe UI)
- Body: Same stack, regular weight
- Monospace: JetBrains Mono, SF Mono, Menlo for code/data
- Sizes: 14px base, 12px small/labels, 16px subheadings, 20px headings
- No decorative fonts. No serifs.

## Component Style Rules
1. Cards: Rounded corners (8px), subtle border, no heavy shadows
2. Buttons: Filled for primary, outlined for secondary, ghost for tertiary
3. Status indicators: Small colored dots (8px), not badges
4. Progress bars: Thin (4px height), rounded, accent color fill
5. Tables: Minimal borders, alternating row backgrounds
6. Icons: Emoji for departments, simple SVG for actions
7. Spacing: 8px grid system (8, 16, 24, 32, 48)

## Layout Principles
- Left sidebar for navigation (collapsible)
- Main content area fills remaining space
- Cards for grouping related info
- No unnecessary whitespace, but not cramped
- Mobile: stack vertically, hide sidebar behind hamburger

## What to Avoid
- Warm earthy tones (that was the marketplace)
- Gradients (keep flat)
- Rounded everything (only cards and buttons get border-radius)
- Heavy drop shadows
- Decorative elements that serve no function
- Bright/neon colors
- Any marketplace or shopping visual language

## Status Colors
- Online/Success: #22c55e (light), #1a9048 (dark)
- Offline/Error: #e53e3e (light), #b83030 (dark)
- Warning/Pending: #f59e0b (light), #c07a08 (dark)
- Info/Neutral: #3b82f6 (light), #2a60c0 (dark)

## Reference
This spec matches the Behique Hub v3 theme defined in:
- `~/behique-hub/src/components/office-view/themes-locale.ts`
- PixiJS pixel art canvas uses these same hex values

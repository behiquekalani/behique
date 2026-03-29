---
name: Blueprint CSS Standard
type: pattern
use_when: "building any blueprint or guide product PDF"
last_verified: 2026-03-28
---

# Blueprint CSS Standard

## Core Variables
```css
:root {
  --bg: #0a0a0a;
  --surface: #111111;
  --border: #1a1a1a;
  --text: #e0e0e0;
  --text-dim: #888888;
  --accent: #00e5ff;
  --accent-dim: rgba(0, 229, 255, 0.1);
  --danger: #ff4444;
  --success: #00c853;
  --warning: #ffd600;
}
```

## Page Setup
```css
@page {
  size: letter;
  margin: 0.6in 0.75in;
}

body {
  font-family: 'Inter', -apple-system, sans-serif;
  background: var(--bg);
  color: var(--text);
  font-size: 10pt;
  line-height: 1.5;
}
```

## Print Rules (CRITICAL)
```css
@media print {
  color-adjust: exact;
  -webkit-print-color-adjust: exact;
  /* DO NOT add background: #fff here. EVER. */
}
```

## Section Headers
```css
.section-header {
  font-size: 14pt;
  font-weight: 700;
  color: var(--accent);
  border-bottom: 2px solid var(--accent);
  padding-bottom: 4px;
  margin-top: 24px;
  margin-bottom: 12px;
}
```

## Fill-in Fields
```css
.fill-line {
  border-bottom: 1px solid var(--border);
  min-height: 20px;
  margin: 4px 0;
  padding: 2px 4px;
}
```

## Module Grid
```css
.module-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
}

.module-card {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: 6px;
  padding: 12px;
}
```

## Header Bar
- Reduced padding (8px 16px, not 20px 30px)
- Logo left, title center or right
- Thin cyan bottom border

## Key Rules
1. Dark theme ONLY. No light variants.
2. Print CSS: ONLY `color-adjust: exact`. NO `background: #fff`.
3. Render with `--force-device-scale-factor=2` for 2x Retina.
4. Font size 10pt for body, 14pt for headers.
5. Inter font family with system fallbacks.

---
name: Product Thumbnail Template
type: pattern
use_when: "creating a thumbnail for any Gumroad product"
last_verified: 2026-03-28
---

# Thumbnail Template (600x600)

## Style: Clean Typography
- Just title + cyan line + BEHIKE brand
- No module lists
- No borders
- No images
- Minimal and bold

## HTML Shell
```html
<!DOCTYPE html>
<html>
<head>
<style>
  * { margin: 0; padding: 0; box-sizing: border-box; }
  body {
    width: 600px;
    height: 600px;
    background: #0a0a0a;
    color: #fff;
    font-family: 'Inter', sans-serif;
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    text-align: center;
    padding: 60px;
    overflow: hidden;
  }
  .title {
    font-size: 32px;
    font-weight: 800;
    line-height: 1.2;
    margin-bottom: 16px;
  }
  .cyan-line {
    width: 60px;
    height: 3px;
    background: #00e5ff;
    margin-bottom: 24px;
  }
  .brand {
    font-size: 11px;
    color: #444;
    letter-spacing: 4px;
    text-transform: uppercase;
  }
</style>
</head>
<body>
  <div class="title">PRODUCT<br>TITLE</div>
  <div class="cyan-line"></div>
  <div class="brand">BEHIKE</div>
</body>
</html>
```

## Rules
1. Size: exactly 600x600px
2. NO prices
3. NO module lists (covers have those)
4. NO borders or decorative elements
5. Clean, centered, typographic only
6. Render with Brave `--force-device-scale-factor=2`
7. Title should be 2-3 words max per line (use `<br>`)

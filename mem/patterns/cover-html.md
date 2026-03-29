---
name: Product Cover Template
type: pattern
use_when: "creating a cover image for any Gumroad product"
last_verified: 2026-03-28
---

# Cover Image Template (1280x720)

## Structure
```
+------------------------------------------+
|                                          |
|   "Pain point quote in quotes"           |
|                                          |
|   ~~Strikethrough pain point 1~~         |
|   ~~Strikethrough pain point 2~~         |
|   ~~Strikethrough pain point 3~~         |
|                                          |
|   PRODUCT TITLE                          |
|   ─── cyan line ───                      |
|                                          |
|   Module 1  |  Module 2  |  Module 3     |
|   Module 4  |  Module 5  |  Module 6     |
|                                          |
|                           BEHIKE branding |
+------------------------------------------+
```

## HTML Shell
```html
<!DOCTYPE html>
<html>
<head>
<style>
  * { margin: 0; padding: 0; box-sizing: border-box; }
  body {
    width: 1280px;
    height: 720px;
    background: #0a0a0a;
    color: #e0e0e0;
    font-family: 'Inter', sans-serif;
    display: flex;
    flex-direction: column;
    justify-content: center;
    padding: 60px 80px;
    overflow: hidden;
  }
  .quote { font-size: 18px; color: #888; font-style: italic; margin-bottom: 20px; }
  .pain { text-decoration: line-through; color: #666; font-size: 16px; margin: 4px 0; }
  .title { font-size: 36px; font-weight: 800; color: #fff; margin: 20px 0 8px; }
  .cyan-line { width: 80px; height: 3px; background: #00e5ff; margin-bottom: 20px; }
  .modules { display: flex; flex-wrap: wrap; gap: 8px; }
  .mod { background: #111; border: 1px solid #1a1a1a; padding: 6px 14px; border-radius: 4px; font-size: 13px; color: #aaa; }
  .brand { position: absolute; bottom: 30px; right: 40px; font-size: 12px; color: #444; letter-spacing: 3px; }
</style>
</head>
<body>
  <div class="quote">"Pain point quote"</div>
  <div class="pain">~~Old way that doesn't work~~</div>
  <div class="pain">~~Another old way~~</div>
  <div class="pain">~~Third old way~~</div>
  <div class="title">PRODUCT TITLE</div>
  <div class="cyan-line"></div>
  <div class="modules">
    <span class="mod">Module 1</span>
    <span class="mod">Module 2</span>
    <!-- ... -->
  </div>
  <div class="brand">BEHIKE</div>
</body>
</html>
```

## Rules
1. Size: exactly 1280x720px
2. NO prices on covers (Gumroad shows the price)
3. Dark background (#0a0a0a)
4. Render with Brave `--force-device-scale-factor=2` for 2x quality
5. Quote + strikethrough pain points + modules format
6. BEHIKE brand bottom-right, subtle
7. Hormozi-style copy (pain → solution)

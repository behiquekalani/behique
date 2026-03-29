---
name: Product Folder Structure
type: pattern
use_when: "creating or verifying any product ready for Gumroad"
last_verified: 2026-03-28
---

# Product Folder Structure

Every product in `READY-TO-SELL/products-organized/` must contain exactly:

```
product-name/
  ├── product-name.pdf          # The actual product
  ├── cover.png                 # 1280x720 at 2x (2560x1440 actual)
  ├── thumbnail.png             # 600x600 at 2x (1200x1200 actual)
  └── GUMROAD_INFO.txt          # Listing copy (see gumroad-listing pattern)
```

## Checklist Before Listing
- [ ] PDF renders correctly (dark theme, all pages, no white backgrounds)
- [ ] Cover has quote + strikethrough + modules + BEHIKE brand
- [ ] Cover has NO price
- [ ] Thumbnail has title + cyan line + BEHIKE brand only
- [ ] Thumbnail has NO price, NO module list
- [ ] GUMROAD_INFO.txt has name, price, slug, description, summary, receipt
- [ ] All images are 2x Retina quality

## Folder Naming
- Lowercase, hyphenated: `ai-agency`, `first-dollar-guide`, `claude-code-builders`
- Match the Gumroad URL slug when possible
- Spanish variants add `-es` suffix: `ecommerce-es`, `freelancer-es`

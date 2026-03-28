# READY TO SELL - Product Inventory

All products in this folder have PDFs generated and are ready to upload to Gumroad.

## How to List on Gumroad
1. Go to gumroad.com -> Dashboard -> New Product
2. Upload the PDF file
3. Copy the title, description, and price from the listings doc below
4. Set the price
5. Publish

## Listings Copy (ready to paste)
See: `Ceiba/projects/content-empire/gumroad-all-products.md` for full Gumroad copy.
See: `Ceiba/projects/content-empire/GUMROAD_LISTINGS_FINAL.md` for final version.

## Products in This Folder (64 files)

### Paid Products ($9.99 - $29.99)
| File | Suggested Price |
|------|----------------|
| ai-employee-guide.pdf | $19.99 |
| ai-security-guide.pdf | $14.99 |
| prompt-engineering-cheat-sheet.pdf | $9.99 |
| ecommerce-playbook-v3.pdf | $14.99 |
| behike-method-v2.pdf | $14.99 |
| solopreneur-os.pdf | $14.99 |
| claude-code-course.pdf | $19.99 |
| content-franchise-kit.pdf | $14.99 |
| ai-chatbot-guide.pdf | $9.99 |
| amazon-fba-guide.pdf | $9.99 |
| ebay-dropshipping-guide.pdf | $9.99 |
| self-hosted-store-guide.pdf | $14.99 |
| ai-news-tracker-guide.pdf | $9.99 |
| social-media-pipeline-guide-v2.pdf | $9.99 |
| mastery-for-builders.pdf | $14.99 |
| content-waterfall.pdf | $9.99 |
| ghost-writer-kit.pdf | $19.99 |
| n8n-automation-pack.pdf | $29.99 |
| n8n-solopreneur-guide.pdf | $14.99 |
| roblox-builders-guide.pdf | $9.99 |
| 3d-fashion-guide.pdf | $9.99 |
| reel-factory-system.pdf | $14.99 |
| ai-copywriting-playbook.pdf | $9.99 |
| ai-writing-workflows.pdf | $9.99 |
| ai-content-machine-kit.pdf | $14.99 |
| niche-sniper-guide.pdf | $9.99 |
| polymarket-strategy-guide.pdf | $14.99 |
| fl-studio-ai-guide.pdf | $9.99 |
| ai-agent-installer-kit.pdf | $19.99 |
| adhd-budget-guide.pdf | $9.99 |
| adhd-finance-guide.pdf | $9.99 |
| freelance-client-acquisition.pdf | $14.99 |
| email-list-accelerator.pdf | $9.99 |
| linkedin-growth-playbook.pdf | $14.99 |
| gumroad-sellers-playbook.pdf | $9.99 |
| digital-product-pricing-guide.pdf | $9.99 |
| telegram-bot-for-business.pdf | $14.99 |
| youtube-channel-blueprint.pdf | $14.99 |
| youtube-monetization-guide.pdf | $14.99 |
| zero-to-first-sale.pdf | $9.99 |
| creators-revenue-blueprint.pdf | $9.99 |
| affiliate-marketing-blueprint.pdf | $9.99 |
| personal-brand-blueprint.pdf | $14.99 |
| faceless-creator-blueprint.pdf | $14.99 |
| solopreneur-second-brain.pdf | $14.99 |
| ai-tutor-guide.pdf | $9.99 |
| behike-method-content-system.pdf | $14.99 |
| solopreneur-os-live-guide.pdf | $14.99 |
| Personal-Budget-Template.xlsx | $9.99 |
| Cash Flow Dashboard.xlsx | $14.99 |
| landing-page-template.zip | $19.99 |

### Free Lead Magnets ($0)
| File | Purpose |
|------|---------|
| 5-ai-tools-lead-magnet.pdf | Email list builder |
| 7-ai-tools-that-replaced-my-team.pdf | Email list builder |
| ai-safety-checklist.pdf | Fear funnel entry |
| business-automation-audit.pdf | Service funnel entry |
| zero-dollar-ai-stack.pdf | Email list builder |

### Ghost Writer Kit Bundle Components
| File | Part of $19.99 bundle |
|------|----------------------|
| 10-voice-prompt-templates.pdf | Included |
| corpus-ingestion-guide.pdf | Included |
| voice-audit-checklist.pdf | Included |
| voice-bible-template.pdf | Included |

## Security Audit Status
- Sprint audit: PASS (24 low-priority copyright flags, all false positives)
- PII scan: See findings below
- No API keys, tokens, or passwords in any product file
- No Yamilet references in any product
- Local IPs (192.168.x.x) found in AI Employee Guide (used as examples in the tutorial)

## PII Findings in Products

### SAFE (intentional, public-facing author credit)
- "Kalani" as author name in product headers -- THIS IS INTENTIONAL for branding
- @kalaniandrez and @behikeai social handles -- PUBLIC, intentional
- "Kalani Andre Gomez Padin" in author bylines -- your public pen name
- "Puerto Rico" location references -- public, part of brand story

### NEEDS REVIEW
- `ai-employee-guide.md` contains local IP addresses (192.168.0.x) as tutorial examples
- `n8n-automation-pack/` JSON workflows contain "Kalani" in email signatures and Telegram alert names
- `gumroad-sellers-playbook.md` has full name "Kalani Andre Gomez Padin"
- `10-day-ai-business-challenge.md` contains a local file path `/Users/kalani/behique/`

### CLEAN (no personal info)
- No Yamilet references in any sellable product
- No phone numbers, SSNs, or credit card numbers anywhere
- No real email addresses (kalani1337@gmail.com) in products
- No geolocation/GPS data
- Deploy script has local paths but is not a sellable product

## Files NOT in This Folder (not ready to sell)
- Spanish products (need separate listing strategy)
- Interactive HTML products (need hosting, not PDF-sellable)
- Markdown source files (kept in original location)
- Products without PDF versions yet

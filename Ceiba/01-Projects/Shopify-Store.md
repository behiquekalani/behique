---
type: project
status: waiting
tools:
  - TOOL_Listing_Pipeline
systems:
  - SYS_AI_Cluster
patterns:
  - PAT_Sequence_Matters
decisions:
  - DEC_Ebay_Before_Shopify
tags: [project, ecommerce, revenue]
---

# Shopify Store
**Status:** ⏸ Waiting for products
**Priority:** Medium — feeds from eBay
**Cost:** Monthly subscription active (paid, needs to generate revenue)

---

## What It Is
Shopify store — logo done, setup done, no sales yet.
**Brand name:** Merchoo (Clothes Shop)
Strategy: use eBay as the testing ground. Products that sell well on eBay → migrate to Shopify for higher margins and brand building.

## Brand Assets
- **Logo:** Starfish design with "MERCHOO — CLOTHES SHOP" text
- **Color variants:** Cyan (turquoise), Pink, Brown
- **Logo location (Cobo):** `C:\Users\kalan\Desktop\Kalani-Business\Dropshipping\MERCHOO\logo`
- **Status:** Logo finalized, 3 color variants ready
- **TODO:** Copy logos to Ceiba assets once Cobo is back online

## Why eBay First
eBay has built-in traffic. No marketing needed to validate a product.
Shopify needs marketing. Only add products that are already proven.

## The Pipeline
```
Google Trends → eBay listing → product sells → migrate to Shopify → scale with ads
```

## When to Activate
- [ ] At least 3 products with consistent eBay sales
- [ ] eBay Listing Assistant is live and running
- [ ] Google Trends Scraper feeding product ideas

## Future Automation
- n8n workflow: eBay sale threshold hit → auto-create Shopify product page
- Price sync between eBay and Shopify
- Inventory alerts when stock gets low

## Uses Tools
- [[TOOL_Listing_Pipeline]] — auto-migrate eBay winners

## Related Projects
- [[eBay-Listing-Assistant]] — primary feeder
- [[Google-Trends-Scraper]] — product research engine
- [[02-Goals/Q3-2026]] — Month 3 target: Shopify live with proven products

## Key Decisions
- [[DEC_Ebay_Before_Shopify]] — don't activate until 3+ products proven on eBay

---

*Don't touch this until eBay is generating sales. Sequence matters.*

---
title: "Gumroad Upload Guide V2"
type: guide
tags: [gumroad, products, listing, revenue]
created: 2026-03-22
---

# Gumroad Upload Guide V2 -- Complete Product Listing Checklist

All products ready. All copy written. Follow this guide to list everything.

---

## PRODUCT LISTING ORDER (recommended)

List in this order. Start with the free lead magnets to build an email list, then add paid products.

| # | Product | Price | File Location | Status |
|---|---------|-------|---------------|--------|
| 1 | 5 AI Tools That Replaced My Team | FREE | products/free/5-ai-tools-lead-magnet.pdf | READY |
| 2 | AI Safety Checklist | FREE | products/free/ai-safety-checklist.pdf | READY |
| 3 | Business Automation Audit | FREE | products/free/business-automation-audit.pdf | READY |
| 4 | The $0 AI Stack Checklist | FREE | products/free/zero-dollar-ai-stack.pdf | READY |
| 5 | Personal Budget Template | $9.99 | products/Personal-Budget-Template.xlsx | Upload directly |
| 6 | AI Prompt Engineering Cheat Sheet | $9.99 | products/prompt-engineering-cheat-sheet.pdf | READY |
| 7 | Roblox Builder's Guide | $9.99 | products/roblox-builders-guide.pdf | READY |
| 8 | ADHD Budget Playbook | $9.99 | products/adhd-budget-guide.pdf | READY |
| 9 | Behike Method v2 | $9.99 | products/behike-method-v2.pdf | READY |
| 10 | Solopreneur OS | $12.99 | products/solopreneur-os.pdf | READY |
| 11 | AI Security Guide | $14.99 | products/ai-security-guide.pdf | READY |
| 12 | Ecommerce Playbook | $14.99 | products/ecommerce-playbook.pdf | READY |
| 13 | Cash Flow Dashboard | $14.99 | Cash Flow Dashboard.xlsx | Upload directly |
| 14 | 3D Fashion Design Guide | $9.99 | products/3d-fashion-guide.pdf | READY |
| 15 | Self-Hosted Store Guide | $4.99 | products/self-hosted-store-guide.pdf | READY |
| 16 | Social Media Pipeline Guide | $9.99 | products/social-media-pipeline-guide.pdf | READY |
| 17 | AI News Tracker Guide | $9.99 | products/ai-news-tracker-guide.pdf | READY |
| 18 | AI Employee Guide | $19.99 | products/ai-employee-guide.pdf | READY |
| 19 | Focus DJ (Lifetime) | $29.99 | themes/behike-store/landing-pages/focus-dj.html | Upload HTML |
| 20 | Ceiba Sanctuary (Lifetime) | $49.99 | themes/behike-store/landing-pages/ceiba-sanctuary.html | Upload HTML |

---

## HOW TO LIST EACH PRODUCT

### Step 1: Go to gumroad.com/products/new

### Step 2: For Each Product, Fill In:

**Name:** [Product name from table above]

**Price:** [Price from table above]

**Description:** Copy from `product-listings.md` (the Description section for each product)

**Cover image:** Create in Canva using briefs from `product-cover-designs.md`

**File:** Upload the product file (PDF, XLSX, or HTML)

**Tags:** Add relevant tags (ai, automation, business, productivity, budget, ecommerce)

### Step 3: Publish

Click "Publish" to make it live.

---

## PDF CONVERSION

For markdown products, convert to PDF before uploading:

```bash
# If md_to_pdf.py exists:
python3 tools/md_to_pdf.py [input.md] [output.pdf]

# Alternative with pandoc (if installed):
pandoc input.md -o output.pdf

# Alternative with Python fpdf2:
pip3 install fpdf2
python3 -c "
from fpdf import FPDF
# See tools/md_to_pdf.py for full implementation
"
```

### Conversion checklist (ALL COMPLETE as of 2026-03-22):
- [x] 5-ai-tools-lead-magnet.pdf -- DONE
- [x] zero-dollar-ai-stack.pdf -- DONE
- [x] business-automation-audit.pdf -- DONE
- [x] ai-safety-checklist.pdf -- DONE
- [x] prompt-engineering-cheat-sheet.pdf -- DONE
- [x] ai-employee-guide.pdf -- DONE
- [x] ecommerce-playbook.pdf -- DONE (13,093 word original rewrite)
- [x] adhd-budget-guide.pdf -- DONE
- [x] roblox-builders-guide.pdf -- DONE
- [x] 3d-fashion-guide.pdf -- DONE
- [x] self-hosted-store-guide.pdf -- DONE
- [x] social-media-pipeline-guide.pdf -- DONE
- [x] ai-news-tracker-guide.pdf -- DONE
- [x] solopreneur-os.pdf -- DONE
- [x] behike-method-v2.pdf -- DONE
- [x] ai-security-guide.pdf -- DONE

---

## GUMROAD STOREFRONT SETTINGS

### Profile
- **Display name:** Behike
- **Bio:** AI tools, automation guides, and digital products for builders. Built by a computer engineering student in Puerto Rico.
- **Profile picture:** Use Behike logo (create in Canva if needed)

### Custom URL
- Aim for: gumroad.com/behike or behike.gumroad.com

### Categories to Set Up
1. Free Resources (lead magnets)
2. Templates & Tools (budget, cash flow)
3. Guides & Playbooks (ebook, AI employee guide, prompt cheat sheet)

---

## AFTER LISTING: EMAIL COLLECTION SETUP

Free products on Gumroad automatically collect email addresses. These feed into:
1. The email welcome sequence (see email-welcome-sequence.md)
2. Future product launches
3. Service inquiries

Set up email integration:
- Gumroad has built-in email (basic)
- For better sequences: connect to ConvertKit, Mailchimp, or Buttondown (all have free tiers)
- n8n can automate this: Gumroad webhook -> email tool

---

## LAUNCH CHECKLIST

- [ ] All 20 products listed on Gumroad (all files ready)
- [ ] Cover images created in Canva for each product
- [ ] Instagram bio updated with Gumroad link
- [ ] First Instagram post from batch 3 (product launch carousel)
- [ ] First X/Twitter thread posted
- [ ] Email welcome sequence connected
- [ ] Test purchase on one free product to verify download flow

---

## REVENUE PROJECTIONS (conservative)

| Product | Monthly units (low) | Price | Monthly revenue |
|---------|-------------------|-------|-----------------|
| Free lead magnets x3 | 50 downloads | $0 | $0 (but 50 email leads) |
| Budget Template | 5 | $9.99 | $49.95 |
| Prompt Cheat Sheet | 8 | $9.99 | $79.92 |
| Ecommerce Playbook | 3 | $14.99 | $44.97 |
| Cash Flow Dashboard | 3 | $14.99 | $44.97 |
| Meditation Premium | 5 | $4.99 | $24.95 |
| AI Employee Guide | 5 | $19.99 | $99.95 |
| **Total** | **79** | | **$344.71/mo** |

With service clients added:
- 1 Quick Win client/month: + $497
- **Total with 1 service client: $841.71/mo**

This is conservative. With consistent content + growing audience, these numbers compound.

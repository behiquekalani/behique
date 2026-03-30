---
name: Local Business Website Template
type: pattern
use_when: "building a website for any local business in Puerto Rico"
last_verified: 2026-03-30
---

# Local Business Website Pattern

## Standard Sections (in order)
1. **Nav** - logo, 4-5 links, CTA button (call or book), mobile hamburger
2. **Hero** - headline with pain/emotion, subtext, 2 CTAs (call + WhatsApp), trust badges
3. **Pain Points** - 3 cards addressing customer fears/worries (Hormozi style)
4. **Story/About** - real story of the business, founder, why they started
5. **Services** - 2-column grid, icon + name + description per card
6. **Expansion/News** - if applicable (new location, new service)
7. **Gallery** - 3-column grid with photos (tall item for featured)
8. **Testimonials** - 3 cards with stars, quote, name
9. **Contact** - 2-column: info left, form right
10. **Footer** - logo, links, copyright, "Hecho por Behike"

## Standard Tech Stack
- Single HTML file (no build tools, no framework)
- Google Fonts (2 fonts max: display + body)
- CSS variables for easy theming
- IntersectionObserver for scroll animations
- JSON-LD schema markup for Google
- OG + Twitter meta tags
- Mobile-first responsive (768px breakpoint)

## Standard Deployment
- Hosted on Naboria (nginx)
- Subdomain: `clientname.behike.store`
- Deploy script: `deploy.sh` with rsync + nginx config
- SSL via Let's Encrypt (certbot)

## Color Palettes by Industry

### Barbershop / Salon
- Dark: #0a0a0a, Accent: #c8ff00 (neon green), Surface: #111

### Elderly Care / Medical
- Light: #f8f5f0, Accent: #2d6a4f (forest green), Warm: #d4a373

### Restaurant / Food
- Dark: #1a1a1a, Accent: #e07a5f (terracotta), Warm: #f4e285

### Auto / Mechanic
- Dark: #0f0f0f, Accent: #ef4444 (red), Surface: #1a1a1a

### Professional Services (Law, Accounting)
- Light: #fafafa, Accent: #1e3a5f (navy), Surface: #ffffff

## Standard Deliverables Per Client
1. `index.html` - the website
2. `images/` - all photos
3. `deploy/nginx.conf` - server config
4. `deploy/deploy.sh` - deployment script
5. `DIGITAL_PRESENCE_KIT.md` - Google Business, SEO, social, job postings

## Pricing Model
- First client per vertical: FREE (portfolio piece)
- Subsequent clients: $300 setup + $100/month maintenance
- With AI compliance SaaS (hogares): $500-1000/month
- With creative flooding ads: +$500/month

## Build Time Target
- Website: 1-2 hours
- Digital presence kit: 30 minutes
- Deployment: 15 minutes
- Total per client: under 3 hours

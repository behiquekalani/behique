#!/usr/bin/env python3
"""
Batch Product Prep - Create GUMROAD_INFO.txt, cover.html, thumbnail.html
for products that have PDFs but aren't in products-organized/ yet.
"""

import os
import shutil
from pathlib import Path

REPO = Path(os.path.expanduser("~/behique"))
PRODUCTS_SRC = REPO / "Ceiba/projects/content-empire/products"
PRODUCTS_DST = REPO / "READY-TO-SELL/products-organized"
COVERS_DIR = REPO / "READY-TO-SELL/product-covers"

# Products to prep: name, slug, price, tags, description, summary, receipt, pages
PRODUCTS = [
    {
        "name": "Roblox Builder's Guide",
        "slug": "roblox-guide",
        "pdf": "roblox-builders-guide.pdf",
        "price": "$9.99",
        "pages": 16,
        "tags": "roblox, game development, lua, coding, builders",
        "desc": "5 chapters. Roblox Studio, Lua scripting, UI design, game mechanics, monetization. Everything you need to build and sell games on Roblox.\n\nNot theory. Step-by-step with code examples you can copy.\n\nWhether you're 14 or 40, if you want to make money on Roblox, this is the guide.\n\nPDF format. 16 pages. No fluff.",
        "summary": "1 PDF guide (16 pages, 5 chapters)\nRoblox Studio setup + Lua scripting\nGame mechanics + UI design\nMonetization strategies",
        "receipt": "Welcome to Behike. Time to build your first Roblox game. behike.gumroad.com"
    },
    {
        "name": "3D Fashion Design Guide",
        "slug": "3d-fashion",
        "pdf": "3d-fashion-guide.pdf",
        "price": "$9.99",
        "pages": 14,
        "tags": "3D design, fashion, marvelous designer, zbrush, game assets",
        "desc": "5 chapters. Marvelous Designer, ZBrush, retopology, texturing for game-ready fashion assets.\n\nBuild clothes for Roblox, VTubers, games, or your own fashion brand. From concept to export.\n\nPDF format. 14 pages. No fluff.",
        "summary": "1 PDF guide (14 pages, 5 chapters)\nMarvelous Designer workflow\nZBrush sculpting\nGame-ready asset export",
        "receipt": "Welcome to Behike. Start designing. behike.gumroad.com"
    },
    {
        "name": "Self-Hosted Store Guide",
        "slug": "self-hosted-store",
        "pdf": "self-hosted-store-guide.pdf",
        "price": "$4.99",
        "pages": 12,
        "tags": "self-hosted, store, ecommerce, free hosting, digital products",
        "desc": "You're paying $29/month for Shopify to sell digital products. That's $348/year. For what?\n\nThis guide shows you how to build a product store for $0/month. HTML landing pages + Gumroad for payments + free hosting.\n\nI built my entire store this way. It works.\n\nPDF format. 12 pages. Save $348/year.",
        "summary": "1 PDF guide (12 pages)\nHTML landing page templates\nGumroad payment integration\nFree hosting setup (GitHub Pages/Cloudflare)",
        "receipt": "Welcome to Behike. Stop paying for Shopify. behike.gumroad.com"
    },
    {
        "name": "Social Media Pipeline Guide",
        "slug": "social-pipeline",
        "pdf": "social-media-pipeline-guide.pdf",
        "price": "$4.99",
        "pages": 11,
        "tags": "social media, automation, instagram, content, pipeline",
        "desc": "Turn RSS feeds into Instagram posts. Automatically.\n\nPython scripts, OPB templates, carousel generators, hashtag automation. Build once, post forever.\n\nPDF format. 11 pages.",
        "summary": "1 PDF guide (11 pages)\nRSS-to-Instagram automation\nCarousel generator templates\nHashtag automation system",
        "receipt": "Welcome to Behike. Automate your content. behike.gumroad.com"
    },
    {
        "name": "AI News Tracker Guide",
        "slug": "ai-news-tracker",
        "pdf": "ai-news-tracker-guide.pdf",
        "price": "$4.99",
        "pages": 9,
        "tags": "AI, news, tracker, python, automation, RSS",
        "desc": "18 RSS feeds. Impact scoring. Entity tracking. HTML digests. All in Python.\n\nBuild your own AI-powered news tracker that finds the stories that matter.\n\nPDF format. 9 pages.",
        "summary": "1 PDF guide (9 pages)\n18 RSS feed sources\nImpact scoring system\nEntity tracking + HTML digests",
        "receipt": "Welcome to Behike. Stay ahead of the news. behike.gumroad.com"
    },
    {
        "name": "Solopreneur Operating System",
        "slug": "solopreneur-os",
        "pdf": "solopreneur-os.pdf",
        "price": "$12.99",
        "pages": 36,
        "tags": "solopreneur, operating system, ADHD, business, productivity",
        "desc": "5 modules. 13 exercises. Vision Builder, Domain Stack, Content Engine, Monetization Map, Daily Operations.\n\nThis is the system I use to run an entire business with ADHD. Not a course. A workbook. Fill it in and build.\n\nPDF format. 36 pages. Built for brains that can't sit through 40-hour courses.",
        "summary": "1 PDF workbook (36 pages, 5 modules)\n13 fill-in exercises\nADHD-friendly format\nVision + Content + Monetization systems",
        "receipt": "Welcome to Behike. Your operating system is ready. Fill it in. behike.gumroad.com"
    },
    {
        "name": "Behike Method v2",
        "slug": "behike-method",
        "pdf": "behike-method-v2.pdf",
        "price": "$19.99",
        "pages": 34,
        "tags": "behike method, business, AI, ADHD, blueprint, system",
        "desc": "8 chapters. Vision Layer, Domain Stacking, ADHD Builder's Edge, Content Waterfall, AI Content Engine, Building in Public, Value Ladder, Ship It.\n\nThis is not another business book. It's the exact system I used to build 100+ products in 2 weeks with ADHD and Claude Code.\n\nPDF format. 34 pages. The flagship.",
        "summary": "1 PDF guide (34 pages, 8 chapters)\nThe Behike Method framework\nADHD Builder's Edge system\nContent Waterfall + Value Ladder",
        "receipt": "Welcome to Behike. The method is yours now. Build. behike.gumroad.com"
    },
    {
        "name": "AI Copywriting Playbook",
        "slug": "ai-copywriting",
        "pdf": "ai-copywriting-playbook.pdf",
        "price": "$9.99",
        "pages": 15,
        "tags": "copywriting, AI, marketing, sales, writing",
        "desc": "Write copy that sells using AI. Headlines, emails, product descriptions, social posts, ad copy.\n\nPrompt templates for every type of copy. Not generic outputs. Copy that sounds human and converts.\n\nPDF format. 15 pages.",
        "summary": "1 PDF playbook (15 pages)\nAI prompt templates for all copy types\nHeadline formulas\nEmail + ad copy frameworks",
        "receipt": "Welcome to Behike. Words make money. Use them. behike.gumroad.com"
    },
    {
        "name": "FL Studio AI Production Guide",
        "slug": "fl-studio-ai",
        "pdf": "fl-studio-ai-guide.pdf",
        "price": "$9.99",
        "pages": 17,
        "tags": "FL Studio, music production, AI, beats, producer",
        "desc": "Use AI to make beats in FL Studio. Sample generation, melody creation, mixing assistance, mastering workflow.\n\nFor producers who want to speed up their workflow without losing their sound.\n\nPDF format. 17 pages.",
        "summary": "1 PDF guide (17 pages)\nAI sample generation\nMelody + beat creation with AI\nMixing + mastering workflow",
        "receipt": "Welcome to Behike. Make beats faster. behike.gumroad.com"
    },
    {
        "name": "Niche Sniper Guide",
        "slug": "niche-sniper",
        "pdf": "niche-sniper-guide.pdf",
        "price": "$9.99",
        "pages": 11,
        "tags": "niche research, market research, business, products, validation",
        "desc": "Find profitable niches before everyone else. Research framework, validation checklist, competition analysis.\n\nStop guessing. Start with data.\n\nPDF format. 11 pages.",
        "summary": "1 PDF guide (11 pages)\nNiche research framework\nValidation checklist\nCompetition analysis template",
        "receipt": "Welcome to Behike. Find your niche. behike.gumroad.com"
    },
    {
        "name": "Prompt Engineering Cheat Sheet",
        "slug": "prompt-cheatsheet",
        "pdf": "prompt-engineering-cheat-sheet.pdf",
        "price": "$4.99",
        "pages": 18,
        "tags": "prompt engineering, AI, ChatGPT, Claude, cheat sheet",
        "desc": "Every prompt framework in one place. Chain of thought, few-shot, role-playing, system prompts, and more.\n\nPrint it. Pin it next to your monitor. Reference it every time you talk to AI.\n\n18 pages of pure utility.",
        "summary": "1 PDF cheat sheet (18 pages)\nAll major prompt frameworks\nCopy-paste templates\nPrint-friendly format",
        "receipt": "Welcome to Behike. Better prompts = better outputs. behike.gumroad.com"
    },
    {
        "name": "LinkedIn Growth Playbook",
        "slug": "linkedin-growth",
        "pdf": "linkedin-growth-playbook.pdf",
        "price": "$9.99",
        "pages": 15,
        "tags": "LinkedIn, growth, social media, networking, B2B",
        "desc": "Grow on LinkedIn without being cringe. Content strategy, profile optimization, connection system, engagement framework.\n\nFor builders and creators who want B2B visibility without the corporate buzzwords.\n\nPDF format. 15 pages.",
        "summary": "1 PDF playbook (15 pages)\nProfile optimization\nContent strategy framework\nConnection + engagement system",
        "receipt": "Welcome to Behike. Grow your LinkedIn. Not your cringe. behike.gumroad.com"
    },
    {
        "name": "Personal Brand Blueprint",
        "slug": "personal-brand",
        "pdf": "personal-brand-blueprint.pdf",
        "price": "$9.99",
        "pages": 20,
        "tags": "personal brand, branding, social media, creator, identity",
        "desc": "Build a personal brand that makes money. Not one that just gets likes.\n\nPositioning, content pillars, audience building, monetization. 20 pages.\n\nPDF format.",
        "summary": "1 PDF blueprint (20 pages)\nBrand positioning framework\nContent pillar system\nMonetization strategies",
        "receipt": "Welcome to Behike. Build your brand. behike.gumroad.com"
    },
    {
        "name": "Email List Accelerator",
        "slug": "email-list",
        "pdf": "email-list-accelerator.pdf",
        "price": "$9.99",
        "pages": 13,
        "tags": "email marketing, list building, newsletter, leads, automation",
        "desc": "Build an email list from zero. Lead magnets, opt-in pages, welcome sequences, monetization.\n\nThe list is the asset. Everything else is a channel.\n\n13 pages. No fluff.",
        "summary": "1 PDF guide (13 pages)\nLead magnet templates\nOpt-in page framework\nWelcome sequence blueprint",
        "receipt": "Welcome to Behike. Build the list. Own the audience. behike.gumroad.com"
    },
    {
        "name": "Faceless Creator Blueprint",
        "slug": "faceless-creator",
        "pdf": "faceless-creator-blueprint.pdf",
        "price": "$9.99",
        "pages": 13,
        "tags": "faceless, youtube, content, creator, anonymous, AI",
        "desc": "Build a content business without showing your face. AI voiceovers, stock footage, automated editing, faceless YouTube channels.\n\nFor introverts who want to create but don't want to be on camera.\n\n13 pages. Every step.",
        "summary": "1 PDF blueprint (13 pages)\nFaceless content creation workflow\nAI voiceover setup\nAutomated editing pipeline",
        "receipt": "Welcome to Behike. Create without showing your face. behike.gumroad.com"
    },
    {
        "name": "Gumroad Seller's Playbook",
        "slug": "gumroad-playbook",
        "pdf": "gumroad-sellers-playbook.pdf",
        "price": "$9.99",
        "pages": 22,
        "tags": "gumroad, selling, digital products, ecommerce, passive income",
        "desc": "Everything I learned selling on Gumroad. Product creation, pricing, descriptions, covers, SEO, promotions, analytics.\n\n22 pages of what actually works. Not what some guru said in a YouTube video.\n\nPDF format.",
        "summary": "1 PDF playbook (22 pages)\nProduct creation to listing\nPricing + description formulas\nGumroad SEO + promotions",
        "receipt": "Welcome to Behike. Start selling on Gumroad. behike.gumroad.com"
    },
    {
        "name": "Freelance Client Acquisition",
        "slug": "freelance-clients",
        "pdf": "freelance-client-acquisition.pdf",
        "price": "$9.99",
        "pages": 16,
        "tags": "freelance, clients, acquisition, sales, outreach",
        "desc": "Get freelance clients without cold DMs that make you feel gross.\n\nInbound strategy, portfolio positioning, pricing framework, proposal templates.\n\n16 pages. Built for freelancers who are good at the work but bad at selling it.",
        "summary": "1 PDF guide (16 pages)\nInbound client strategy\nPortfolio positioning\nProposal templates",
        "receipt": "Welcome to Behike. Get clients. Not anxiety. behike.gumroad.com"
    },
    {
        "name": "Amazon FBA Starter Guide",
        "slug": "amazon-fba",
        "pdf": "amazon-fba-guide.pdf",
        "price": "$9.99",
        "pages": 15,
        "tags": "amazon, FBA, ecommerce, product research, selling",
        "desc": "Start selling on Amazon FBA. Product research, supplier sourcing, listing optimization, PPC basics.\n\n15 pages. The starter guide, not the $997 course.\n\nPDF format.",
        "summary": "1 PDF guide (15 pages)\nProduct research framework\nSupplier sourcing\nListing optimization + PPC basics",
        "receipt": "Welcome to Behike. Start your Amazon business. behike.gumroad.com"
    },
    {
        "name": "Affiliate Marketing Blueprint",
        "slug": "affiliate-marketing",
        "pdf": "affiliate-marketing-blueprint.pdf",
        "price": "$9.99",
        "pages": 14,
        "tags": "affiliate marketing, passive income, commissions, marketing",
        "desc": "Make money recommending products you actually use. Niche selection, content strategy, link optimization, traffic.\n\n14 pages. No fake guru promises. Just the system.\n\nPDF format.",
        "summary": "1 PDF blueprint (14 pages)\nNiche selection framework\nContent + traffic strategy\nLink optimization",
        "receipt": "Welcome to Behike. Earn while you recommend. behike.gumroad.com"
    },
]

def create_product_folder(product):
    """Create a complete product folder ready for Gumroad."""
    slug = product["slug"]
    folder = PRODUCTS_DST / slug

    # Skip if already exists
    if folder.exists():
        print(f"  SKIP: {slug} (already exists)")
        return False

    folder.mkdir(parents=True, exist_ok=True)

    # Copy PDF
    src_pdf = PRODUCTS_SRC / product["pdf"]
    if src_pdf.exists():
        shutil.copy2(src_pdf, folder / product["pdf"])
    else:
        print(f"  WARN: PDF not found: {src_pdf}")

    # Create GUMROAD_INFO.txt
    info = f"""GUMROAD LISTING INFO
====================

Name: {product['name']}
Price: {product['price']}
URL slug: {slug}
Call to action: Buy this
Category: Self Improvement > Productivity
Tags: {product['tags']}
Receipt button: Download Guide

DESCRIPTION:
{product['desc']}

SUMMARY (You'll get...):
{product['summary']}

RECEIPT MESSAGE:
{product['receipt']}
"""
    (folder / "GUMROAD_INFO.txt").write_text(info)

    print(f"  DONE: {slug} ({product['pages']} pages, {product['price']})")
    return True


def main():
    print(f"\n{'='*50}")
    print(f"  BATCH PRODUCT PREP - {len(PRODUCTS)} products")
    print(f"{'='*50}\n")

    created = 0
    skipped = 0

    for product in PRODUCTS:
        if create_product_folder(product):
            created += 1
        else:
            skipped += 1

    print(f"\n  Created: {created}")
    print(f"  Skipped: {skipped}")
    print(f"  Total in products-organized/: {len(list(PRODUCTS_DST.iterdir()))}")
    print(f"\n  Next: create covers and thumbnails for new products")


if __name__ == "__main__":
    main()

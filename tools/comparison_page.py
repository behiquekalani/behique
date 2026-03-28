#!/usr/bin/env python3
"""
Behike vs Competitor -- SEO comparison page generator.

Generates HTML comparison pages that rank for "Behike vs X" searches.
Outputs to storefront/comparisons/.

Usage:
    python3 tools/comparison_page.py --all
    python3 tools/comparison_page.py --versus "Notion Templates"
    python3 tools/comparison_page.py --list
"""

import argparse
import json
import os
import sys
from datetime import datetime
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent
OUTPUT_DIR = PROJECT_ROOT / "storefront" / "comparisons"
PRODUCTS_JSON = PROJECT_ROOT / "storefront" / "products.json"

GUMROAD_STORE_URL = "https://behike.gumroad.com"
STOREFRONT_URL = "https://behike.store"
BRAND = "Behike"
YEAR = datetime.now().year

# --- Competitor definitions ---

COMPETITORS = {
    "notion-templates": {
        "name": "Notion Templates",
        "slug": "behike-vs-notion-templates",
        "title": f"{BRAND} vs Notion Templates",
        "meta_description": f"Side-by-side comparison of {BRAND} business blueprints vs generic Notion templates. See which gives you a real system, not just a pretty layout.",
        "tagline": "A template is a blank page. A blueprint is a system.",
        "competitor_description": "Generic Notion templates sold on marketplaces. Usually pretty layouts with empty databases, toggles, and dashboards. No strategy, no process, no guidance on what to do next.",
        "behike_description": f"{BRAND} blueprints are complete business systems. Each one includes strategy, step-by-step execution plans, AI-powered workflows, and real frameworks tested by builders.",
        "features": [
            ("Complete business strategy", True, False),
            ("Step-by-step execution plan", True, False),
            ("AI workflow integration", True, False),
            ("Revenue model included", True, False),
            ("Aesthetic layout/design", True, True),
            ("Drag-and-drop databases", False, True),
            ("Notion-native format", False, True),
            ("Platform independent", True, False),
            ("Pricing framework", True, False),
            ("Content calendar system", True, True),
            ("Client acquisition system", True, False),
            ("Works without Notion subscription", True, False),
        ],
        "pricing": {
            "behike": "$5 - $29 per blueprint",
            "competitor": "$9 - $79 per template pack",
        },
        "use_cases": [
            {
                "persona": "Solo creator launching a brand",
                "behike_outcome": "Gets a full launch roadmap: positioning, content strategy, monetization channels, and pricing. Ready to execute day one.",
                "competitor_outcome": "Gets a clean Notion workspace with empty databases labeled 'Content Ideas' and 'Revenue Tracker'. Still has to figure out what to put in them.",
            },
            {
                "persona": "Freelancer going full-time",
                "behike_outcome": "Uses the Freelancer to Founder Playbook to build recurring revenue, set pricing, and land high-ticket clients with a proven system.",
                "competitor_outcome": "Gets a project tracker and invoice template. No strategy for actually finding clients or setting rates.",
            },
        ],
        "usp_points": [
            "Every blueprint is a complete business system, not a blank canvas",
            "Built by someone actively building businesses with AI, not a template designer",
            "Platform-independent. Use it in Notion, Google Docs, or pen and paper",
            "Priced for builders, not collectors. No $79 aesthetic packs",
        ],
    },
    "mrnotion-business-blueprint": {
        "name": "Business Blueprint by mrnotion",
        "slug": "behike-vs-mrnotion",
        "title": f"{BRAND} vs Business Blueprint by mrnotion",
        "meta_description": f"Honest comparison: {BRAND} blueprints vs mrnotion's Business Blueprint. Strategy-first systems vs Notion-locked templates.",
        "tagline": "One gives you a system. The other gives you a subscription dependency.",
        "competitor_description": "mrnotion's Business Blueprint is a Notion-based business template. Well-designed, popular in the template space. Requires Notion to use. Focused on organization and tracking rather than strategy.",
        "behike_description": f"{BRAND} blueprints deliver strategy and execution. Each product includes the thinking behind the system, not just the containers to organize your work. Works on any platform.",
        "features": [
            ("Business strategy framework", True, False),
            ("AI automation workflows", True, False),
            ("Step-by-step action plans", True, True),
            ("Revenue model templates", True, False),
            ("Notion integration", False, True),
            ("Platform independent", True, False),
            ("Pricing under $30", True, False),
            ("Content creation system", True, True),
            ("Client acquisition playbook", True, False),
            ("Community/support", False, True),
            ("Multiple product categories", True, False),
            ("AI tools guidance", True, False),
        ],
        "pricing": {
            "behike": "$5 - $29 per blueprint",
            "competitor": "$49 - $149 per template",
        },
        "use_cases": [
            {
                "persona": "New entrepreneur setting up systems",
                "behike_outcome": "Picks the specific blueprint for their business model. Gets strategy + execution plan. Starts implementing immediately regardless of tools.",
                "competitor_outcome": "Gets a comprehensive Notion workspace. Spends time customizing databases before doing any actual business work.",
            },
            {
                "persona": "Creator building multiple income streams",
                "behike_outcome": "Stacks multiple blueprints (Creator's Revenue Blueprint + Email List Blueprint + Content Monetization Bible) for under $70 total. Each one covers a different revenue channel.",
                "competitor_outcome": "Gets one all-in-one template for $99+. Covers breadth but lacks depth on any single revenue strategy.",
            },
        ],
        "usp_points": [
            "Strategy-first, not organization-first. Know what to do, not just where to put it",
            "No platform lock-in. Use with any tool you already have",
            "Modular system. Buy exactly what you need, skip what you don't",
            "AI-native approach. Built for 2026, not 2022",
        ],
    },
    "canva-business-templates": {
        "name": "Canva Business Templates",
        "slug": "behike-os-vs-canva-templates",
        "title": f"{BRAND} OS vs Canva Business Templates",
        "meta_description": f"Compare {BRAND} OS business blueprints to Canva's business template library. Strategy vs design. Which one actually moves your business forward?",
        "tagline": "Design is not strategy. Pretty slides do not build businesses.",
        "competitor_description": "Canva offers thousands of business templates: pitch decks, social media posts, business plans, presentations. Visually polished, easy to customize, free tier available. But they are design templates, not business systems.",
        "behike_description": f"{BRAND} blueprints are business execution systems. Not slide decks. Not social media templates. Actual frameworks, strategies, and step-by-step plans for building revenue.",
        "features": [
            ("Business execution framework", True, False),
            ("Revenue strategy", True, False),
            ("AI workflow integration", True, False),
            ("Visual design templates", False, True),
            ("Social media templates", False, True),
            ("Pitch deck templates", False, True),
            ("Step-by-step business plans", True, False),
            ("Pricing and monetization", True, False),
            ("Client acquisition system", True, False),
            ("Free tier available", False, True),
            ("Content strategy framework", True, False),
            ("Platform independent", True, True),
        ],
        "pricing": {
            "behike": "$5 - $29 per blueprint",
            "competitor": "Free - $14.99/mo (Canva Pro)",
        },
        "use_cases": [
            {
                "persona": "Solopreneur needing business direction",
                "behike_outcome": "Gets a clear roadmap: what to build, how to price it, where to find customers, how to automate. Starts executing with clarity.",
                "competitor_outcome": "Gets beautiful pitch deck slides and social posts. Still does not know what their business model is or how to get customers.",
            },
            {
                "persona": "Creator launching a digital product",
                "behike_outcome": "Uses the Digital Product Launch Formula to plan positioning, pricing, launch sequence, and email automation. Launches with a system.",
                "competitor_outcome": "Makes great-looking promotional graphics. No launch strategy, no email sequence, no pricing framework.",
            },
        ],
        "usp_points": [
            "Business strategy, not business aesthetics",
            "One-time purchase, no monthly subscription",
            "Built for execution, not presentation",
            "AI-powered workflows that actually automate your business",
        ],
    },
    "best-business-blueprint-2026": {
        "name": "Other Business Blueprints",
        "slug": "best-business-blueprint-2026",
        "title": f"Best Business Blueprint {YEAR}",
        "meta_description": f"Looking for the best business blueprint in {YEAR}? Compare top options and see why {BRAND} blueprints are built for the AI era.",
        "tagline": f"The best business blueprint in {YEAR} was built for {YEAR}.",
        "competitor_description": f"Most business blueprints on the market were written before AI changed everything. They teach manual processes, outdated funnels, and strategies that worked in 2020. In {YEAR}, you need a system that leverages AI from day one.",
        "behike_description": f"{BRAND} blueprints are built for the AI era. Every system integrates AI tools, automation workflows, and modern strategies. Written by someone actively building businesses with AI, not recycling old playbooks.",
        "features": [
            ("AI-native business strategies", True, False),
            ("Updated for current year", True, False),
            ("Automation workflows included", True, False),
            ("Multiple business models covered", True, False),
            ("Step-by-step execution plans", True, True),
            ("Affordable pricing", True, False),
            ("Platform independent", True, False),
            ("Revenue frameworks", True, True),
            ("Content strategy", True, True),
            ("Community support", False, True),
            ("Video walkthroughs", False, True),
            ("Modular / stackable", True, False),
        ],
        "pricing": {
            "behike": "$5 - $29 per blueprint",
            "competitor": "$27 - $497 (varies widely)",
        },
        "use_cases": [
            {
                "persona": "First-time digital entrepreneur",
                "behike_outcome": f"Picks the Creator's First $10K Blueprint for $10. Gets a focused, actionable plan to hit first revenue milestone using {YEAR} tools and strategies.",
                "competitor_outcome": "Buys a $197 course that teaches Instagram growth tactics from 2021. Spends weeks on content that nobody sees.",
            },
            {
                "persona": "Experienced creator adding revenue streams",
                "behike_outcome": "Stacks specialized blueprints for each channel: email, YouTube, subscriptions. Total investment under $80 for three complete systems.",
                "competitor_outcome": "Buys one expensive all-in-one program. Gets 20 hours of video content. Never finishes it.",
            },
        ],
        "usp_points": [
            f"Built for {YEAR}. AI-first strategies, not recycled 2020 playbooks",
            "Modular system. Buy what you need, when you need it",
            "Priced for action, not for shelf collecting",
            "Written by a builder, not a guru. No fluff, no filler",
        ],
    },
    "building-from-scratch": {
        "name": "Building from Scratch",
        "slug": "behike-vs-building-from-scratch",
        "title": f"{BRAND} vs Building from Scratch",
        "meta_description": f"Should you build your business from scratch or use a proven blueprint? See how {BRAND} blueprints save months of trial and error.",
        "tagline": "You can figure it all out yourself. Or you can start with a system that works.",
        "competitor_description": "Building from scratch means researching everything yourself, testing strategies through trial and error, and learning from expensive mistakes. It is how most people start. It is also why most people quit in the first 6 months.",
        "behike_description": f"{BRAND} blueprints compress months of research into actionable systems. You still do the work. You just skip the part where you waste time figuring out what the work actually is.",
        "features": [
            ("Proven strategy framework", True, False),
            ("Skip trial-and-error phase", True, False),
            ("AI tool recommendations", True, False),
            ("Complete creative freedom", False, True),
            ("No upfront cost", False, True),
            ("Step-by-step execution plan", True, False),
            ("Revenue model included", True, False),
            ("Learn by doing (hard way)", False, True),
            ("Pricing guidance", True, False),
            ("Content strategy included", True, False),
            ("Time to first revenue: weeks", True, False),
            ("Time to first revenue: months", False, True),
        ],
        "pricing": {
            "behike": "$5 - $29 (one-time)",
            "competitor": "Free (but costs months of time)",
        },
        "use_cases": [
            {
                "persona": "Side hustler with limited hours",
                "behike_outcome": "Spends $19 on a blueprint. Follows the system in 2-3 hours per week. Has a functioning business model within 30 days.",
                "competitor_outcome": "Spends 3 months researching business models on YouTube. Still has not launched anything. Motivation fading.",
            },
            {
                "persona": "Developer wanting to sell digital products",
                "behike_outcome": "Uses the Micro-SaaS Playbook + Gumroad Seller's Playbook. Knows exactly what to build, how to price it, and where to sell it.",
                "competitor_outcome": "Builds something cool. Has no idea how to market it. Gets 3 sales from friends. Concludes 'building products does not work.'",
            },
        ],
        "usp_points": [
            "Skip the research phase. Start with a proven system",
            "Your time is worth more than $19. Stop trading it for free information",
            "A blueprint does not replace your creativity. It gives it structure",
            "Every month you spend 'figuring it out' is a month of lost revenue",
        ],
    },
}


def generate_html(competitor_key: str) -> str:
    """Generate a complete HTML comparison page for a given competitor."""
    c = COMPETITORS[competitor_key]

    # Build feature rows
    feature_rows = ""
    for feature_name, behike_has, competitor_has in c["features"]:
        b_icon = '<span class="check">&#10003;</span>' if behike_has else '<span class="cross">&#10007;</span>'
        c_icon = '<span class="check">&#10003;</span>' if competitor_has else '<span class="cross">&#10007;</span>'
        feature_rows += f"""
            <tr>
                <td class="feature-name">{feature_name}</td>
                <td class="feature-val">{b_icon}</td>
                <td class="feature-val">{c_icon}</td>
            </tr>"""

    # Build use case cards
    use_case_html = ""
    for uc in c["use_cases"]:
        use_case_html += f"""
        <div class="use-case">
            <h3>{uc['persona']}</h3>
            <div class="uc-grid">
                <div class="uc-card uc-behike">
                    <div class="uc-label">With {BRAND}</div>
                    <p>{uc['behike_outcome']}</p>
                </div>
                <div class="uc-card uc-other">
                    <div class="uc-label">With {c['name']}</div>
                    <p>{uc['competitor_outcome']}</p>
                </div>
            </div>
        </div>"""

    # Build USP list
    usp_html = ""
    for point in c["usp_points"]:
        usp_html += f'<li>{point}</li>\n'

    # Structured data (JSON-LD)
    structured_data = json.dumps({
        "@context": "https://schema.org",
        "@type": "WebPage",
        "name": c["title"],
        "description": c["meta_description"],
        "url": f"{STOREFRONT_URL}/comparisons/{c['slug']}.html",
        "publisher": {
            "@type": "Organization",
            "name": BRAND,
            "url": STOREFRONT_URL,
        },
        "mainEntity": {
            "@type": "Product",
            "name": f"{BRAND} Business Blueprints",
            "description": c["behike_description"],
            "brand": {"@type": "Brand", "name": BRAND},
            "offers": {
                "@type": "AggregateOffer",
                "lowPrice": "5",
                "highPrice": "200",
                "priceCurrency": "USD",
                "offerCount": "34",
                "url": GUMROAD_STORE_URL,
            },
        },
    }, indent=2)

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{c['title']} | {BRAND}</title>
<meta name="description" content="{c['meta_description']}">
<meta name="robots" content="index, follow">
<link rel="canonical" href="{STOREFRONT_URL}/comparisons/{c['slug']}.html">

<!-- Open Graph -->
<meta property="og:title" content="{c['title']}">
<meta property="og:description" content="{c['meta_description']}">
<meta property="og:type" content="website">
<meta property="og:url" content="{STOREFRONT_URL}/comparisons/{c['slug']}.html">

<!-- Twitter -->
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{c['title']}">
<meta name="twitter:description" content="{c['meta_description']}">

<!-- Structured Data -->
<script type="application/ld+json">
{structured_data}
</script>

<style>
*,*::before,*::after{{box-sizing:border-box;margin:0;padding:0}}
:root{{--bg:#000;--text:#F5F5F7;--dim:#86868B;--cyan:#00E5FF;--green:#00C853;--red:#FF1744;--surface:#0A0A0A;--surface2:#111;--border:#1A1A1A;--radius:12px;--max:1080px}}
html{{scroll-behavior:smooth}}
body{{background:var(--bg);color:var(--text);font-family:'Helvetica Neue',Helvetica,Arial,sans-serif;font-size:17px;line-height:1.6;-webkit-font-smoothing:antialiased}}
a{{color:var(--cyan);text-decoration:none}}
a:hover{{text-decoration:underline}}
.wrap{{max-width:var(--max);margin:0 auto;padding:0 24px}}

/* Nav */
nav{{position:sticky;top:0;z-index:100;background:rgba(0,0,0,.92);backdrop-filter:blur(20px);-webkit-backdrop-filter:blur(20px);border-bottom:1px solid var(--border)}}
nav .wrap{{display:flex;align-items:center;justify-content:space-between;height:56px}}
nav .logo{{font-size:18px;font-weight:600;letter-spacing:-.02em;color:var(--text)}}
nav .links{{display:flex;gap:28px;font-size:14px}}
nav .links a{{color:var(--dim);transition:color .2s}}
nav .links a:hover{{color:var(--text);text-decoration:none}}

/* Hero */
.hero{{text-align:center;padding:100px 24px 60px}}
.hero .badge{{display:inline-block;padding:6px 16px;border:1px solid var(--cyan);border-radius:980px;font-size:12px;text-transform:uppercase;letter-spacing:.1em;color:var(--cyan);margin-bottom:24px}}
.hero h1{{font-size:clamp(32px,5.5vw,56px);font-weight:700;letter-spacing:-.03em;line-height:1.1;margin-bottom:16px}}
.hero h1 .accent{{color:var(--cyan)}}
.hero .tagline{{font-size:20px;color:var(--dim);max-width:640px;margin:0 auto 40px}}

/* Descriptions */
.desc-grid{{display:grid;grid-template-columns:1fr 1fr;gap:24px;padding:0 24px 80px}}
@media(max-width:680px){{.desc-grid{{grid-template-columns:1fr}}}}
.desc-card{{background:var(--surface2);border:1px solid var(--border);border-radius:var(--radius);padding:32px}}
.desc-card.behike{{border-color:var(--cyan)}}
.desc-card .label{{font-size:12px;text-transform:uppercase;letter-spacing:.1em;color:var(--dim);margin-bottom:12px}}
.desc-card.behike .label{{color:var(--cyan)}}
.desc-card p{{font-size:15px;color:var(--dim);line-height:1.7}}

/* Comparison Table */
.table-section{{padding:0 24px 80px}}
.table-section h2{{font-size:28px;font-weight:600;letter-spacing:-.02em;margin-bottom:32px;text-align:center}}
.comp-table{{width:100%;border-collapse:collapse;background:var(--surface2);border-radius:var(--radius);overflow:hidden;border:1px solid var(--border)}}
.comp-table thead th{{padding:16px 20px;font-size:14px;text-transform:uppercase;letter-spacing:.08em;color:var(--dim);border-bottom:1px solid var(--border);text-align:center}}
.comp-table thead th:first-child{{text-align:left}}
.comp-table thead th.behike-col{{color:var(--cyan)}}
.comp-table tbody tr{{border-bottom:1px solid var(--border)}}
.comp-table tbody tr:last-child{{border-bottom:none}}
.comp-table td{{padding:14px 20px;font-size:15px}}
.comp-table .feature-name{{color:var(--text)}}
.comp-table .feature-val{{text-align:center;font-size:20px}}
.check{{color:var(--green);font-weight:700}}
.cross{{color:var(--red);font-weight:700}}

/* Pricing */
.pricing-section{{padding:0 24px 80px}}
.pricing-section h2{{font-size:28px;font-weight:600;letter-spacing:-.02em;margin-bottom:32px;text-align:center}}
.pricing-grid{{display:grid;grid-template-columns:1fr 1fr;gap:24px;max-width:700px;margin:0 auto}}
@media(max-width:680px){{.pricing-grid{{grid-template-columns:1fr}}}}
.pricing-card{{background:var(--surface2);border:1px solid var(--border);border-radius:var(--radius);padding:32px;text-align:center}}
.pricing-card.behike{{border-color:var(--cyan)}}
.pricing-card .p-label{{font-size:12px;text-transform:uppercase;letter-spacing:.1em;color:var(--dim);margin-bottom:16px}}
.pricing-card.behike .p-label{{color:var(--cyan)}}
.pricing-card .p-price{{font-size:28px;font-weight:700;margin-bottom:8px}}
.pricing-card .p-note{{font-size:13px;color:var(--dim)}}

/* Use Cases */
.uc-section{{padding:0 24px 80px}}
.uc-section h2{{font-size:28px;font-weight:600;letter-spacing:-.02em;margin-bottom:40px;text-align:center}}
.use-case{{margin-bottom:40px}}
.use-case h3{{font-size:18px;font-weight:600;margin-bottom:16px;color:var(--dim)}}
.uc-grid{{display:grid;grid-template-columns:1fr 1fr;gap:20px}}
@media(max-width:680px){{.uc-grid{{grid-template-columns:1fr}}}}
.uc-card{{background:var(--surface2);border:1px solid var(--border);border-radius:var(--radius);padding:24px}}
.uc-card.uc-behike{{border-color:var(--cyan)}}
.uc-label{{font-size:11px;text-transform:uppercase;letter-spacing:.1em;color:var(--dim);margin-bottom:12px}}
.uc-card.uc-behike .uc-label{{color:var(--cyan)}}
.uc-card p{{font-size:14px;color:var(--dim);line-height:1.6}}

/* Why Behike */
.why-section{{padding:0 24px 80px}}
.why-section h2{{font-size:28px;font-weight:600;letter-spacing:-.02em;margin-bottom:32px;text-align:center}}
.why-list{{max-width:640px;margin:0 auto;list-style:none}}
.why-list li{{padding:16px 0;border-bottom:1px solid var(--border);font-size:16px;color:var(--text);padding-left:28px;position:relative}}
.why-list li::before{{content:'\\2192';position:absolute;left:0;color:var(--cyan)}}

/* CTA */
.cta-section{{text-align:center;padding:80px 24px 100px;border-top:1px solid var(--border)}}
.cta-section h2{{font-size:clamp(24px,4vw,40px);font-weight:700;letter-spacing:-.02em;margin-bottom:16px}}
.cta-section p{{font-size:18px;color:var(--dim);max-width:520px;margin:0 auto 40px}}
.cta-btn{{display:inline-block;background:var(--cyan);color:#000;padding:16px 40px;border-radius:980px;font-size:16px;font-weight:600;transition:opacity .2s}}
.cta-btn:hover{{opacity:.85;text-decoration:none}}

/* Footer */
footer{{border-top:1px solid var(--border);padding:40px 24px;text-align:center;font-size:13px;color:var(--dim)}}
</style>
</head>
<body>

<nav>
<div class="wrap">
    <a href="{STOREFRONT_URL}" class="logo">{BRAND}</a>
    <div class="links">
        <a href="{STOREFRONT_URL}/products.html">Products</a>
        <a href="{STOREFRONT_URL}/about.html">About</a>
        <a href="{GUMROAD_STORE_URL}">Store</a>
    </div>
</div>
</nav>

<section class="hero">
<div class="wrap">
    <div class="badge">Comparison</div>
    <h1>{c['title'].replace(BRAND, f'<span class="accent">{BRAND}</span>')}</h1>
    <p class="tagline">{c['tagline']}</p>
</div>
</section>

<div class="wrap">
<div class="desc-grid">
    <div class="desc-card behike">
        <div class="label">{BRAND}</div>
        <p>{c['behike_description']}</p>
    </div>
    <div class="desc-card">
        <div class="label">{c['name']}</div>
        <p>{c['competitor_description']}</p>
    </div>
</div>
</div>

<section class="table-section">
<div class="wrap">
    <h2>Feature Comparison</h2>
    <table class="comp-table">
        <thead>
            <tr>
                <th>Feature</th>
                <th class="behike-col">{BRAND}</th>
                <th>{c['name']}</th>
            </tr>
        </thead>
        <tbody>
            {feature_rows}
        </tbody>
    </table>
</div>
</section>

<section class="pricing-section">
<div class="wrap">
    <h2>Pricing</h2>
    <div class="pricing-grid">
        <div class="pricing-card behike">
            <div class="p-label">{BRAND}</div>
            <div class="p-price">{c['pricing']['behike']}</div>
            <div class="p-note">One-time purchase. No subscription.</div>
        </div>
        <div class="pricing-card">
            <div class="p-label">{c['name']}</div>
            <div class="p-price">{c['pricing']['competitor']}</div>
            <div class="p-note"></div>
        </div>
    </div>
</div>
</section>

<section class="uc-section">
<div class="wrap">
    <h2>Real Use Cases</h2>
    {use_case_html}
</div>
</section>

<section class="why-section">
<div class="wrap">
    <h2>Why {BRAND}</h2>
    <ul class="why-list">
        {usp_html}
    </ul>
</div>
</section>

<section class="cta-section">
<div class="wrap">
    <h2>Ready to stop organizing and start executing?</h2>
    <p>Browse the full {BRAND} catalog. Pick the blueprint that matches your next move.</p>
    <a href="{GUMROAD_STORE_URL}" class="cta-btn">Browse Blueprints</a>
</div>
</section>

<footer>
<div class="wrap">
    &copy; {YEAR} {BRAND}. Built for builders.
</div>
</footer>

</body>
</html>"""
    return html


def build_index_page() -> str:
    """Generate an index page listing all comparison pages."""
    links = ""
    for key, c in COMPETITORS.items():
        links += f"""
        <a href="{c['slug']}.html" class="comp-link">
            <span class="comp-title">{c['title']}</span>
            <span class="comp-arrow">&#8594;</span>
        </a>"""

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{BRAND} Comparisons | See How We Stack Up</title>
<meta name="description" content="Compare {BRAND} business blueprints against popular alternatives. Side-by-side feature, pricing, and strategy comparisons.">
<style>
*,*::before,*::after{{box-sizing:border-box;margin:0;padding:0}}
body{{background:#000;color:#F5F5F7;font-family:'Helvetica Neue',Helvetica,Arial,sans-serif;font-size:17px;line-height:1.6;-webkit-font-smoothing:antialiased}}
a{{color:#00E5FF;text-decoration:none}}
.wrap{{max-width:720px;margin:0 auto;padding:80px 24px}}
h1{{font-size:clamp(28px,5vw,48px);font-weight:700;letter-spacing:-.03em;margin-bottom:12px}}
.sub{{font-size:18px;color:#86868B;margin-bottom:48px}}
.comp-link{{display:flex;align-items:center;justify-content:space-between;padding:20px 24px;background:#111;border:1px solid #1A1A1A;border-radius:12px;margin-bottom:12px;transition:border-color .2s}}
.comp-link:hover{{border-color:#00E5FF;text-decoration:none}}
.comp-title{{font-size:16px;font-weight:500}}
.comp-arrow{{font-size:20px;color:#86868B}}
.comp-link:hover .comp-arrow{{color:#00E5FF}}
.back{{display:inline-block;margin-top:40px;font-size:14px;color:#86868B}}
.back:hover{{color:#F5F5F7}}
</style>
</head>
<body>
<div class="wrap">
    <h1>{BRAND} vs The Rest</h1>
    <p class="sub">See how {BRAND} blueprints compare. No fluff, just facts.</p>
    {links}
    <a href="{STOREFRONT_URL}" class="back">&larr; Back to {BRAND}</a>
</div>
</body>
</html>"""


def generate_one(competitor_key: str) -> Path:
    """Generate a single comparison page and write to disk."""
    if competitor_key not in COMPETITORS:
        print(f"Error: Unknown competitor '{competitor_key}'")
        print(f"Available: {', '.join(COMPETITORS.keys())}")
        sys.exit(1)

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    c = COMPETITORS[competitor_key]
    html = generate_html(competitor_key)
    out_path = OUTPUT_DIR / f"{c['slug']}.html"
    out_path.write_text(html)
    print(f"  Generated: {out_path}")
    return out_path


def generate_all():
    """Generate all comparison pages + index."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    print(f"Generating {len(COMPETITORS)} comparison pages...\n")

    for key in COMPETITORS:
        generate_one(key)

    # Generate index
    index_html = build_index_page()
    index_path = OUTPUT_DIR / "index.html"
    index_path.write_text(index_html)
    print(f"  Generated: {index_path}")

    print(f"\nDone. {len(COMPETITORS) + 1} files written to {OUTPUT_DIR}/")


def find_competitor_by_name(name: str) -> str | None:
    """Fuzzy match a competitor name to a key."""
    name_lower = name.lower().strip()
    # Exact key match
    if name_lower in COMPETITORS:
        return name_lower
    # Match by competitor name
    for key, c in COMPETITORS.items():
        if name_lower in c["name"].lower():
            return key
    # Match by slug
    for key, c in COMPETITORS.items():
        if name_lower.replace(" ", "-") in c["slug"]:
            return key
    # Partial keyword match
    for key, c in COMPETITORS.items():
        if any(word in c["name"].lower() for word in name_lower.split()):
            return key
    return None


def main():
    parser = argparse.ArgumentParser(
        description=f"{BRAND} vs Competitor comparison page generator"
    )
    parser.add_argument("--all", action="store_true", help="Generate all comparison pages")
    parser.add_argument("--versus", type=str, help="Generate page for a specific competitor")
    parser.add_argument("--list", action="store_true", help="List available competitors")

    args = parser.parse_args()

    if args.list:
        print("Available competitors:\n")
        for key, c in COMPETITORS.items():
            print(f"  {key:30s}  {c['name']}")
        print(f"\nUsage: python3 {sys.argv[0]} --versus \"Notion Templates\"")
        return

    if args.all:
        generate_all()
        return

    if args.versus:
        match = find_competitor_by_name(args.versus)
        if match is None:
            print(f"Error: No competitor matching '{args.versus}'")
            print("Run with --list to see available competitors.")
            sys.exit(1)
        OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        generate_one(match)
        return

    parser.print_help()


if __name__ == "__main__":
    main()

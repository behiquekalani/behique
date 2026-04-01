#!/usr/bin/env python3
"""Wave 3: Prep remaining PDFs + web apps as products."""
import os, shutil
from pathlib import Path

REPO = Path(os.path.expanduser("~/behique"))
SRC_PDF = REPO / "Ceiba/projects/content-empire/products"
DST = REPO / "READY-TO-SELL/products-organized"

# PDFs
PDF_PRODUCTS = [
    {"slug":"content-waterfall","pdf":"content-waterfall.pdf","name":"Content Waterfall System","price":"$4.99","tags":"content, repurposing, social media, waterfall, system","title":"CONTENT\nWATERFALL","modules":["One Input","Multiple Outputs","Repurposing","Distribution"],"desc":"One piece of content becomes 10. Blog post → thread → carousel → reel → newsletter.\n\n8 pages. The waterfall system."},
    {"slug":"content-bundle-strategy","pdf":"content-bundle-strategy.pdf","name":"Content Bundle Strategy","price":"$9.99","tags":"content, bundles, pricing, strategy, revenue","title":"CONTENT\nBUNDLE\nSTRATEGY","modules":["Bundle Types","Pricing","Cross-Sell","Upsell","Value Stack"],"desc":"How to bundle your products for maximum revenue. Pricing psychology, value stacking, cross-sell frameworks.\n\n15 pages."},
    {"slug":"behike-flowmap","pdf":"behike-flowmap.pdf","name":"Behike Flowmap","price":"$4.99","tags":"flowmap, business, system, visual, planning","title":"BEHIKE\nFLOWMAP","modules":["Visual Planning","Business Flow","Decision Trees"],"desc":"Your entire business on one visual map. See how everything connects.\n\n6 pages."},
    {"slug":"launch-checklist","pdf":"behike-launch-checklist.pdf","name":"Behike Launch Checklist","price":"$4.99","tags":"launch, checklist, product, gumroad, shipping","title":"LAUNCH\nCHECKLIST","modules":["Pre-Launch","Launch Day","Post-Launch","Promotion"],"desc":"Never forget a step when launching a product. Print it. Check it off. Ship it.\n\n6 pages."},
    {"slug":"content-system","pdf":"behike-method-content-system.pdf","name":"Behike Content System","price":"$9.99","tags":"content, system, creation, pipeline, ADHD","title":"BEHIKE\nCONTENT\nSYSTEM","modules":["Content Pillars","Creation","Scheduling","Analytics","Iteration"],"desc":"The complete content creation system. From idea to post to analytics to iteration.\n\n9 pages."},
    {"slug":"ai-tutor","pdf":"ai-tutor-guide.pdf","name":"AI Tutor Guide","price":"$4.99","tags":"AI, tutor, education, chatbot, learning","title":"AI TUTOR\nGUIDE","modules":["Setup","Training","Deployment","Use Cases"],"desc":"Build an AI tutor from any book or document. Upload content, ask questions, get answers.\n\n7 pages."},
    {"slug":"ecommerce-v3","pdf":"ecommerce-playbook-v3.pdf","name":"E-Commerce Playbook v3","price":"$14.99","tags":"ecommerce, playbook, store, sales, marketing","title":"E-COMMERCE\nPLAYBOOK\nV3","modules":["Store Setup","Products","Marketing","Ads","Analytics","Scaling"],"desc":"The complete e-commerce playbook. Third edition. Everything from store setup to scaling.\n\n19 pages."},
    {"slug":"solopreneur-live-guide","pdf":"solopreneur-os-live-guide.pdf","name":"Solopreneur OS Live Guide","price":"$9.99","tags":"solopreneur, guide, interactive, system, ADHD","title":"SOLOPRENEUR\nOS LIVE\nGUIDE","modules":["Setup","Modules","Exercises","Dashboard","Export"],"desc":"Companion guide for the Solopreneur OS Live web app. How to use every feature.\n\n16 pages."},
]

# Web apps
APP_PRODUCTS = [
    {"slug":"behike-wellness","src":"tools/behike-wellness/index.html","name":"Behike Wellness Suite","price":"$9.99","tags":"wellness, ADHD, circadian, focus, health","title":"BEHIKE\nWELLNESS","modules":["Circadian Filter","ADHD Tools","Focus Timer","Break Reminders"]},
    {"slug":"adhd-tools","src":"tools/adhd-tools/index.html","name":"ADHD Productivity Tools","price":"$4.99","tags":"ADHD, productivity, focus, tools, timer","title":"ADHD\nTOOLS","modules":["Focus Timer","Task Breaker","Dopamine Tracker","Break System"]},
    {"slug":"beatsmith","src":"tools/beatsmith/index.html","name":"BeatSmith - Beat Maker","price":"$9.99","tags":"beats, music, producer, drum machine, synth","title":"BEATSMITH","modules":["Drum Machine","Synth","Sequencer","Export"]},
    {"slug":"daft-punk-studio","src":"tools/daft-punk-studio/index.html","name":"Daft Punk Studio","price":"$9.99","tags":"music, synth, electronic, production, daft punk","title":"DAFT PUNK\nSTUDIO","modules":["Vocoder","Synth","Sequencer","Effects","Mixer"]},
    {"slug":"melodymind","src":"tools/melodymind/index.html","name":"MelodyMind - Melody Generator","price":"$9.99","tags":"melody, music, generator, AI, composition","title":"MELODY\nMIND","modules":["Scale Selection","Pattern Gen","Chord Progressions","Export"]},
    {"slug":"chord-genie","src":"tools/chord-genie/index.html","name":"Chord Genie","price":"$4.99","tags":"chords, music, guitar, piano, theory","title":"CHORD\nGENIE","modules":["Chord Library","Progressions","Voicings","Theory"]},
    {"slug":"freefall-pricing","src":"tools/freefall-pricing/index.html","name":"Freefall Pricing Calculator","price":"$4.99","tags":"pricing, calculator, products, margins, business","title":"FREEFALL\nPRICING","modules":["Cost Calculator","Margin Analysis","Price Comparison","Projections"]},
    {"slug":"revenue-tracker","src":"tools/revenue-tracker/index.html","name":"Revenue Tracker Dashboard","price":"$4.99","tags":"revenue, tracker, dashboard, sales, analytics","title":"REVENUE\nTRACKER","modules":["Sales Log","Revenue Chart","Goals","Projections"]},
]

def create_pdf_product(p):
    folder = DST / p["slug"]
    if folder.exists(): print(f"  SKIP: {p['slug']}"); return False
    folder.mkdir(parents=True, exist_ok=True)
    src = SRC_PDF / p["pdf"]
    if src.exists(): shutil.copy2(src, folder / p["pdf"])
    write_info(folder, p)
    write_covers(folder, p)
    print(f"  PDF: {p['slug']} ({p['price']})")
    return True

def create_app_product(p):
    folder = DST / p["slug"]
    if folder.exists(): print(f"  SKIP: {p['slug']}"); return False
    folder.mkdir(parents=True, exist_ok=True)
    src = REPO / p["src"]
    if src.exists(): shutil.copy2(src, folder / f"{p['slug']}.html")
    p["desc"] = p.get("desc", f"Browser-based app. One HTML file. No account. Works offline.\n\nFeatures: {', '.join(p['modules'])}")
    write_info(folder, p)
    write_covers(folder, p)
    print(f"  APP: {p['slug']} ({p['price']})")
    return True

def write_info(folder, p):
    info = f"GUMROAD LISTING INFO\n====================\n\nName: {p['name']}\nPrice: {p['price']}\nURL slug: {p['slug']}\nCall to action: Buy this\nCategory: Self Improvement > Productivity\nTags: {p['tags']}\nReceipt button: Download\n\nDESCRIPTION:\n{p.get('desc','One HTML file. No account. Works offline.')}\n\nSUMMARY:\n1 file\n{chr(10).join(p['modules'])}\nWorks offline\n\nRECEIPT MESSAGE:\nWelcome to Behike. behike.gumroad.com\n"
    (folder / "GUMROAD_INFO.txt").write_text(info)

def write_covers(folder, p):
    title_html = "<br>".join(p["title"].split("\n"))
    mods = "".join(f'<span class="mod">{m}</span>' for m in p["modules"])
    (folder / "cover.html").write_text(f'<!DOCTYPE html><html><head><meta charset="UTF-8"><style>@import url("https://fonts.googleapis.com/css2?family=Inter:wght@400;700;900&display=swap");*{{margin:0;padding:0;box-sizing:border-box;}}body{{width:1280px;height:720px;background:#0a0a0a;color:#e0e0e0;font-family:"Inter",sans-serif;display:flex;flex-direction:column;justify-content:center;padding:60px 80px;overflow:hidden;position:relative;}}.title{{font-size:38px;font-weight:900;color:#fff;margin:8px 0;line-height:1.1;}}.title span{{color:#00e5ff;}}.line{{width:80px;height:3px;background:#00e5ff;margin:12px 0;}}.modules{{display:flex;flex-wrap:wrap;gap:6px;}}.mod{{background:#111;border:1px solid #1a1a1a;padding:4px 10px;border-radius:4px;font-size:11px;color:#888;}}.brand{{position:absolute;bottom:30px;right:40px;font-size:11px;color:#333;letter-spacing:3px;}}</style></head><body><div class="title"><span>{title_html}</span></div><div class="line"></div><div class="modules">{mods}</div><div class="brand">BEHIKE</div></body></html>')
    (folder / "thumbnail.html").write_text(f'<!DOCTYPE html><html><head><meta charset="UTF-8"><style>@import url("https://fonts.googleapis.com/css2?family=Inter:wght@700;900&display=swap");*{{margin:0;padding:0;box-sizing:border-box;}}body{{width:600px;height:600px;background:#0a0a0a;color:#00e5ff;font-family:"Inter",sans-serif;display:flex;flex-direction:column;justify-content:center;align-items:center;text-align:center;padding:60px;overflow:hidden;}}.title{{font-size:36px;font-weight:900;line-height:1.15;margin-bottom:16px;}}.line{{width:60px;height:3px;background:#00e5ff;margin-bottom:20px;}}.brand{{font-size:11px;color:#333;letter-spacing:4px;}}</style></head><body><div class="title">{title_html}</div><div class="line"></div><div class="brand">BEHIKE</div></body></html>')

print(f"\n{'='*50}\n  WAVE 3: {len(PDF_PRODUCTS)} PDFs + {len(APP_PRODUCTS)} Apps\n{'='*50}\n")
c1 = sum(1 for p in PDF_PRODUCTS if create_pdf_product(p))
c2 = sum(1 for p in APP_PRODUCTS if create_app_product(p))
print(f"\n  Created: {c1+c2} ({c1} PDFs, {c2} apps)")
print(f"  Total: {len(list(DST.iterdir()))}")

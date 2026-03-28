#!/usr/bin/env python3
"""Google Trends Opportunity Detector -- Behike Intelligence.
Fetches daily trending searches (US + PR), cross-references against the Behike
product catalog, scores each trend, generates suggested posts, and sends
Telegram alerts for high-relevance matches.

CLI:  --scan | --report | --history | --keywords
Cron: 0 */6 * * * cd ~/behique/bios/intelligence && python3 trends_detector.py --scan
"""
import argparse, json, os, re, sys
from datetime import datetime, date
from pathlib import Path
import requests

BASE_DIR = Path(__file__).resolve().parent.parent
REPORTS_DIR = BASE_DIR / "reports"
REPORTS_DIR.mkdir(parents=True, exist_ok=True)
PRODUCTS_PATH = BASE_DIR.parent / "storefront" / "products.json"
PROXY_URL = os.environ.get("PROXY_URL")
TG_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
TG_CHAT = os.environ.get("TELEGRAM_CHAT_ID")
UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/124.0.0.0"

# Keyword -> product IDs that should be pushed when this keyword trends
KW = {
    "solopreneur": ["solopreneur-os", "solopreneurs-time-freedom-blueprint",
                     "solopreneur-systems-bible", "n8n-solopreneur-guide"],
    "side hustle": ["freelancer-to-founder-playbook", "creators-first-10k-blueprint",
                     "passive-income-blueprint", "zero-to-1k-roadmap"],
    "ai tools": ["ai-tools-mastery-guide", "ai-agent-installer-kit",
                  "ai-automation-blueprint", "ai-prompt-cheat-sheet"],
    "ai agent": ["ai-agent-installer-kit", "ai-employee-guide", "ai-security-guide"],
    "dropshipping": ["ebay-dropshipping-guide", "ecommerce-playbook-v3", "niche-sniper-guide"],
    "passive income": ["passive-income-blueprint", "recurring-revenue-blueprint"],
    "personal brand": ["personal-brand-blueprint", "one-person-brand-bible", "brand-voice-guide"],
    "youtube": ["youtube-channel-blueprint", "youtube-monetization-blueprint",
                 "faceless-creator-blueprint"],
    "affiliate": ["affiliate-marketing-blueprint", "content-monetization-bible"],
    "freelance": ["freelancer-to-founder-playbook", "freelance-rate-calculator-guide",
                   "consulting-blueprint"],
    "content creation": ["ai-content-machine-kit", "content-empire-kit", "the-content-vault"],
    "email marketing": ["email-list-blueprint", "email-marketing-playbook"],
    "online course": ["creators-course-creation-blueprint", "digital-product-launch-formula"],
    "coaching": ["creators-coaching-business-blueprint", "high-ticket-client-blueprint"],
    "notion": ["creator-productivity-os", "solopreneur-os", "solopreneur-second-brain"],
    "digital product": ["digital-product-launch-formula", "gumroad-sellers-playbook"],
    "newsletter": ["creators-newsletter-bible", "email-list-blueprint"],
    "linkedin": ["linkedin-growth-playbook", "thought-leadership-playbook"],
    "twitter": ["twitter-x-growth-system"],
    "remote work": ["remote-work-mastery-guide", "digital-nomad-starter-kit"],
    "adhd": ["adhd-finance-guide", "study-buddy-guide"],
    "automation": ["n8n-automation-pack", "n8n-solopreneur-guide", "ai-automation-blueprint"],
    "saas": ["micro-saas-playbook", "recurring-revenue-blueprint"],
    "copywriting": ["ai-copywriting-playbook", "creators-writing-masterclass"],
    "ecommerce": ["ecommerce-playbook-v3", "amazon-fba-guide", "ebay-dropshipping-guide"],
    "claude": ["claude-code-course", "ai-tools-mastery-guide"],
    "chatgpt": ["ai-prompt-cheat-sheet", "ai-tools-mastery-guide"],
    "n8n": ["n8n-automation-pack", "n8n-solopreneur-guide"],
    "gumroad": ["gumroad-sellers-playbook", "gumroad-starter-kit"],
    "budgeting": ["budget-template", "cash-flow-dashboard", "personal-finance-os"],
    "storytelling": ["creators-storytelling-masterclass", "brand-voice-guide"],
}

POST_TPL = {
    "ai tools": "AI is moving fast. Here are the tools that matter -- not hype. Check {product}.",
    "solopreneur": "Running a business alone is a strategy, not a disadvantage. {product} shows you the system.",
    "side hustle": "The best side hustles in 2026 are not what you think. {product} breaks it down.",
    "passive income": "Passive income is not passive at the start. {product} gives you the system.",
    "dropshipping": "Dropshipping is not dead. It evolved. {product} shows you the new playbook.",
    "youtube": "YouTube is still the best long-term play for creators. {product} is your launch system.",
    "freelance": "Stop trading hours for dollars. {product} shows you how to build from freelancing.",
}
DEFAULT_TPL = "This is trending right now: {trend}. If you are building online, {product} is your next move."

def load_products() -> dict:
    if not PRODUCTS_PATH.exists():
        print(f"[!] products.json not found at {PRODUCTS_PATH}", file=sys.stderr)
        return {}
    with open(PRODUCTS_PATH) as f:
        return {p["id"]: p for p in json.load(f)}

def _session() -> requests.Session:
    s = requests.Session()
    s.headers["User-Agent"] = UA
    if PROXY_URL:
        s.proxies = {"http": PROXY_URL, "https": PROXY_URL}
    return s

def fetch_daily_trends(geo: str = "US") -> list[dict]:
    url = f"https://trends.google.com/trending/rss?geo={geo}"
    try:
        r = _session().get(url, timeout=15)
        r.raise_for_status()
    except requests.RequestException as e:
        print(f"[!] Trends fetch failed ({geo}): {e}", file=sys.stderr)
        return []
    items = []
    for m in re.finditer(
        r"<item>.*?<title>(.+?)</title>.*?"
        r"<ht:approx_traffic>(.+?)</ht:approx_traffic>.*?"
        r"<pubDate>(.+?)</pubDate>", r.text, re.DOTALL
    ):
        vol_raw = m.group(2).strip().replace(",", "").replace("+", "")
        try: vol = int(vol_raw)
        except ValueError: vol = 0
        items.append({"title": m.group(1).strip(), "volume": vol,
                       "pub_date": m.group(3).strip(), "geo": geo})
    return items

def fetch_all_trends() -> list[dict]:
    trends = fetch_daily_trends("US") + fetch_daily_trends("PR")
    seen = {}
    for t in trends:
        k = t["title"].lower()
        if k not in seen or t["volume"] > seen[k]["volume"]:
            seen[k] = t
    return list(seen.values())

def score_trend(trend: dict, products: dict) -> dict:
    title_lower = trend["title"].lower()
    matched_kw, matched_pids = [], set()
    for keyword, pids in KW.items():
        if keyword in title_lower or any(w in title_lower for w in keyword.split() if len(w) > 3):
            matched_kw.append(keyword)
            matched_pids.update(pids)
    vol = trend.get("volume", 0)
    vol_score = 40 if vol >= 500_000 else 30 if vol >= 100_000 else 20 if vol >= 50_000 else 10 if vol >= 10_000 else 5
    rel_score = min(40, len(matched_kw) * 15)
    total = vol_score + rel_score + 20  # recency = 20 (daily trends)
    top_prods = [{"id": p, "title": products[p]["title"], "price": products[p]["price"]}
                 for p in list(matched_pids)[:3] if p in products]
    return {**trend, "score": total, "vol_score": vol_score, "rel_score": rel_score,
            "matched_keywords": matched_kw, "matched_products": top_prods,
            "is_opportunity": rel_score > 0}

def generate_post(scored: dict) -> str:
    if not scored["matched_products"]:
        return ""
    product = scored["matched_products"][0]["title"]
    key = scored["matched_keywords"][0] if scored["matched_keywords"] else ""
    tpl = POST_TPL.get(key, DEFAULT_TPL)
    return tpl.format(product=product, trend=scored["title"])

def send_telegram(msg: str):
    if not TG_TOKEN or not TG_CHAT:
        return
    try:
        requests.post(f"https://api.telegram.org/bot{TG_TOKEN}/sendMessage",
                      json={"chat_id": TG_CHAT, "text": msg, "parse_mode": "Markdown"}, timeout=10)
    except requests.RequestException:
        pass

def build_report(scored: list) -> dict:
    opps = sorted([t for t in scored if t["is_opportunity"]], key=lambda x: x["score"], reverse=True)
    posts = [{"trend": o["title"], "score": o["score"], "products": o["matched_products"],
              "post": generate_post(o)} for o in opps[:3] if generate_post(o)]
    return {
        "date": date.today().isoformat(), "scan_time": datetime.now().isoformat(),
        "total_trends": len(scored), "opportunities": len(opps),
        "top_opportunities": [{"title": o["title"], "score": o["score"], "volume": o["volume"],
                                "keywords": o["matched_keywords"], "products": o["matched_products"]}
                               for o in opps[:10]],
        "suggested_posts": posts,
        "all_trends": [{"title": t["title"], "volume": t["volume"], "score": t["score"],
                         "is_opportunity": t["is_opportunity"]}
                        for t in sorted(scored, key=lambda x: x["score"], reverse=True)],
    }

def save_report(report: dict) -> Path:
    path = REPORTS_DIR / f"trends-{report['date']}.json"
    with open(path, "w") as f:
        json.dump(report, f, indent=2)
    return path

# -- CLI commands --

def cmd_scan():
    print("[*] Fetching Google Trends (US + PR)...")
    trends = fetch_all_trends()
    if not trends:
        print("[!] No trends fetched. Check network/proxy."); return
    print(f"[*] Got {len(trends)} trending topics")
    products = load_products()
    scored = [score_trend(t, products) for t in trends]
    report = build_report(scored)
    path = save_report(report)
    print(f"[+] Report saved: {path}")
    opps = report["top_opportunities"]
    if opps:
        print(f"\n--- {len(opps)} OPPORTUNITIES ---")
        for i, o in enumerate(opps[:5], 1):
            prods = ", ".join(p["title"] for p in o["products"][:2]) or "general"
            print(f"  {i}. [{o['score']}] {o['title']} (vol: {o['volume']:,})")
            print(f"     Keywords: {', '.join(o['keywords'])}  |  Push: {prods}")
    else:
        print("\n[*] No product-aligned opportunities right now.")
    if report["suggested_posts"]:
        print("\n--- SUGGESTED POSTS ---")
        for sp in report["suggested_posts"]:
            print(f"\n  [{sp['trend']}]\n  {sp['post']}")
    high = [o for o in opps if o["score"] >= 50]
    if high:
        lines = ["*Trends Alert*\n"]
        for o in high[:3]:
            prods = ", ".join(p["title"] for p in o["products"][:2])
            lines.append(f"*{o['title']}* (score {o['score']})\nPush: {prods}\n")
        send_telegram("\n".join(lines))
        print("\n[+] Telegram alert sent for high-relevance trends")

def cmd_report():
    reports = sorted(REPORTS_DIR.glob("trends-*.json"), reverse=True)
    if not reports: print("[!] No reports found. Run --scan first."); return
    with open(reports[0]) as f: r = json.load(f)
    print(f"Report: {reports[0].name} | {r.get('scan_time', '?')}")
    print(f"Trends: {r['total_trends']} | Opportunities: {r['opportunities']}")
    for i, o in enumerate(r.get("top_opportunities", [])[:5], 1):
        prods = ", ".join(p["title"] for p in o.get("products", [])[:2]) or "none"
        print(f"  {i}. [{o['score']}] {o['title']} -> {prods}")
    for sp in r.get("suggested_posts", []):
        print(f"\n  [{sp['trend']}] {sp['post']}")

def cmd_history():
    reports = sorted(REPORTS_DIR.glob("trends-*.json"), reverse=True)
    if not reports: print("[!] No reports found."); return
    for rp in reports[:30]:
        try:
            with open(rp) as f: d = json.load(f)
            print(f"  {rp.name} | opps: {d.get('opportunities','?')} | trends: {d.get('total_trends','?')}")
        except json.JSONDecodeError: print(f"  {rp.name} | [corrupt]")

def cmd_keywords():
    products = load_products()
    print(f"Tracking {len(KW)} keyword groups:\n")
    for kw, pids in sorted(KW.items()):
        print(f"  {kw:20s} -> {', '.join(products[p]['title'] for p in pids[:3] if p in products)}")

def main():
    p = argparse.ArgumentParser(description="Google Trends Opportunity Detector")
    p.add_argument("--scan", action="store_true", help="Fetch + score + alert")
    p.add_argument("--report", action="store_true", help="Show latest report")
    p.add_argument("--history", action="store_true", help="List past reports")
    p.add_argument("--keywords", action="store_true", help="Show tracked keywords")
    a = p.parse_args()
    if a.scan: cmd_scan()
    elif a.report: cmd_report()
    elif a.history: cmd_history()
    elif a.keywords: cmd_keywords()
    else: p.print_help()

if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
Competitor Price Monitor -- Digital Products Niche
Tracks pricing changes across Gumroad, business-blueprints.com, and Etsy.
Alerts via Telegram on price changes. Weekly market positioning report.

Usage:
    python3 price_monitor.py --scan                  # Scan all sources
    python3 price_monitor.py --report                # Weekly pricing report
    python3 price_monitor.py --history SELLER_NAME   # Price history for competitor
    python3 price_monitor.py --suggest               # Price adjustment suggestions

Cron (daily 8 AM):
    0 8 * * * cd /Users/kalani/behique/bios/intelligence && python3 price_monitor.py --scan
"""
import argparse, json, os, re, sys, urllib.error, urllib.request
from datetime import datetime, date
from pathlib import Path
import requests
from bs4 import BeautifulSoup

# -- Config ------------------------------------------------------------------
DATA_DIR = Path(__file__).resolve().parent / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)
DB_FILE = DATA_DIR / "competitor_prices.json"
PROXY_URL = os.environ.get("PROXY_URL")
TG_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "")
TG_CHAT = os.environ.get("TELEGRAM_CHAT_ID", "")
UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
      "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36")
GUMROAD_Q = ["business blueprint", "solopreneur template", "business operating system"]
ETSY_Q = ["business blueprint template"]
OUR_PRODUCTS = {"Business Blueprint": 29.00, "Starter Pack": 19.00}

# -- DB helpers --------------------------------------------------------------
def _load_db():
    if DB_FILE.exists():
        with open(DB_FILE) as f: return json.load(f)
    return {"products": {}, "scans": [], "alerts": []}

def _save_db(db):
    with open(DB_FILE, "w") as f: json.dump(db, f, indent=2, default=str)

def _pkey(name, seller):
    return f"{seller.lower().strip()}::{name.lower().strip()}"

# -- HTTP --------------------------------------------------------------------
def _session():
    s = requests.Session()
    s.headers.update({"User-Agent": UA})
    if PROXY_URL: s.proxies = {"http": PROXY_URL, "https": PROXY_URL}
    return s

def _get(sess, url, **kw):
    try:
        r = sess.get(url, timeout=15, **kw); r.raise_for_status(); return r
    except requests.RequestException as e:
        print(f"  [WARN] {url}: {e}", file=sys.stderr); return None

# -- Telegram ----------------------------------------------------------------
def _tg(msg):
    if not TG_TOKEN or not TG_CHAT: return
    payload = json.dumps({"chat_id": TG_CHAT, "text": msg, "parse_mode": "Markdown"}).encode()
    req = urllib.request.Request(
        f"https://api.telegram.org/bot{TG_TOKEN}/sendMessage",
        data=payload, headers={"Content-Type": "application/json"})
    try: urllib.request.urlopen(req, timeout=10)
    except (urllib.error.URLError, OSError): pass

# -- Scrapers ----------------------------------------------------------------
def _parse_price(text):
    m = re.search(r"\$([\d,.]+)", text or "")
    if m:
        try: return float(m.group(1).replace(",", ""))
        except ValueError: pass
    return None

def _scrape_gumroad(sess):
    products, seen = [], set()
    for q in GUMROAD_Q:
        print(f"  [gumroad] '{q}'...")
        resp = _get(sess, "https://gumroad.com/discover", params={"query": q})
        if not resp: continue
        soup = BeautifulSoup(resp.text, "html.parser")
        for card in soup.find_all("article"):
            t = card.find(["h2", "h3", "h4", "span"])
            if not t: continue
            link = card.find("a", href=True)
            url = link.get("href", "") if link else ""
            if url in seen: continue
            seen.add(url)
            sel_el = card.find(class_=re.compile(r"creator|seller|author"))
            price_el = card.find(string=re.compile(r"\$\d+"))
            products.append({"name": t.get_text(strip=True), "price": _parse_price(str(price_el)),
                "seller": sel_el.get_text(strip=True) if sel_el else "unknown",
                "url": url, "source": "gumroad"})
        for script in soup.find_all("script"):
            txt = script.string or ""
            if "price" not in txt: continue
            for m in re.findall(r'\{[^{}]*"name"\s*:\s*"[^"]*"[^{}]*"price"\s*:\s*\d+[^{}]*\}', txt):
                try:
                    d = json.loads(m); url = d.get("url", "")
                    if url in seen: continue
                    seen.add(url)
                    products.append({"name": d.get("name", "Unknown"),
                        "price": (d.get("price", 0) or 0) / 100,
                        "seller": d.get("creator_name", "unknown"),
                        "url": url, "source": "gumroad"})
                except (json.JSONDecodeError, TypeError): continue
    return products

def _scrape_blueprints(sess):
    print("  [mrnotion] business-blueprints.com...")
    products = []
    resp = _get(sess, "https://business-blueprints.com")
    if not resp: return products
    soup = BeautifulSoup(resp.text, "html.parser")
    headings = [h.get_text(strip=True) for tag in ["h2","h3","h4"]
                for h in soup.find_all(tag)
                if any(k in h.get_text(strip=True).lower() for k in ["blueprint","template","pack","bundle","system"])]
    prices = []
    for pt in soup.find_all(string=re.compile(r"\$\d+")):
        p = _parse_price(pt)
        if p: prices.append(p)
    for i, name in enumerate(headings):
        products.append({"name": name, "price": prices[i] if i < len(prices) else None,
            "seller": "mrnotion", "url": "https://business-blueprints.com", "source": "mrnotion"})
    if not headings:
        for i, p in enumerate(prices):
            products.append({"name": f"Product #{i+1}", "price": p,
                "seller": "mrnotion", "url": "https://business-blueprints.com", "source": "mrnotion"})
    return products

def _scrape_etsy(sess):
    products, seen = [], set()
    for q in ETSY_Q:
        print(f"  [etsy] '{q}'...")
        resp = _get(sess, "https://www.etsy.com/search", params={"q": q})
        if not resp: continue
        soup = BeautifulSoup(resp.text, "html.parser")
        for card in soup.find_all("div", class_=re.compile(r"listing-card|v2-listing")):
            t = card.find(["h3","h2","p"], class_=re.compile(r"title|name")) or card.find(["h3","h2"])
            if not t: continue
            link = card.find("a", href=True)
            url = link.get("href", "") if link else ""
            if url in seen: continue
            seen.add(url)
            pe = card.find(string=re.compile(r"\$?\d+\.\d{2}"))
            if not pe:
                pe_el = card.find(class_=re.compile(r"price|currency"))
                pe = pe_el.get_text() if pe_el else None
            sel = card.find(class_=re.compile(r"shop-name|seller"))
            products.append({"name": t.get_text(strip=True), "price": _parse_price(str(pe)),
                "seller": sel.get_text(strip=True) if sel else "unknown",
                "url": url, "source": "etsy"})
    return products

# -- Core commands -----------------------------------------------------------
def scan():
    print("[*] Starting price scan...")
    db, sess, now = _load_db(), _session(), datetime.utcnow().isoformat()
    found = _scrape_gumroad(sess) + _scrape_blueprints(sess) + _scrape_etsy(sess)
    changes = []
    for item in found:
        if item["price"] is None: continue
        key = _pkey(item["name"], item["seller"])
        ex = db["products"].get(key)
        if ex:
            old = ex.get("price")
            if old is not None and old != item["price"]:
                ch = {"product": item["name"], "seller": item["seller"],
                      "old_price": old, "new_price": item["price"],
                      "diff": round(item["price"] - old, 2), "detected_at": now}
                changes.append(ch); db["alerts"].append(ch)
                ex.setdefault("price_history", []).append({"price": old, "date": ex.get("last_checked", now)})
            ex["price"] = item["price"]; ex["last_checked"] = now
        else:
            db["products"][key] = {"name": item["name"], "price": item["price"],
                "seller": item["seller"], "url": item.get("url", ""),
                "source": item.get("source", ""), "last_checked": now, "price_history": []}
    db["scans"].append({"timestamp": now, "found": len(found), "changes": len(changes)})
    db["scans"] = db["scans"][-90:]
    _save_db(db)
    print(f"[+] {len(found)} products scanned. {len(changes)} price change(s).")
    if changes:
        lines = ["*Price Change Alert*\n"]
        for c in changes:
            d = "UP" if c["diff"] > 0 else "DOWN"
            lines.append(f"  {c['seller']} - {c['product']}\n  ${c['old_price']:.2f} -> ${c['new_price']:.2f} ({d} ${abs(c['diff']):.2f})")
        msg = "\n".join(lines); _tg(msg); print(msg)
    return changes

def report():
    db = _load_db()
    if not db["products"]: print("[!] No data. Run --scan first."); return
    by_src = {"gumroad": [], "mrnotion": [], "etsy": []}
    all_p = []
    for p in db["products"].values():
        pr = p.get("price")
        if not pr or pr <= 0: continue
        all_p.append(pr)
        src = p.get("source", "other")
        if src in by_src: by_src[src].append(pr)
    if not all_p: print("[!] No valid prices."); return
    all_p.sort(); avg = sum(all_p)/len(all_p); med = all_p[len(all_p)//2]
    print("=" * 60)
    print(f"  WEEKLY PRICING REPORT -- {date.today().isoformat()}")
    print("=" * 60)
    print(f"\n  Market ({len(all_p)} products)")
    print(f"    Avg: ${avg:.2f}  |  Median: ${med:.2f}  |  Range: ${all_p[0]:.2f}-${all_p[-1]:.2f}")
    for src, v in by_src.items():
        if v: print(f"    {src}: {len(v)} products, avg ${sum(v)/len(v):.2f}")
    print(f"\n  Your Products vs Market")
    for name, op in OUR_PRODUCTS.items():
        pctile = round(sum(1 for p in all_p if p < op) / len(all_p) * 100)
        print(f"    {name}: ${op:.2f}  ({pctile}th percentile)")
    recent = db.get("alerts", [])[-10:]
    if recent:
        print(f"\n  Recent Changes ({len(recent)})")
        for a in recent:
            print(f"    {a['seller']} - {a['product']}: ${a['old_price']:.2f} -> ${a['new_price']:.2f}")
    print()

def history(filt):
    db, found = _load_db(), False
    for _, p in db["products"].items():
        if filt.lower() not in p.get("seller","").lower() and filt.lower() not in p.get("name","").lower(): continue
        found = True
        print(f"\n  {p['name']} ({p['seller']})  --  ${p.get('price','N/A')}  [{p.get('source','')}]")
        print(f"    URL: {p.get('url','N/A')}  |  Last: {p.get('last_checked','N/A')}")
        hist = p.get("price_history", [])
        if hist:
            for h in hist: print(f"    ${h['price']:.2f} on {h['date']}")
        else: print("    No price changes yet.")
    if not found: print(f"[!] No products matching '{filt}'.")

def suggest():
    db = _load_db()
    all_p = sorted(p["price"] for p in db["products"].values() if p.get("price") and p["price"] > 0)
    if not all_p: print("[!] No data. Run --scan first."); return
    avg, med = sum(all_p)/len(all_p), all_p[len(all_p)//2]
    print("=" * 60)
    print(f"  PRICING SUGGESTIONS  |  Market: avg ${avg:.2f}, median ${med:.2f}, range ${all_p[0]:.2f}-${all_p[-1]:.2f}")
    print("=" * 60)
    for name, op in OUR_PRODUCTS.items():
        ratio = op / avg if avg else 1
        if ratio < 0.6:    strat, rec = "UNDERPRICED", f"Raise to ${avg*0.85:.2f}-${avg:.2f}. Leaving money on the table."
        elif ratio < 0.85: strat, rec = "BUDGET", f"Entry price. Consider ${med:.2f} to match median."
        elif ratio < 1.15: strat, rec = "COMPETITIVE", "Hold steady or add bonuses to justify a bump."
        elif ratio < 1.5:  strat, rec = "PREMIUM", "Above average. Ensure landing page shows premium value."
        else:              strat, rec = "LUXURY", f"Well above market (avg ${avg:.2f}). Needs strong differentiation."
        pctile = round(sum(1 for p in all_p if p < op) / len(all_p) * 100)
        tactic = (f"UNDERCUT -- only {pctile}% cheaper. Room to raise." if pctile < 30
                  else f"PREMIUM -- {pctile}% cheaper. Justify with bonuses." if pctile > 70
                  else f"HOLD -- {pctile}th percentile. Solid ground.")
        print(f"\n  {name} (${op:.2f})  [{strat}]")
        print(f"    {rec}")
        print(f"    Tactic: {tactic}")
    print()

# -- CLI ---------------------------------------------------------------------
def main():
    ap = argparse.ArgumentParser(description="Competitor Price Monitor")
    ap.add_argument("--scan", action="store_true", help="Scan all sources for prices")
    ap.add_argument("--report", action="store_true", help="Weekly pricing report")
    ap.add_argument("--history", metavar="COMPETITOR", help="Price history for competitor")
    ap.add_argument("--suggest", action="store_true", help="Price adjustment suggestions")
    args = ap.parse_args()
    if not any([args.scan, args.report, args.history, args.suggest]):
        ap.print_help(); sys.exit(1)
    if args.scan: scan()
    if args.report: report()
    if args.history: history(args.history)
    if args.suggest: suggest()

if __name__ == "__main__":
    main()

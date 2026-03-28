#!/usr/bin/env python3
"""
PR Opportunities Scraper - Grants, programs, incentives, and events for Puerto Rico entrepreneurs.

Scrapes:
    - Colmena66 events and programs
    - DDEC (Dept. of Economic Development) announcements
    - SBA Puerto Rico district office
    - Invest Puerto Rico news
    - PRITS (PR Innovation & Technology Service)

Usage:
    python3 bios/ingestion/pr_opportunities.py --run
    python3 bios/ingestion/pr_opportunities.py --run --notify

Cron (every 12 hours):
    0 */12 * * * cd ~/behique && python3 bios/ingestion/pr_opportunities.py --run --notify
"""

import argparse
import hashlib
import json
import os
import re
import time
from datetime import datetime, timezone, timedelta
from pathlib import Path

try:
    import feedparser
except ImportError:
    print("ERROR: feedparser not installed. Run: pip install feedparser")
    raise SystemExit(1)

try:
    import requests
except ImportError:
    print("ERROR: requests not installed. Run: pip install requests")
    raise SystemExit(1)

from bs4 import BeautifulSoup

# --- Config ---

BASE_DIR = Path(__file__).resolve().parent.parent.parent
STORAGE_DIR = BASE_DIR / "bios" / "storage"
OUTPUT_FILE = STORAGE_DIR / "pr_opportunities.json"
STORAGE_DIR.mkdir(parents=True, exist_ok=True)

MAX_OPPORTUNITIES = 500
DELAY_BETWEEN_SOURCES = 2
USER_AGENT = "BIOS/2.0 (Behike Intelligence System)"
DEADLINE_ALERT_DAYS = 30

HEADERS = {
    "User-Agent": USER_AGENT,
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9,es;q=0.8",
}

# --- Sources ---

SOURCES = {
    "colmena66": {
        "name": "Colmena66",
        "urls": [
            "https://colmena66.com/eventos/",
            "https://colmena66.com/programas/",
        ],
        "type": "html",
        "default_category": "program",
    },
    "ddec": {
        "name": "DDEC",
        "urls": [
            "https://www.ddec.pr.gov/category/noticias/feed/",
            "https://www.ddec.pr.gov/category/comunicados/feed/",
        ],
        "type": "rss",
        "default_category": "incentive",
    },
    "sba_pr": {
        "name": "SBA Puerto Rico",
        "urls": [
            "https://www.sba.gov/RSS/feeds?office=puerto-rico",
            "https://www.sba.gov/blog?office=puerto-rico",
        ],
        "type": "mixed",
        "default_category": "grant",
    },
    "invest_pr": {
        "name": "Invest Puerto Rico",
        "urls": [
            "https://www.investpr.org/news/",
            "https://www.investpr.org/incentives/",
        ],
        "type": "html",
        "default_category": "incentive",
    },
    "prits": {
        "name": "PRITS",
        "urls": [
            "https://www.prits.pr.gov/noticias",
            "https://www.prits.pr.gov/programas",
        ],
        "type": "html",
        "default_category": "program",
    },
}

# Category keywords for classification
CATEGORY_KEYWORDS = {
    "grant": ["grant", "beca", "subvencion", "funding", "fondos", "financiamiento", "sbir", "sttr"],
    "program": ["program", "programa", "training", "capacitacion", "mentoría", "mentor", "accelerator", "incubadora", "bootcamp", "cohort"],
    "event": ["event", "evento", "webinar", "workshop", "taller", "conferencia", "summit", "meetup", "hackathon", "feria"],
    "incentive": ["incentive", "incentivo", "tax", "exencion", "act 20", "act 22", "act 60", "ley 60", "tax credit", "credito contributivo"],
}


def classify_category(text, default="program"):
    """Classify opportunity into grant/program/event/incentive based on keywords."""
    text_lower = text.lower()
    scores = {}
    for category, keywords in CATEGORY_KEYWORDS.items():
        scores[category] = sum(1 for kw in keywords if kw in text_lower)
    best = max(scores, key=scores.get)
    return best if scores[best] > 0 else default


def extract_deadline(text):
    """Try to extract a deadline date from text. Returns ISO string or None."""
    patterns = [
        # English patterns
        r"deadline[:\s]+(\w+ \d{1,2},?\s*\d{4})",
        r"due[:\s]+(\w+ \d{1,2},?\s*\d{4})",
        r"closes?\s+(?:on\s+)?(\w+ \d{1,2},?\s*\d{4})",
        r"until\s+(\w+ \d{1,2},?\s*\d{4})",
        r"before\s+(\w+ \d{1,2},?\s*\d{4})",
        r"expires?\s+(?:on\s+)?(\w+ \d{1,2},?\s*\d{4})",
        # Spanish patterns
        r"fecha l[ií]mite[:\s]+(\d{1,2}\s+de\s+\w+\s+de\s+\d{4})",
        r"hasta el\s+(\d{1,2}\s+de\s+\w+\s+de\s+\d{4})",
        r"cierra?\s+(?:el\s+)?(\d{1,2}\s+de\s+\w+\s+de\s+\d{4})",
        # ISO-ish
        r"(\d{4}-\d{2}-\d{2})",
        r"(\d{1,2}/\d{1,2}/\d{4})",
    ]

    spanish_months = {
        "enero": "January", "febrero": "February", "marzo": "March",
        "abril": "April", "mayo": "May", "junio": "June",
        "julio": "July", "agosto": "August", "septiembre": "September",
        "octubre": "October", "noviembre": "November", "diciembre": "December",
    }

    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            date_str = match.group(1).strip()
            # Replace Spanish month names
            for es, en in spanish_months.items():
                date_str = re.sub(es, en, date_str, flags=re.IGNORECASE)
                date_str = date_str.replace(" de ", " ")

            for fmt in ["%B %d %Y", "%B %d, %Y", "%Y-%m-%d", "%m/%d/%Y", "%d %B %Y"]:
                try:
                    dt = datetime.strptime(date_str, fmt)
                    return dt.strftime("%Y-%m-%d")
                except ValueError:
                    continue
    return None


def fetch_url(url, timeout=15):
    """Fetch a URL with error handling."""
    try:
        resp = requests.get(url, headers=HEADERS, timeout=timeout)
        resp.raise_for_status()
        return resp
    except Exception as e:
        print(f"  [WARN] Failed to fetch {url}: {e}")
        return None


def scrape_rss(url, source_name, default_category):
    """Scrape opportunities from an RSS feed."""
    opportunities = []
    resp = fetch_url(url)
    if not resp:
        return opportunities

    feed = feedparser.parse(resp.text)
    for entry in feed.entries[:25]:
        title = entry.get("title", "").strip()
        link = entry.get("link", "").strip()
        description = entry.get("summary", entry.get("description", "")).strip()
        # Strip HTML tags from description
        if "<" in description:
            description = BeautifulSoup(description, "html.parser").get_text(separator=" ").strip()
        description = description[:500]

        published = entry.get("published", entry.get("updated", ""))
        combined_text = f"{title} {description}"
        category = classify_category(combined_text, default_category)
        deadline = extract_deadline(combined_text)

        if title and link:
            opportunities.append({
                "title": title,
                "description": description,
                "url": link,
                "source": source_name,
                "category": category,
                "deadline": deadline,
                "published": published,
                "scraped_at": datetime.now(timezone.utc).isoformat(),
            })

    return opportunities


def scrape_html_page(url, source_name, default_category):
    """Scrape opportunities from an HTML page by extracting links and text."""
    opportunities = []
    resp = fetch_url(url)
    if not resp:
        return opportunities

    soup = BeautifulSoup(resp.text, "html.parser")

    # Strategy: find article/card-like containers, or fall back to links
    containers = soup.select(
        "article, .event-card, .program-card, .post-card, .card, "
        ".news-item, .entry, .listing-item, .grid-item, "
        "[class*='event'], [class*='program'], [class*='news'], [class*='post']"
    )

    if containers:
        for container in containers[:25]:
            # Find the main link
            link_tag = container.find("a", href=True)
            if not link_tag:
                continue

            href = link_tag["href"]
            if not href.startswith("http"):
                from urllib.parse import urljoin
                href = urljoin(url, href)

            # Title: first heading or link text
            title_tag = container.find(["h1", "h2", "h3", "h4", "h5"])
            title = title_tag.get_text(strip=True) if title_tag else link_tag.get_text(strip=True)

            # Description: first paragraph or all text minus title
            desc_tag = container.find("p")
            description = desc_tag.get_text(strip=True) if desc_tag else ""
            if not description:
                description = container.get_text(separator=" ", strip=True)[:300]

            # Date from time tag or text
            time_tag = container.find("time")
            published = time_tag.get("datetime", time_tag.get_text(strip=True)) if time_tag else ""

            combined_text = f"{title} {description}"
            category = classify_category(combined_text, default_category)
            deadline = extract_deadline(combined_text)

            if title and href and len(title) > 3:
                opportunities.append({
                    "title": title[:200],
                    "description": description[:500],
                    "url": href,
                    "source": source_name,
                    "category": category,
                    "deadline": deadline,
                    "published": published,
                    "scraped_at": datetime.now(timezone.utc).isoformat(),
                })
    else:
        # Fallback: grab all meaningful links
        for link_tag in soup.find_all("a", href=True)[:30]:
            href = link_tag["href"]
            text = link_tag.get_text(strip=True)
            if not text or len(text) < 10:
                continue
            if not href.startswith("http"):
                from urllib.parse import urljoin
                href = urljoin(url, href)
            # Skip navigation/footer links
            if any(skip in href.lower() for skip in ["#", "javascript:", "login", "signup", "facebook.com", "twitter.com", "instagram.com"]):
                continue

            category = classify_category(text, default_category)
            opportunities.append({
                "title": text[:200],
                "description": "",
                "url": href,
                "source": source_name,
                "category": category,
                "deadline": None,
                "published": "",
                "scraped_at": datetime.now(timezone.utc).isoformat(),
            })

    return opportunities


def scrape_source(source_key, source_config):
    """Scrape all URLs for a given source."""
    all_opps = []
    source_name = source_config["name"]
    source_type = source_config["type"]
    default_cat = source_config["default_category"]

    print(f"[*] Scraping {source_name}...")

    for url in source_config["urls"]:
        if source_type == "rss":
            opps = scrape_rss(url, source_name, default_cat)
        elif source_type == "html":
            opps = scrape_html_page(url, source_name, default_cat)
        elif source_type == "mixed":
            # Try RSS first, fall back to HTML
            opps = scrape_rss(url, source_name, default_cat)
            if not opps:
                opps = scrape_html_page(url, source_name, default_cat)
        else:
            opps = []

        all_opps.extend(opps)
        print(f"  [{source_name}] {url} -> {len(opps)} items")
        time.sleep(DELAY_BETWEEN_SOURCES)

    return all_opps


def deduplicate(opportunities, existing):
    """De-duplicate by URL. Returns only new opportunities."""
    existing_urls = {opp["url"] for opp in existing}
    new_opps = []
    seen = set()
    for opp in opportunities:
        url = opp["url"]
        if url not in existing_urls and url not in seen:
            new_opps.append(opp)
            seen.add(url)
    return new_opps


def load_existing():
    """Load existing opportunities from storage."""
    if OUTPUT_FILE.exists():
        try:
            with open(OUTPUT_FILE, "r") as f:
                data = json.load(f)
                return data if isinstance(data, list) else data.get("opportunities", [])
        except (json.JSONDecodeError, IOError):
            return []
    return []


def save_opportunities(opportunities):
    """Save opportunities to JSON file."""
    # Sort by deadline (items with deadlines first, then by deadline date)
    def sort_key(opp):
        dl = opp.get("deadline")
        if dl:
            return (0, dl)
        return (1, opp.get("scraped_at", ""))

    opportunities.sort(key=sort_key)

    # Trim to max
    opportunities = opportunities[:MAX_OPPORTUNITIES]

    with open(OUTPUT_FILE, "w") as f:
        json.dump(opportunities, f, indent=2, ensure_ascii=False)

    print(f"[+] Saved {len(opportunities)} opportunities to {OUTPUT_FILE}")
    return opportunities


def get_urgent_opportunities(opportunities):
    """Find opportunities with deadlines within DEADLINE_ALERT_DAYS days."""
    now = datetime.now(timezone.utc).date()
    cutoff = now + timedelta(days=DEADLINE_ALERT_DAYS)
    urgent = []

    for opp in opportunities:
        dl = opp.get("deadline")
        if dl:
            try:
                deadline_date = datetime.strptime(dl, "%Y-%m-%d").date()
                if now <= deadline_date <= cutoff:
                    days_left = (deadline_date - now).days
                    opp["_days_left"] = days_left
                    urgent.append(opp)
            except ValueError:
                continue

    urgent.sort(key=lambda x: x.get("_days_left", 999))
    return urgent


def send_telegram_alert(new_opportunities):
    """Send Telegram alert for new opportunities with upcoming deadlines."""
    bot_token = os.environ.get("TELEGRAM_BOT_TOKEN")
    chat_id = os.environ.get("TELEGRAM_CHAT_ID")

    if not bot_token or not chat_id:
        print("[WARN] Telegram credentials not set. Skipping notification.")
        return

    urgent = get_urgent_opportunities(new_opportunities)
    if not urgent:
        print("[*] No urgent new opportunities to alert on.")
        return

    # Build message
    lines = ["🇵🇷 *PR Opportunities Alert*\n"]
    for opp in urgent[:10]:
        days = opp.get("_days_left", "?")
        emoji = "🔴" if isinstance(days, int) and days <= 7 else "🟡" if isinstance(days, int) and days <= 14 else "🟢"
        cat_emoji = {"grant": "💰", "program": "🎓", "event": "📅", "incentive": "🏛️"}.get(opp["category"], "📋")
        lines.append(
            f"{emoji}{cat_emoji} *{opp['title'][:80]}*\n"
            f"   Source: {opp['source']} | Deadline: {opp['deadline']} ({days}d)\n"
            f"   [Link]({opp['url']})\n"
        )

    if len(urgent) > 10:
        lines.append(f"\n_...and {len(urgent) - 10} more. Check dashboard._")

    message = "\n".join(lines)

    try:
        url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
        payload = {
            "chat_id": chat_id,
            "text": message,
            "parse_mode": "Markdown",
            "disable_web_page_preview": True,
        }
        resp = requests.post(url, json=payload, timeout=10)
        if resp.status_code == 200:
            print(f"[+] Telegram alert sent: {len(urgent)} urgent opportunities")
        else:
            print(f"[WARN] Telegram API returned {resp.status_code}: {resp.text[:200]}")
    except Exception as e:
        print(f"[WARN] Telegram alert failed: {e}")


def run():
    """Main scrape run."""
    print(f"=== PR Opportunities Scraper ===")
    print(f"    Time: {datetime.now(timezone.utc).isoformat()}")
    print()

    existing = load_existing()
    print(f"[*] Existing opportunities: {len(existing)}")

    all_new = []
    for source_key, source_config in SOURCES.items():
        try:
            opps = scrape_source(source_key, source_config)
            all_new.extend(opps)
        except Exception as e:
            print(f"  [ERROR] {source_key} failed: {e}")

    print(f"\n[*] Total scraped: {len(all_new)}")

    # De-duplicate against existing
    truly_new = deduplicate(all_new, existing)
    print(f"[*] New (de-duped): {len(truly_new)}")

    # Merge and save
    combined = truly_new + existing
    saved = save_opportunities(combined)

    return truly_new, saved


def main():
    parser = argparse.ArgumentParser(description="PR Opportunities Scraper")
    parser.add_argument("--run", action="store_true", help="Run the scraper")
    parser.add_argument("--notify", action="store_true", help="Send Telegram alerts for urgent opportunities")
    parser.add_argument("--stats", action="store_true", help="Show stats on stored opportunities")
    args = parser.parse_args()

    if args.stats:
        existing = load_existing()
        print(f"Total: {len(existing)}")
        cats = {}
        sources = {}
        for opp in existing:
            cats[opp.get("category", "unknown")] = cats.get(opp.get("category", "unknown"), 0) + 1
            sources[opp.get("source", "unknown")] = sources.get(opp.get("source", "unknown"), 0) + 1
        print("By category:", json.dumps(cats, indent=2))
        print("By source:", json.dumps(sources, indent=2))
        urgent = get_urgent_opportunities(existing)
        print(f"Urgent (within {DEADLINE_ALERT_DAYS} days): {len(urgent)}")
        return

    if args.run:
        new_opps, all_opps = run()
        if args.notify and new_opps:
            send_telegram_alert(new_opps)
        print("\n[DONE]")
    else:
        parser.print_help()


if __name__ == "__main__":
    main()

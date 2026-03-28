#!/usr/bin/env python3
"""
YouTuber Outreach Bot - Find micro-influencers and generate personalized outreach emails.

Usage:
    python3 youtuber_outreach.py --search "shopify theme review"
    python3 youtuber_outreach.py --import channels.csv
    python3 youtuber_outreach.py --list
    python3 youtuber_outreach.py --generate
    python3 youtuber_outreach.py --generate --template shopify
    python3 youtuber_outreach.py --log
    python3 youtuber_outreach.py --log --status replied
"""

import argparse
import csv
import json
import os
import re
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Optional

import requests

# ──────────────────────────────────────────────
# Config
# ──────────────────────────────────────────────

OUTREACH_LOG = Path(os.path.expanduser("~/behique/Ceiba/news/outreach_log.json"))
CHANNELS_DB = Path(os.path.expanduser("~/behique/Ceiba/news/channels_db.json"))
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept-Language": "en-US,en;q=0.9",
}

MIN_SUBS = 1_000
MAX_SUBS = 100_000


# ──────────────────────────────────────────────
# Email Templates
# ──────────────────────────────────────────────

TEMPLATES = {
    "shopify": {
        "subject": "Free Shopify theme for your channel",
        "body": (
            "Hey {name},\n\n"
            "I saw your video about {recent_topic}. Really solid breakdown.\n\n"
            "I built a Shopify theme called Empire and I'd love to give you free access "
            "($49.99 value). If you like it, maybe feature it in a future video? "
            "No pressure at all.\n\n"
            "Let me know if you're interested and I'll send it over.\n\n"
            "Best,\nKalani"
        ),
    },
    "ai_guide": {
        "subject": "Free AI guide for you",
        "body": (
            "Hey {name},\n\n"
            "Loved your content about {recent_topic}. Really good stuff.\n\n"
            "I wrote a guide on building AI systems with zero cloud costs. "
            "Happy to send you a free copy ($19.99 value). "
            "If it resonates, a mention would mean the world.\n\n"
            "Either way, keep making great content.\n\n"
            "Best,\nKalani"
        ),
    },
    "ecommerce": {
        "subject": "Free product for honest feedback",
        "body": (
            "Hey {name},\n\n"
            "I've been watching your videos on {recent_topic} and they're really helpful.\n\n"
            "I'm a builder from Puerto Rico making digital products for ecommerce sellers. "
            "Would love to send you free access to any of my tools in exchange for "
            "honest feedback. No strings attached.\n\n"
            "Interested?\n\n"
            "Best,\nKalani"
        ),
    },
    "productivity": {
        "subject": "Built something your audience might like",
        "body": (
            "Hey {name},\n\n"
            "Your video on {recent_topic} was exactly the kind of content I wish "
            "I had found earlier.\n\n"
            "I built an automation toolkit for creators who want to save time on "
            "repetitive tasks. Would love to give you free access and get your take on it.\n\n"
            "If it's useful, maybe worth a mention. If not, no worries at all.\n\n"
            "Best,\nKalani"
        ),
    },
    "coding": {
        "subject": "Free dev tool for your channel",
        "body": (
            "Hey {name},\n\n"
            "Just watched your video on {recent_topic}. Clean explanation.\n\n"
            "I'm building dev tools for AI-powered workflows and I'd love to get "
            "your feedback. Happy to give you full free access. "
            "If you think it's worth sharing with your audience, that would be amazing.\n\n"
            "Best,\nKalani"
        ),
    },
    "general": {
        "subject": "Collaboration idea",
        "body": (
            "Hey {name},\n\n"
            "I'm a builder from Puerto Rico making digital products for {niche}. "
            "Would love to send you free access to any of my products in exchange "
            "for honest feedback.\n\n"
            "Your video on {recent_topic} caught my eye. "
            "Let me know if you'd be open to it.\n\n"
            "Best,\nKalani"
        ),
    },
}


# ──────────────────────────────────────────────
# Persistence helpers
# ──────────────────────────────────────────────

def load_json(path: Path, default=None):
    if default is None:
        default = []
    if path.exists():
        with open(path, "r") as f:
            return json.load(f)
    return default


def save_json(path: Path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def load_channels() -> list[dict]:
    return load_json(CHANNELS_DB, [])


def save_channels(channels: list[dict]):
    save_json(CHANNELS_DB, channels)


def load_outreach_log() -> list[dict]:
    return load_json(OUTREACH_LOG, [])


def save_outreach_log(log: list[dict]):
    save_json(OUTREACH_LOG, log)


# ──────────────────────────────────────────────
# YouTube scraping
# ──────────────────────────────────────────────

def parse_sub_count(text: str) -> Optional[int]:
    """Parse subscriber count from strings like '12.3K subscribers', '1.5M subscribers'."""
    text = text.strip().lower().replace(",", "")
    match = re.search(r"([\d.]+)\s*(k|m|b)?\s*subscriber", text)
    if not match:
        return None
    num = float(match.group(1))
    multiplier = match.group(2)
    if multiplier == "k":
        return int(num * 1_000)
    elif multiplier == "m":
        return int(num * 1_000_000)
    elif multiplier == "b":
        return int(num * 1_000_000_000)
    return int(num)


def extract_channel_id_from_url(url: str) -> Optional[str]:
    """Extract channel ID or handle from a YouTube URL."""
    patterns = [
        r"youtube\.com/channel/([a-zA-Z0-9_-]+)",
        r"youtube\.com/@([a-zA-Z0-9_.-]+)",
        r"youtube\.com/c/([a-zA-Z0-9_.-]+)",
        r"youtube\.com/user/([a-zA-Z0-9_.-]+)",
    ]
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    return None


def scrape_channel_page(url: str) -> dict:
    """Scrape basic info from a YouTube channel page."""
    info = {
        "url": url,
        "name": None,
        "subscriber_count": None,
        "email": None,
        "recent_videos": [],
    }

    try:
        resp = requests.get(url, headers=HEADERS, timeout=15)
        resp.raise_for_status()
        html = resp.text

        # Channel name from <title>
        title_match = re.search(r"<title>(.+?)</title>", html)
        if title_match:
            name = title_match.group(1).replace(" - YouTube", "").strip()
            info["name"] = name

        # Subscriber count from meta or page content
        sub_match = re.search(r'"subscriberCountText":\s*\{"simpleText":\s*"([^"]+)"', html)
        if sub_match:
            info["subscriber_count"] = parse_sub_count(sub_match.group(1))

        # Try to find business email
        email_match = re.findall(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', html)
        # Filter out YouTube/Google internal emails
        filtered = [e for e in email_match if not any(
            d in e.lower() for d in ["youtube.com", "google.com", "gstatic.com", "googleapis.com"]
        )]
        if filtered:
            info["email"] = filtered[0]

        # Recent video titles
        video_titles = re.findall(r'"title":\s*\{"runs":\s*\[\{"text":\s*"([^"]{5,100})"', html)
        # Deduplicate while preserving order
        seen = set()
        unique_titles = []
        for t in video_titles:
            if t not in seen:
                seen.add(t)
                unique_titles.append(t)
        info["recent_videos"] = unique_titles[:5]

    except requests.RequestException as e:
        print(f"  [!] Failed to scrape {url}: {e}")

    return info


def scrape_about_page(channel_url: str) -> Optional[str]:
    """Try to get business email from the channel's about page."""
    about_url = channel_url.rstrip("/") + "/about"
    try:
        resp = requests.get(about_url, headers=HEADERS, timeout=15)
        resp.raise_for_status()
        html = resp.text

        # Look for business email in about page
        email_match = re.findall(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', html)
        filtered = [e for e in email_match if not any(
            d in e.lower() for d in ["youtube.com", "google.com", "gstatic.com", "googleapis.com"]
        )]
        if filtered:
            return filtered[0]
    except requests.RequestException:
        pass
    return None


def search_youtube_channels(query: str, max_results: int = 20) -> list[str]:
    """
    Search YouTube for channels matching a query.
    Returns a list of channel URLs.
    """
    # Use YouTube search with channel filter
    search_url = f"https://www.youtube.com/results?search_query={requests.utils.quote(query)}&sp=EgIQAg%253D%253D"

    try:
        resp = requests.get(search_url, headers=HEADERS, timeout=15)
        resp.raise_for_status()
        html = resp.text

        # Extract channel URLs from search results
        # Look for channel links in the JSON data embedded in the page
        channel_ids = re.findall(r'"channelId":\s*"(UC[a-zA-Z0-9_-]+)"', html)
        handles = re.findall(r'"canonicalBaseUrl":\s*"(/[@a-zA-Z0-9_.-]+)"', html)

        urls = set()

        # Prefer handles (cleaner URLs)
        for handle in handles:
            if handle.startswith("/@"):
                urls.add(f"https://www.youtube.com{handle}")

        # Fallback to channel IDs
        for cid in channel_ids:
            urls.add(f"https://www.youtube.com/channel/{cid}")

        return list(urls)[:max_results]

    except requests.RequestException as e:
        print(f"[!] Search failed: {e}")
        return []


# ──────────────────────────────────────────────
# Core logic
# ──────────────────────────────────────────────

def discover_channels(query: str, max_results: int = 20):
    """Search YouTube for channels and save them to the database."""
    print(f"Searching YouTube for: {query}")
    print(f"Looking for channels with {MIN_SUBS:,}-{MAX_SUBS:,} subscribers...\n")

    urls = search_youtube_channels(query, max_results=max_results)
    if not urls:
        print("No channels found. Try a different search query.")
        return

    print(f"Found {len(urls)} channel URLs. Scraping details...\n")

    existing = load_channels()
    existing_urls = {c["url"] for c in existing}
    new_count = 0

    for i, url in enumerate(urls, 1):
        if url in existing_urls:
            print(f"  [{i}/{len(urls)}] Already tracked: {url}")
            continue

        print(f"  [{i}/{len(urls)}] Scraping: {url}")
        info = scrape_channel_page(url)

        # Try about page for email if not found
        if not info["email"]:
            email = scrape_about_page(url)
            if email:
                info["email"] = email

        # Filter by subscriber count
        subs = info["subscriber_count"]
        if subs is not None:
            if subs < MIN_SUBS:
                print(f"    Skipping: {subs:,} subs (under {MIN_SUBS:,})")
                continue
            if subs > MAX_SUBS:
                print(f"    Skipping: {subs:,} subs (over {MAX_SUBS:,})")
                continue
            print(f"    {info['name']} - {subs:,} subs", end="")
        else:
            print(f"    {info['name'] or 'Unknown'} - subs unknown", end="")

        if info["email"]:
            print(f" - email: {info['email']}")
        else:
            print(" - no email found")

        info["discovered_at"] = datetime.now().isoformat()
        info["search_query"] = query
        existing.append(info)
        new_count += 1

        # Rate limit
        time.sleep(1.5)

    save_channels(existing)
    print(f"\nDone. Added {new_count} new channels. Total tracked: {len(existing)}")


def import_channels_csv(csv_path: str):
    """Import channels from a CSV file. Expected columns: url (required), name, email."""
    path = Path(csv_path)
    if not path.exists():
        print(f"File not found: {csv_path}")
        return

    existing = load_channels()
    existing_urls = {c["url"] for c in existing}
    new_count = 0

    with open(path, "r") as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    print(f"Importing {len(rows)} channels from {csv_path}...\n")

    for row in rows:
        url = row.get("url", "").strip()
        if not url:
            continue
        if url in existing_urls:
            print(f"  Already tracked: {url}")
            continue

        # Normalize URL
        if not url.startswith("http"):
            url = f"https://www.youtube.com/{url}"

        print(f"  Scraping: {url}")
        info = scrape_channel_page(url)

        # Override with CSV data if provided
        if row.get("name"):
            info["name"] = row["name"]
        if row.get("email"):
            info["email"] = row["email"]

        # Try about page for email if still missing
        if not info["email"]:
            email = scrape_about_page(url)
            if email:
                info["email"] = email

        info["discovered_at"] = datetime.now().isoformat()
        info["search_query"] = "csv_import"
        existing.append(info)
        new_count += 1

        time.sleep(1)

    save_channels(existing)
    print(f"\nDone. Added {new_count} new channels. Total tracked: {len(existing)}")


def list_channels():
    """Show all tracked channels."""
    channels = load_channels()
    if not channels:
        print("No channels tracked yet. Run --search or --import first.")
        return

    # Sort: channels with email first, then by sub count
    with_email = [c for c in channels if c.get("email")]
    without_email = [c for c in channels if not c.get("email")]

    print(f"Tracked channels: {len(channels)} total, {len(with_email)} with email\n")
    print(f"{'Name':<30} {'Subs':<12} {'Email':<35} {'Videos'}")
    print("-" * 100)

    for c in with_email + without_email:
        name = (c.get("name") or "Unknown")[:29]
        subs = f"{c['subscriber_count']:,}" if c.get("subscriber_count") else "?"
        email = (c.get("email") or "none")[:34]
        videos = len(c.get("recent_videos", []))
        print(f"{name:<30} {subs:<12} {email:<35} {videos} videos")


def generate_emails(template_key: Optional[str] = None, niche: str = "digital products"):
    """Generate personalized outreach emails for all channels with emails."""
    channels = load_channels()
    outreach_log = load_outreach_log()
    already_sent = {entry["channel_url"] for entry in outreach_log}

    candidates = [
        c for c in channels
        if c.get("email") and c["url"] not in already_sent
    ]

    if not candidates:
        print("No new channels with emails to generate outreach for.")
        if not any(c.get("email") for c in channels):
            print("None of your tracked channels have emails yet.")
        else:
            print("All channels with emails have already been processed.")
        return

    # Pick template
    if template_key and template_key in TEMPLATES:
        template = TEMPLATES[template_key]
    else:
        template_key = "general"
        template = TEMPLATES["general"]

    print(f"Generating emails for {len(candidates)} channels using '{template_key}' template\n")
    print("=" * 80)

    generated = []

    for c in candidates:
        name = c.get("name", "there")
        # Use first name if possible
        first_name = name.split()[0] if name else "there"

        # Pick a recent video topic for personalization
        recent_topic = "your latest content"
        if c.get("recent_videos"):
            recent_topic = c["recent_videos"][0]

        # Format the email
        body = template["body"].format(
            name=first_name,
            recent_topic=recent_topic,
            niche=niche,
        )
        subject = template["subject"]

        print(f"\nTo: {c['email']}")
        print(f"Subject: {subject}")
        print(f"Channel: {name}")
        print("-" * 40)
        print(body)
        print("=" * 80)

        entry = {
            "channel_name": name,
            "channel_url": c["url"],
            "email": c["email"],
            "template": template_key,
            "subject": subject,
            "body": body,
            "generated_at": datetime.now().isoformat(),
            "status": "generated",
        }
        generated.append(entry)

    # Save to outreach log
    outreach_log.extend(generated)
    save_outreach_log(outreach_log)
    print(f"\nGenerated {len(generated)} emails. Saved to outreach log.")
    print(f"Log location: {OUTREACH_LOG}")


def show_outreach_log(status_filter: Optional[str] = None):
    """Show outreach history."""
    log = load_outreach_log()
    if not log:
        print("Outreach log is empty. Run --generate first.")
        return

    if status_filter:
        log = [e for e in log if e.get("status") == status_filter]
        if not log:
            print(f"No entries with status '{status_filter}'.")
            return

    # Stats
    statuses = {}
    for entry in log:
        s = entry.get("status", "unknown")
        statuses[s] = statuses.get(s, 0) + 1

    print(f"Outreach log: {len(log)} entries")
    print(f"Status breakdown: {', '.join(f'{k}: {v}' for k, v in statuses.items())}\n")

    print(f"{'Channel':<25} {'Email':<30} {'Template':<12} {'Status':<12} {'Date'}")
    print("-" * 95)

    for entry in log:
        name = (entry.get("channel_name") or "?")[:24]
        email = (entry.get("email") or "?")[:29]
        template = (entry.get("template") or "?")[:11]
        status = (entry.get("status") or "?")[:11]
        date = entry.get("generated_at", "?")[:10]
        print(f"{name:<25} {email:<30} {template:<12} {status:<12} {date}")


def update_status(channel_name: str, new_status: str):
    """Update the status of an outreach entry."""
    log = load_outreach_log()
    updated = False
    for entry in log:
        if channel_name.lower() in (entry.get("channel_name") or "").lower():
            old_status = entry.get("status")
            entry["status"] = new_status
            entry["status_updated_at"] = datetime.now().isoformat()
            print(f"Updated '{entry['channel_name']}': {old_status} -> {new_status}")
            updated = True

    if updated:
        save_outreach_log(log)
    else:
        print(f"No matching channel found for '{channel_name}'.")


# ──────────────────────────────────────────────
# CLI
# ──────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="YouTuber Outreach Bot. Find micro-influencers and generate personalized emails.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Examples:\n"
            '  python3 youtuber_outreach.py --search "shopify theme review"\n'
            "  python3 youtuber_outreach.py --import channels.csv\n"
            "  python3 youtuber_outreach.py --list\n"
            "  python3 youtuber_outreach.py --generate --template shopify\n"
            "  python3 youtuber_outreach.py --log\n"
            '  python3 youtuber_outreach.py --update "TechGuy" --status sent\n'
        ),
    )

    parser.add_argument("--search", type=str, help="Search YouTube for channels in a niche")
    parser.add_argument("--max", type=int, default=20, help="Max channels to find (default: 20)")
    parser.add_argument("--import", dest="import_csv", type=str, help="Import channels from CSV")
    parser.add_argument("--list", action="store_true", help="List all tracked channels")
    parser.add_argument("--generate", action="store_true", help="Generate outreach emails")
    parser.add_argument(
        "--template",
        choices=list(TEMPLATES.keys()),
        default=None,
        help="Email template to use (default: general)",
    )
    parser.add_argument("--niche", type=str, default="digital products", help="Niche for template fill")
    parser.add_argument("--log", action="store_true", help="Show outreach history")
    parser.add_argument("--status", type=str, help="Filter log by status, or set status with --update")
    parser.add_argument("--update", type=str, help="Update status for a channel (use with --status)")
    parser.add_argument("--templates", action="store_true", help="List available email templates")

    args = parser.parse_args()

    if args.templates:
        print("Available templates:\n")
        for key, tmpl in TEMPLATES.items():
            print(f"  {key:<15} {tmpl['subject']}")
        return

    if args.search:
        discover_channels(args.search, max_results=args.max)
    elif args.import_csv:
        import_channels_csv(args.import_csv)
    elif args.list:
        list_channels()
    elif args.generate:
        generate_emails(template_key=args.template, niche=args.niche)
    elif args.log:
        show_outreach_log(status_filter=args.status)
    elif args.update:
        if not args.status:
            print("Use --status with --update. Example: --update 'TechGuy' --status sent")
        else:
            update_status(args.update, args.status)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
beehiiv_sync.py — Beehiiv API integration for Behike newsletter.

Env vars:
    BEEHIIV_API_KEY         - Beehiiv API key
    BEEHIIV_PUBLICATION_ID  - Beehiiv publication ID

CLI:
    python3 beehiiv_sync.py stats
    python3 beehiiv_sync.py subscribers
    python3 beehiiv_sync.py draft "Title" content.md
    python3 beehiiv_sync.py schedule <post_id> "2026-04-01T18:00:00Z"
"""

import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

try:
    import requests
except ImportError:
    print("[beehiiv] requests not installed — run: pip install requests")
    sys.exit(1)

# ── Config ─────────────────────────────────────────────────────────────────────

BASE_URL = "https://api.beehiiv.com/v2"
API_KEY = os.environ.get("BEEHIIV_API_KEY", "")
PUB_ID = os.environ.get("BEEHIIV_PUBLICATION_ID", "")
LOGS_DIR = Path(__file__).parent / "logs"


def _headers():
    return {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json",
    }


def _check_keys():
    if not API_KEY or not PUB_ID:
        print("[beehiiv] BEEHIIV_API_KEY or BEEHIIV_PUBLICATION_ID not set.")
        print("          Set them in your environment to enable Beehiiv sync.")
        return False
    return True


def _api_get(path, params=None):
    url = f"{BASE_URL}/publications/{PUB_ID}{path}"
    resp = requests.get(url, headers=_headers(), params=params, timeout=30)
    resp.raise_for_status()
    return resp.json()


def _api_post(path, payload):
    url = f"{BASE_URL}/publications/{PUB_ID}{path}"
    resp = requests.post(url, headers=_headers(), json=payload, timeout=30)
    resp.raise_for_status()
    return resp.json()


def _api_put(path, payload):
    url = f"{BASE_URL}/publications/{PUB_ID}{path}"
    resp = requests.put(url, headers=_headers(), json=payload, timeout=30)
    resp.raise_for_status()
    return resp.json()


# ── Public API ─────────────────────────────────────────────────────────────────

def sync_subscribers():
    """Pull subscriber count and recent signups."""
    if not _check_keys():
        return {"total": 0, "recent": [], "error": "no_api_key"}

    try:
        data = _api_get("/subscriptions", params={"limit": 20, "order_by": "created"})
        subs = data.get("data", [])
        total = data.get("total_results", len(subs))

        recent = []
        for s in subs:
            recent.append({
                "email": s.get("email", ""),
                "status": s.get("status", ""),
                "created": s.get("created", ""),
                "utm_source": s.get("utm_source", ""),
            })

        result = {"total": total, "recent": recent}
        _log("subscribers", result)
        return result

    except requests.RequestException as e:
        print(f"[beehiiv] API error: {e}")
        return {"total": 0, "recent": [], "error": str(e)}


def create_post(title, content, status="draft"):
    """Create a newsletter draft on Beehiiv.

    Args:
        title: Post title
        content: HTML content body
        status: 'draft' or 'confirmed' (confirmed = ready to send)

    Returns:
        dict with post_id and web_url, or error info
    """
    if not _check_keys():
        print("[beehiiv] Skipping remote push — saving locally only.")
        return {"post_id": None, "error": "no_api_key"}

    try:
        payload = {
            "title": title,
            "subtitle": "",
            "status": status,
            "content_html": content,
        }
        data = _api_post("/posts", payload)
        post = data.get("data", {})
        result = {
            "post_id": post.get("id", ""),
            "web_url": post.get("web_url", ""),
            "status": post.get("status", ""),
            "title": title,
        }
        _log("post_created", result)
        print(f"[beehiiv] Draft created: {result['post_id']}")
        return result

    except requests.RequestException as e:
        print(f"[beehiiv] API error creating post: {e}")
        return {"post_id": None, "error": str(e)}


def schedule_post(post_id, send_at):
    """Schedule a post for sending.

    Args:
        post_id: Beehiiv post ID
        send_at: ISO 8601 datetime string (e.g. '2026-04-01T18:00:00Z')
    """
    if not _check_keys():
        return {"error": "no_api_key"}

    try:
        payload = {
            "status": "confirmed",
            "send_at": send_at,
        }
        data = _api_put(f"/posts/{post_id}", payload)
        post = data.get("data", {})
        result = {
            "post_id": post_id,
            "scheduled_for": send_at,
            "status": post.get("status", "scheduled"),
        }
        _log("post_scheduled", result)
        print(f"[beehiiv] Post {post_id} scheduled for {send_at}")
        return result

    except requests.RequestException as e:
        print(f"[beehiiv] API error scheduling: {e}")
        return {"error": str(e)}


def get_stats():
    """Pull publication stats: open rate, click rate, subscriber growth."""
    if not _check_keys():
        return {"error": "no_api_key"}

    try:
        # Get recent posts for engagement metrics
        posts_data = _api_get("/posts", params={"limit": 10, "status": "confirmed"})
        posts = posts_data.get("data", [])

        total_opens = 0
        total_clicks = 0
        total_delivered = 0
        post_stats = []

        for p in posts:
            stats = p.get("stats", {})
            opens = stats.get("email", {}).get("opens", 0)
            clicks = stats.get("email", {}).get("clicks", 0)
            delivered = stats.get("email", {}).get("delivered", 0)
            total_opens += opens
            total_clicks += clicks
            total_delivered += delivered
            post_stats.append({
                "title": p.get("title", ""),
                "opens": opens,
                "clicks": clicks,
                "delivered": delivered,
                "open_rate": round(opens / delivered * 100, 1) if delivered else 0,
                "click_rate": round(clicks / delivered * 100, 1) if delivered else 0,
            })

        # Get subscriber count
        subs_data = _api_get("/subscriptions", params={"limit": 1})
        total_subs = subs_data.get("total_results", 0)

        result = {
            "total_subscribers": total_subs,
            "posts_analyzed": len(posts),
            "avg_open_rate": round(total_opens / total_delivered * 100, 1) if total_delivered else 0,
            "avg_click_rate": round(total_clicks / total_delivered * 100, 1) if total_delivered else 0,
            "total_opens": total_opens,
            "total_clicks": total_clicks,
            "recent_posts": post_stats,
        }
        _log("stats", result)
        return result

    except requests.RequestException as e:
        print(f"[beehiiv] API error fetching stats: {e}")
        return {"error": str(e)}


# ── Logging ────────────────────────────────────────────────────────────────────

def _log(event, data):
    LOGS_DIR.mkdir(parents=True, exist_ok=True)
    log_file = LOGS_DIR / "beehiiv.log"
    entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "event": event,
        "data": data,
    }
    with open(log_file, "a") as f:
        f.write(json.dumps(entry) + "\n")


# ── CLI ────────────────────────────────────────────────────────────────────────

def _print_stats(stats):
    if "error" in stats and stats["error"] == "no_api_key":
        return
    print()
    print("=" * 50)
    print("  BEHIKE NEWSLETTER STATS")
    print("=" * 50)
    print(f"  Subscribers:    {stats.get('total_subscribers', '?')}")
    print(f"  Avg Open Rate:  {stats.get('avg_open_rate', '?')}%")
    print(f"  Avg Click Rate: {stats.get('avg_click_rate', '?')}%")
    print(f"  Total Opens:    {stats.get('total_opens', '?')}")
    print(f"  Total Clicks:   {stats.get('total_clicks', '?')}")
    print()
    for p in stats.get("recent_posts", []):
        print(f"  [{p['open_rate']}% open] {p['title']}")
    print()


def _print_subscribers(subs):
    if "error" in subs and subs["error"] == "no_api_key":
        return
    print()
    print(f"  Total subscribers: {subs['total']}")
    print()
    for s in subs.get("recent", []):
        print(f"  {s['email']:40s}  {s['status']:10s}  {s['created']}")
    print()


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(0)

    cmd = sys.argv[1].lower()

    if cmd == "stats":
        stats = get_stats()
        _print_stats(stats)

    elif cmd == "subscribers":
        subs = sync_subscribers()
        _print_subscribers(subs)

    elif cmd == "draft":
        if len(sys.argv) < 4:
            print("Usage: python3 beehiiv_sync.py draft \"Title\" content.md")
            sys.exit(1)
        title = sys.argv[2]
        content_path = Path(sys.argv[3])
        if not content_path.exists():
            print(f"[beehiiv] File not found: {content_path}")
            sys.exit(1)
        content = content_path.read_text()
        result = create_post(title, content)
        print(json.dumps(result, indent=2))

    elif cmd == "schedule":
        if len(sys.argv) < 4:
            print("Usage: python3 beehiiv_sync.py schedule <post_id> \"2026-04-01T18:00:00Z\"")
            sys.exit(1)
        post_id = sys.argv[2]
        send_at = sys.argv[3]
        result = schedule_post(post_id, send_at)
        print(json.dumps(result, indent=2))

    else:
        print(f"Unknown command: {cmd}")
        print(__doc__)
        sys.exit(1)


if __name__ == "__main__":
    main()

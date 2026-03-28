#!/usr/bin/env python3
"""
Publishing daemon. Run via cron every hour.
Checks for due posts, prepares publish packages, sends Telegram notifications.

Cron setup:
    crontab -e
    0 * * * * cd /Users/kalani/behique/bios/publisher && python3 publish_daemon.py

Env vars:
    TELEGRAM_BOT_TOKEN   - Bot token from @BotFather
    TELEGRAM_CHAT_ID     - Your chat ID (get from @userinfobot)
"""

import json
import os
import sys
import urllib.request
import urllib.parse
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

PUBLISHER_DIR = Path(__file__).parent
LOGS_DIR = PUBLISHER_DIR / "logs"
DEFAULT_TZ = "America/Puerto_Rico"

# Ensure we can import sibling modules
sys.path.insert(0, str(PUBLISHER_DIR))


def send_telegram(message: str) -> bool:
    """Send a notification via Telegram bot."""
    token = os.environ.get("TELEGRAM_BOT_TOKEN")
    chat_id = os.environ.get("TELEGRAM_CHAT_ID")

    if not token or not chat_id:
        print("  Telegram not configured (set TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID)")
        return False

    url = f"https://api.telegram.org/bot{token}/sendMessage"
    data = urllib.parse.urlencode({
        "chat_id": chat_id,
        "text": message,
        "parse_mode": "Markdown",
    }).encode("utf-8")

    try:
        req = urllib.request.Request(url, data=data)
        with urllib.request.urlopen(req, timeout=10) as resp:
            return resp.status == 200
    except Exception as e:
        print(f"  Telegram send failed: {e}")
        return False


def log_event(event_type: str, data: dict):
    """Log an event to the daily log file."""
    LOGS_DIR.mkdir(parents=True, exist_ok=True)
    tz = ZoneInfo(DEFAULT_TZ)
    now = datetime.now(tz)

    log_file = LOGS_DIR / f"daemon-{now.strftime('%Y-%m-%d')}.jsonl"

    entry = {
        "timestamp": now.isoformat(),
        "event": event_type,
        **data,
    }

    with open(log_file, "a") as f:
        f.write(json.dumps(entry) + "\n")


def run():
    """Main daemon loop. Called by cron."""
    from scheduler import get_due, mark_published, mark_failed

    tz = ZoneInfo(DEFAULT_TZ)
    now = datetime.now(tz)

    log_event("daemon_start", {"time": now.isoformat()})

    due = get_due()

    if not due:
        log_event("no_due_posts", {})
        return

    print(f"[{now.strftime('%H:%M')}] {len(due)} post(s) due")
    log_event("posts_due", {"count": len(due)})

    for entry in due:
        post_id = entry["id"]
        platform = entry["platform"]
        filename = Path(entry["file"]).name

        print(f"  Processing: [{post_id}] {platform} - {filename}")

        try:
            # Prepare the publish package based on platform
            if platform in ("instagram", "instagram-es"):
                from instagram import prepare_post
                post_data = prepare_post(entry)
                title = post_data.get("title", filename)
                msg = (
                    f"*Post ready for Instagram*\n"
                    f"Title: {title}\n"
                    f"Caption copied to clipboard.\n"
                    f"File: `{filename}`"
                )

            elif platform in ("youtube", "youtube-shorts", "youtube-shorts-es"):
                from youtube import prepare_upload
                video_data = prepare_upload(entry)
                title = video_data.get("title", filename)
                msg = (
                    f"*Video ready for YouTube*\n"
                    f"Title: {title}\n"
                    f"Upload instructions saved.\n"
                    f"File: `{filename}`"
                )

            else:
                # Generic platform: read content preview
                content_path = Path(entry["file"])
                if content_path.exists():
                    raw = content_path.read_text()
                    # Get first heading or first line
                    import re
                    title_match = re.search(r"^#\s+(.+)", raw, re.MULTILINE)
                    title = title_match.group(1) if title_match else filename
                else:
                    title = filename

                msg = (
                    f"*Post ready for {platform}*\n"
                    f"Title: {title}\n"
                    f"File: `{filename}`"
                )

            # Send Telegram notification
            sent = send_telegram(msg)

            # Mark as published
            mark_published(post_id)

            log_event("post_prepared", {
                "post_id": post_id,
                "platform": platform,
                "file": filename,
                "telegram_sent": sent,
            })

            print(f"    Done. Telegram: {'sent' if sent else 'skipped'}")

        except Exception as e:
            error_msg = str(e)
            mark_failed(post_id, error_msg)
            log_event("post_failed", {
                "post_id": post_id,
                "platform": platform,
                "error": error_msg,
            })
            print(f"    FAILED: {error_msg}")

            # Notify about failure too
            send_telegram(
                f"*Publish FAILED*\n"
                f"Platform: {platform}\n"
                f"File: `{filename}`\n"
                f"Error: {error_msg}"
            )

    log_event("daemon_end", {
        "processed": len(due),
        "time": datetime.now(tz).isoformat(),
    })


if __name__ == "__main__":
    run()

#!/usr/bin/env python3
"""
Email Sender for Behike newsletters.
Reads subscribers, sends HTML newsletters via SMTP.

Usage:
    python tools/email_sender.py --send Ceiba/newsletters/2026-03-22.html
    python tools/email_sender.py --test your@email.com
    python tools/email_sender.py --dry-run Ceiba/newsletters/2026-03-22.html

Env vars required:
    SMTP_HOST, SMTP_PORT, SMTP_USER, SMTP_PASS, FROM_EMAIL, FROM_NAME

Copyright 2026 Behike.
"""

import argparse
import json
import os
import smtplib
import time
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pathlib import Path

from dotenv import load_dotenv

# -- Config --

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

SUBSCRIBERS_FILE = BASE_DIR / "Ceiba" / "email-list" / "subscribers.json"
SENT_LOG_FILE = BASE_DIR / "Ceiba" / "email-list" / "sent_log.json"

SMTP_HOST = os.getenv("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USER = os.getenv("SMTP_USER", "")
SMTP_PASS = os.getenv("SMTP_PASS", "")
FROM_EMAIL = os.getenv("FROM_EMAIL", "")
FROM_NAME = os.getenv("FROM_NAME", "Behike")

# Email capture server URL for unsubscribe links
UNSUBSCRIBE_BASE = os.getenv("UNSUBSCRIBE_BASE", "http://localhost:8082")

# Delay between emails to avoid spam filters
SEND_DELAY = 1.0  # seconds


# -- Helpers --

def load_subscribers() -> list[dict]:
    """Load active subscribers."""
    if not SUBSCRIBERS_FILE.exists():
        print(f"No subscribers file found at {SUBSCRIBERS_FILE}")
        return []
    try:
        data = json.loads(SUBSCRIBERS_FILE.read_text())
        return [s for s in data if s.get("active", True)]
    except (json.JSONDecodeError, IOError) as e:
        print(f"Error loading subscribers: {e}")
        return []


def load_sent_log() -> dict:
    """Load the sent log to track which emails were sent per newsletter."""
    if not SENT_LOG_FILE.exists():
        return {}
    try:
        return json.loads(SENT_LOG_FILE.read_text())
    except (json.JSONDecodeError, IOError):
        return {}


def save_sent_log(log: dict):
    """Save the sent log."""
    SENT_LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    SENT_LOG_FILE.write_text(json.dumps(log, indent=2, default=str))


def load_newsletter(filepath: str) -> str:
    """Load newsletter HTML from file."""
    path = Path(filepath)
    if not path.is_absolute():
        path = BASE_DIR / path
    if not path.exists():
        raise FileNotFoundError(f"Newsletter not found: {path}")
    return path.read_text()


def extract_subject(html: str) -> str:
    """Extract subject line from HTML title tag."""
    import re
    match = re.search(r"<title>(.*?)</title>", html, re.IGNORECASE)
    if match:
        return match.group(1)
    return f"Behike Weekly - {datetime.now().strftime('%B %d, %Y')}"


def personalize_html(html: str, email: str) -> str:
    """Insert unsubscribe link and any personalization."""
    unsubscribe_url = f"{UNSUBSCRIBE_BASE}/unsubscribe?email={email}"
    html = html.replace("{{unsubscribe_url}}", unsubscribe_url)
    html = html.replace("{unsubscribe_url}", unsubscribe_url)
    return html


def send_email(to_email: str, subject: str, html_body: str) -> bool:
    """Send a single email via SMTP."""
    if not SMTP_USER or not SMTP_PASS or not FROM_EMAIL:
        print("ERROR: SMTP credentials not configured. Set SMTP_USER, SMTP_PASS, FROM_EMAIL in .env")
        return False

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = f"{FROM_NAME} <{FROM_EMAIL}>"
    msg["To"] = to_email
    msg["List-Unsubscribe"] = f"<{UNSUBSCRIBE_BASE}/unsubscribe?email={to_email}>"

    # Plain text fallback
    plain_text = f"View this email in your browser. Unsubscribe: {UNSUBSCRIBE_BASE}/unsubscribe?email={to_email}"
    msg.attach(MIMEText(plain_text, "plain"))
    msg.attach(MIMEText(html_body, "html"))

    try:
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_USER, SMTP_PASS)
            server.send_message(msg)
        return True
    except Exception as e:
        print(f"  FAILED to send to {to_email}: {e}")
        return False


# -- CLI Commands --

def cmd_send(newsletter_file: str):
    """Send newsletter to all active subscribers."""
    html = load_newsletter(newsletter_file)
    subject = extract_subject(html)
    subscribers = load_subscribers()

    if not subscribers:
        print("No subscribers to send to.")
        return

    newsletter_id = Path(newsletter_file).stem
    sent_log = load_sent_log()

    if newsletter_id not in sent_log:
        sent_log[newsletter_id] = {"sent": [], "failed": [], "started_at": datetime.utcnow().isoformat()}

    already_sent = set(sent_log[newsletter_id].get("sent", []))
    to_send = [s for s in subscribers if s["email"] not in already_sent]

    if not to_send:
        print(f"All {len(subscribers)} subscribers already received this newsletter.")
        return

    print(f"Newsletter: {newsletter_id}")
    print(f"Subject: {subject}")
    print(f"Subscribers: {len(to_send)} to send ({len(already_sent)} already sent)")
    print(f"Delay: {SEND_DELAY}s between emails")
    print()

    confirm = input("Send? (y/n): ").strip().lower()
    if confirm != "y":
        print("Cancelled.")
        return

    sent_count = 0
    fail_count = 0

    for i, sub in enumerate(to_send, 1):
        email = sub["email"]
        personalized = personalize_html(html, email)
        print(f"  [{i}/{len(to_send)}] Sending to {email}...", end=" ")

        if send_email(email, subject, personalized):
            print("OK")
            sent_log[newsletter_id]["sent"].append(email)
            sent_count += 1
        else:
            sent_log[newsletter_id]["failed"].append(email)
            fail_count += 1

        save_sent_log(sent_log)

        if i < len(to_send):
            time.sleep(SEND_DELAY)

    print(f"\nDone. Sent: {sent_count}, Failed: {fail_count}")


def cmd_test(test_email: str, newsletter_file: str = None):
    """Send to a single test email."""
    if newsletter_file:
        html = load_newsletter(newsletter_file)
    else:
        # Find latest newsletter
        newsletters_dir = BASE_DIR / "Ceiba" / "newsletters"
        html_files = sorted(newsletters_dir.glob("*.html"), reverse=True)
        if not html_files:
            print("No newsletters found. Run newsletter_writer.py --generate first.")
            return
        html = html_files[0].read_text()
        print(f"Using latest newsletter: {html_files[0].name}")

    subject = f"[TEST] {extract_subject(html)}"
    personalized = personalize_html(html, test_email)

    print(f"Sending test to {test_email}...")
    if send_email(test_email, subject, personalized):
        print("Test email sent successfully.")
    else:
        print("Failed to send test email. Check SMTP credentials.")


def cmd_dry_run(newsletter_file: str):
    """Simulate sending without actually sending."""
    html = load_newsletter(newsletter_file)
    subject = extract_subject(html)
    subscribers = load_subscribers()

    print(f"DRY RUN")
    print(f"Newsletter: {Path(newsletter_file).stem}")
    print(f"Subject: {subject}")
    print(f"Total active subscribers: {len(subscribers)}")
    print()

    newsletter_id = Path(newsletter_file).stem
    sent_log = load_sent_log()
    already_sent = set(sent_log.get(newsletter_id, {}).get("sent", []))
    to_send = [s for s in subscribers if s["email"] not in already_sent]

    print(f"Would send to {len(to_send)} subscribers:")
    for sub in to_send[:10]:
        print(f"  {sub['email']} (source: {sub.get('source', 'unknown')})")
    if len(to_send) > 10:
        print(f"  ... and {len(to_send) - 10} more")

    estimated_time = len(to_send) * SEND_DELAY
    print(f"\nEstimated send time: {estimated_time:.0f} seconds")


# -- Main --

def main():
    parser = argparse.ArgumentParser(description="Behike Email Sender")
    parser.add_argument("--send", metavar="FILE", help="Send newsletter to all subscribers")
    parser.add_argument("--test", metavar="EMAIL", help="Send test email to yourself")
    parser.add_argument("--dry-run", metavar="FILE", help="Simulate sending (no emails sent)")
    parser.add_argument("--newsletter", metavar="FILE", help="Newsletter file (used with --test)")

    args = parser.parse_args()

    if args.send:
        cmd_send(args.send)
    elif args.test:
        cmd_test(args.test, args.newsletter)
    elif args.dry_run:
        cmd_dry_run(args.dry_run)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()

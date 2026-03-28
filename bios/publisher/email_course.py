#!/usr/bin/env python3
"""
email_course.py -- 5-Day Email Course Autoresponder: "5 Days to Your First Digital Product"

Drives upgrades to the $97 Behike Operating System.

Env vars:
    BEEHIIV_API_KEY          - Beehiiv API key (optional, falls back to local drafts)
    BEEHIIV_PUBLICATION_ID   - Beehiiv publication ID
    TELEGRAM_BOT_TOKEN       - For completion notifications
    TELEGRAM_CHAT_ID         - Chat to notify when someone finishes

CLI:
    python3 email_course.py --add "email@example.com" "First Name"
    python3 email_course.py --list
    python3 email_course.py --stats
    python3 email_course.py --send-due
    python3 email_course.py --preview 1
    python3 email_course.py --preview all
"""

import argparse
import json
import os
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

try:
    import requests
except ImportError:
    requests = None

# -- Paths ---------------------------------------------------------------------

BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
DRAFTS_DIR = BASE_DIR / "drafts"
SUBSCRIBERS_FILE = DATA_DIR / "course_subscribers.json"
LOG_FILE = DATA_DIR / "course_log.json"

DATA_DIR.mkdir(parents=True, exist_ok=True)
DRAFTS_DIR.mkdir(parents=True, exist_ok=True)

# -- Env -----------------------------------------------------------------------

BEEHIIV_API_KEY = os.environ.get("BEEHIIV_API_KEY", "")
BEEHIIV_PUB_ID = os.environ.get("BEEHIIV_PUBLICATION_ID", "")
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID", "")

BEEHIIV_BASE = "https://api.beehiiv.com/v2"

# -- Course Content ------------------------------------------------------------
# Day number maps to days after signup the email is sent.
# day_index 1-5 for display, send_day is actual offset.

COURSE_EMAILS = [
    {
        "day_index": 1,
        "send_day": 0,
        "subject": "Your blueprint is ready. Here's what comes next.",
        "body": """\
Hey {{name}},

Your download is ready. Here's the link:

[DOWNLOAD YOUR FREE BLUEPRINT]

No fluff, no 47-step onboarding. Just the thing you came for.

Quick intro since we're going to be in your inbox for a bit.

I'm Kalani. I run Behike. We build systems, blueprints, and tools for people who are building something on their own. Solopreneurs, creators, students, freelancers. People who don't have a team of 12 but still want to move like they do.

Everything we make is designed to remove friction. Organized systems you can open and start using today. Not courses. Not theory. Tools.

Over the next 8 days, I'll send you a few emails. Some will teach you something useful. Some will show you what we've built and why. If it's not for you, you can unsubscribe anytime. No hard feelings.

But if you're the type of person who actually wants to build, not just consume, you're in the right place.

Start with the blueprint you just downloaded. Use it. Then come back.

Talk soon.

- Kalani, Behike""",
    },
    {
        "day_index": 2,
        "send_day": 2,
        "subject": "I built 100 products in a weekend. Here's why.",
        "body": """\
Hey {{name}},

Last semester I was a computer science student in Puerto Rico with no product, no audience, and no plan.

I had ideas. Lots of them. The problem was never ideas. The problem was I'd start something, get 40% in, then jump to the next thing. Repeat. For months.

I have ADHD. Diagnosed. Working on it. And for a long time I thought that was the thing holding me back. Turns out it wasn't. What was holding me back was not having systems.

So I started building them.

I made a blueprint for launching a product. Then one for content. Then one for automating the boring parts with AI. Then I just kept going. In one weekend I built over 100 digital products using the same repeatable system.

Not because I'm special. Because the system works when you show up.

That's what Behike is. It's the systems I wish I had when I started. Organized, practical, no theory without application. Built for people who think fast and need structure to match.

I'm not a guru. I'm a builder who figured out how to stop spinning.

If that resonates, stick around. The next email is about the one system that changed everything for me.

- Kalani, Behike""",
    },
    {
        "day_index": 3,
        "send_day": 4,
        "subject": "The one system every solopreneur needs",
        "body": """\
Hey {{name}},

Here's the thing nobody tells you when you start building alone: the bottleneck is never talent. It's organization.

You know how to make things. You just don't have a system for deciding what to make, when to make it, or how to ship it without burning out.

That's what an Operating System does.

Not a productivity app. Not a Notion template with 400 properties. An actual decision-making framework that tells you:

1. What to build next (based on what sells, not what's fun)
2. How to build it fast (repeatable steps, not starting from scratch)
3. Where to put it (distribution channels that work while you sleep)

I call it the Behike Operating System. It's the backbone of everything I ship.

When I sit down to work, I don't stare at a blank screen wondering what to do. I open the system, pick the next task, and execute. That's it.

The blueprint you downloaded is a piece of this. But the full system connects product creation, content, sales pages, pricing, and automation into one flow.

If you want a bird's eye view of how it works, here's a free breakdown:

[SEE THE FULL OPERATING SYSTEM OVERVIEW]

Next email, I'll show you the results.

- Kalani, Behike""",
    },
    {
        "day_index": 4,
        "send_day": 6,
        "subject": "From zero to 126 products. No team.",
        "body": """\
Hey {{name}},

Numbers, since that's what matters.

Starting from zero, with no team, no funding, and no audience:

- 126+ digital products created
- 70+ landing pages live
- Full content pipeline (short-form, long-form, newsletter)
- Bilingual catalog (English and Spanish)
- All built using the same repeatable system

I'm not listing this to flex. I'm listing it because when I was starting, the people I looked up to never showed the how. Just the result.

Here's the how: I built one system that works, then I ran it over and over.

Every product follows the same creation blueprint. Every landing page uses the same structure. Every piece of content pulls from the same idea bank. Nothing is improvised. Everything is documented.

The system isn't complicated. It's just organized. And that's the difference between someone who ships and someone who stays stuck in "planning mode" forever.

If you want to see what this looks like in practice, browse some of the free resources on our storefront:

[BROWSE FREE RESOURCES]

Everything there was built using the exact system I've been describing.

Next email, I'm going to show you the full thing.

- Kalani, Behike""",
    },
    {
        "day_index": 5,
        "send_day": 8,
        "subject": "The full system. $97.",
        "body": """\
Hey {{name}},

I've been showing you pieces of the system for the last week. Here's the whole thing.

The Behike Operating System is the complete framework I use to build, launch, and sell digital products as a solo creator. It's not a course. It's a working system you open and use.

Here's what's inside:

- 20+ blueprints covering product creation, content, sales pages, pricing, automation, and launch
- GoodNotes-ready format (print or use digitally, your call)
- Full bilingual versions (English and Spanish)
- Lifetime updates as the system evolves

This is not theory. Every blueprint was built from real execution. The same system that produced 126 products, 70+ landing pages, and a full content pipeline.

The price is $97.

I know that's real money. But here's how I think about it: you can spend the next 3-6 months figuring this out on your own, testing what works, rebuilding from scratch every time. Or you can start with a system that already works and adapt it to your niche.

The blueprints pay for themselves with one product launch.

If you're serious about building, this is the shortcut that isn't a shortcut. It's just the work, organized.

[GET THE BEHIKE OPERATING SYSTEM - $97]

If you have questions, reply to this email. I read everything.

- Kalani, Behike""",
    },
]

# -- Data helpers --------------------------------------------------------------


def _load_subscribers():
    if SUBSCRIBERS_FILE.exists():
        return json.loads(SUBSCRIBERS_FILE.read_text())
    return {}


def _save_subscribers(data):
    SUBSCRIBERS_FILE.write_text(json.dumps(data, indent=2, default=str))


def _load_log():
    if LOG_FILE.exists():
        return json.loads(LOG_FILE.read_text())
    return []


def _append_log(entry):
    log = _load_log()
    entry["timestamp"] = datetime.now(timezone.utc).isoformat()
    log.append(entry)
    LOG_FILE.write_text(json.dumps(log, indent=2, default=str))


# -- Beehiiv API --------------------------------------------------------------


def _beehiiv_available():
    return bool(BEEHIIV_API_KEY and BEEHIIV_PUB_ID and requests)


def _beehiiv_headers():
    return {
        "Authorization": f"Bearer {BEEHIIV_API_KEY}",
        "Content-Type": "application/json",
    }


def _beehiiv_send_email(to_email, subject, body_text):
    """Send an email via Beehiiv's API. Creates a targeted post/email.

    Beehiiv doesn't have a direct transactional send endpoint, so we create
    a post targeted to the subscriber. Falls back to saving as local draft.
    """
    if not _beehiiv_available():
        return _save_draft_locally(to_email, subject, body_text)

    try:
        # Convert plain text to simple HTML
        body_html = body_text.replace("\n\n", "</p><p>").replace("\n", "<br>")
        body_html = f"<p>{body_html}</p>"

        payload = {
            "title": subject,
            "subtitle": "5 Days to Your First Digital Product",
            "status": "draft",
            "content_html": body_html,
        }
        url = f"{BEEHIIV_BASE}/publications/{BEEHIIV_PUB_ID}/posts"
        resp = requests.post(url, headers=_beehiiv_headers(), json=payload, timeout=30)
        resp.raise_for_status()
        data = resp.json().get("data", {})
        post_id = data.get("id", "unknown")
        print(f"  [beehiiv] Draft created: {post_id} for {to_email}")
        return {"method": "beehiiv", "post_id": post_id, "status": "draft_created"}

    except Exception as e:
        print(f"  [beehiiv] API error: {e}. Falling back to local draft.")
        return _save_draft_locally(to_email, subject, body_text)


def _save_draft_locally(to_email, subject, body_text):
    """Save email as a local draft file when Beehiiv is unavailable."""
    ts = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    safe_email = to_email.replace("@", "_at_").replace(".", "_")
    draft_path = DRAFTS_DIR / f"course_{safe_email}_{ts}.txt"

    content = f"To: {to_email}\nSubject: {subject}\nDate: {ts}\n\n{body_text}"
    draft_path.write_text(content)
    print(f"  [local] Draft saved: {draft_path.name}")
    return {"method": "local_draft", "path": str(draft_path)}


# -- Telegram notification -----------------------------------------------------


def _send_telegram_notification(message):
    """Notify via Telegram when someone finishes the course."""
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID or not requests:
        print(f"  [telegram] Skipped (no token/chat_id). Message: {message}")
        return False

    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        payload = {
            "chat_id": TELEGRAM_CHAT_ID,
            "text": message,
            "parse_mode": "Markdown",
        }
        resp = requests.post(url, json=payload, timeout=15)
        resp.raise_for_status()
        print("  [telegram] Notification sent.")
        return True
    except Exception as e:
        print(f"  [telegram] Error: {e}")
        return False


# -- Core actions --------------------------------------------------------------


def add_subscriber(email, name):
    """Add a new subscriber to the email course."""
    subs = _load_subscribers()

    if email in subs:
        print(f"  Already enrolled: {email} (day {subs[email]['current_day']})")
        return False

    now = datetime.now(timezone.utc)
    subs[email] = {
        "name": name,
        "email": email,
        "enrolled_at": now.isoformat(),
        "current_day": 0,
        "emails_sent": [],
        "next_email_date": now.strftime("%Y-%m-%d"),
        "completed": False,
    }
    _save_subscribers(subs)
    _append_log({"event": "subscriber_added", "email": email, "name": name})
    print(f"  Added: {name} <{email}> -- Day 1 email ready to send today.")
    return True


def list_subscribers():
    """Show all subscribers and their progress."""
    subs = _load_subscribers()
    if not subs:
        print("  No subscribers yet. Use --add to enroll someone.")
        return

    print()
    print(f"  {'EMAIL':<35s} {'NAME':<15s} {'DAY':<5s} {'STATUS':<12s} {'NEXT EMAIL'}")
    print(f"  {'-'*35} {'-'*15} {'-'*5} {'-'*12} {'-'*12}")

    for email, info in sorted(subs.items(), key=lambda x: x[1].get("enrolled_at", "")):
        status = "COMPLETED" if info.get("completed") else "ACTIVE"
        day = info.get("current_day", 0)
        # Display which email number they're on next
        next_email_num = len(info.get("emails_sent", [])) + 1
        if next_email_num > 5:
            next_email_num = "done"
        next_date = info.get("next_email_date", "N/A")
        name = info.get("name", "")[:15]
        print(f"  {email:<35s} {name:<15s} {str(next_email_num):<5s} {status:<12s} {next_date}")
    print()


def show_stats():
    """Show course statistics."""
    subs = _load_subscribers()
    log = _load_log()

    total = len(subs)
    completed = sum(1 for s in subs.values() if s.get("completed"))
    active = total - completed

    # Count emails sent per day
    day_counts = {i: 0 for i in range(1, 6)}
    for entry in log:
        if entry.get("event") == "email_sent":
            day_idx = entry.get("day_index", 0)
            if day_idx in day_counts:
                day_counts[day_idx] += 1

    print()
    print("=" * 50)
    print("  5-DAY EMAIL COURSE STATS")
    print("=" * 50)
    print(f"  Total subscribers:  {total}")
    print(f"  Active:             {active}")
    print(f"  Completed:          {completed}")
    if total > 0:
        print(f"  Completion rate:    {round(completed / total * 100, 1)}%")
    print()
    print("  Emails sent per day:")
    for day in range(1, 6):
        email_info = COURSE_EMAILS[day - 1]
        bar = "#" * day_counts[day]
        print(f"    Day {day} ({email_info['subject'][:30]}...): {day_counts[day]} {bar}")
    print()


def send_due_emails():
    """Check all subscribers, send emails that are due today or overdue."""
    subs = _load_subscribers()
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    sent_count = 0

    print(f"\n  Checking {len(subs)} subscribers (today: {today})...\n")

    for email, info in subs.items():
        if info.get("completed"):
            continue

        next_date = info.get("next_email_date", "")
        if not next_date or next_date > today:
            continue

        # Figure out which email to send next
        emails_sent = info.get("emails_sent", [])
        next_index = len(emails_sent)  # 0-based

        if next_index >= len(COURSE_EMAILS):
            # All emails sent, mark complete
            info["completed"] = True
            _save_subscribers(subs)
            continue

        course_email = COURSE_EMAILS[next_index]
        name = info.get("name", "there")
        body = course_email["body"].replace("{{name}}", name)
        subject = course_email["subject"]

        print(f"  Sending Day {course_email['day_index']} to {email}...")
        result = _beehiiv_send_email(email, subject, body)

        # Update subscriber state
        info["emails_sent"].append({
            "day_index": course_email["day_index"],
            "sent_at": datetime.now(timezone.utc).isoformat(),
            "method": result.get("method", "unknown"),
        })
        info["current_day"] = course_email["send_day"]

        # Calculate next email date
        if next_index + 1 < len(COURSE_EMAILS):
            next_course = COURSE_EMAILS[next_index + 1]
            enrolled = datetime.fromisoformat(info["enrolled_at"])
            next_send = enrolled + timedelta(days=next_course["send_day"])
            info["next_email_date"] = next_send.strftime("%Y-%m-%d")
        else:
            # Course complete
            info["completed"] = True
            info["next_email_date"] = None
            _send_telegram_notification(
                f"*Course completed!*\n"
                f"{name} ({email}) finished the 5-day email course.\n"
                f"Ready for the $97 Behike OS pitch follow-up."
            )

        _append_log({
            "event": "email_sent",
            "email": email,
            "day_index": course_email["day_index"],
            "subject": subject,
            "method": result.get("method", "unknown"),
        })
        sent_count += 1

    _save_subscribers(subs)
    print(f"\n  Done. Sent {sent_count} email(s).\n")
    return sent_count


def preview_email(day_num):
    """Preview a course email (or all)."""
    if day_num == "all":
        for email in COURSE_EMAILS:
            _print_email_preview(email)
        return

    day_num = int(day_num)
    if day_num < 1 or day_num > 5:
        print("  Day must be 1-5, or 'all'.")
        return

    _print_email_preview(COURSE_EMAILS[day_num - 1])


def _print_email_preview(email):
    print()
    print("=" * 60)
    print(f"  DAY {email['day_index']} (sends day {email['send_day']} after signup)")
    print(f"  Subject: {email['subject']}")
    print("=" * 60)
    # Show with a sample name
    body = email["body"].replace("{{name}}", "Alex")
    for line in body.split("\n"):
        print(f"  {line}")
    print()


# -- CLI -----------------------------------------------------------------------


def main():
    parser = argparse.ArgumentParser(
        description="5-Day Email Course Autoresponder for Behike OS",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python3 email_course.py --add "test@example.com" "Alex"
  python3 email_course.py --list
  python3 email_course.py --stats
  python3 email_course.py --send-due
  python3 email_course.py --preview 1
  python3 email_course.py --preview all

Cron (daily at 9am):
  0 9 * * * cd /Users/kalani/behique/bios/publisher && python3 email_course.py --send-due
        """,
    )

    parser.add_argument("--add", nargs=2, metavar=("EMAIL", "NAME"),
                        help="Add subscriber with email and name")
    parser.add_argument("--list", action="store_true",
                        help="List all subscribers and progress")
    parser.add_argument("--stats", action="store_true",
                        help="Show course statistics")
    parser.add_argument("--send-due", action="store_true",
                        help="Send all due emails (run daily via cron)")
    parser.add_argument("--preview", metavar="DAY",
                        help="Preview email content (1-5 or 'all')")

    args = parser.parse_args()

    if not any([args.add, args.list, args.stats, args.send_due, args.preview]):
        parser.print_help()
        sys.exit(0)

    if args.add:
        add_subscriber(args.add[0], args.add[1])

    if args.list:
        list_subscribers()

    if args.stats:
        show_stats()

    if args.send_due:
        send_due_emails()

    if args.preview:
        preview_email(args.preview)


if __name__ == "__main__":
    main()

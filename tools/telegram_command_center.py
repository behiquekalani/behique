#!/usr/bin/env python3
"""
Telegram Command Center - Your entire business from one chat thread.

Commands:
    /morning    - Daily briefing (git state, tasks, weather)
    /news       - AI news digest from RSS feeds
    /niche      - Top niche gaps from Reddit scanner
    /focus N    - Start a Pomodoro timer (default 25 min)
    /ideas      - List uncaptured ideas from IDEAS_BACKLOG
    /budget     - Current month spending summary
    /status     - System status (fleet, cron jobs, processes)
    /audit      - Run sprint audit
    /help       - Show all commands

Requirements:
    pip3 install python-telegram-bot feedparser

    Set env var: TELEGRAM_CMD_BOT_TOKEN=your_bot_token

Usage:
    python3 telegram_command_center.py
"""

import asyncio
import json
import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path

try:
    from telegram import Update
    from telegram.ext import Application, CommandHandler, ContextTypes
except ImportError:
    print("Installing python-telegram-bot...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "python-telegram-bot", "-q"])
    from telegram import Update
    from telegram.ext import Application, CommandHandler, ContextTypes

BASE_DIR = Path(__file__).resolve().parent.parent
TOKEN = os.environ.get("TELEGRAM_CMD_BOT_TOKEN", "")

# Allowed user IDs (set after first /start)
ALLOWED_USERS_FILE = BASE_DIR / "tools" / ".cmd_allowed_users.json"


def load_allowed():
    if ALLOWED_USERS_FILE.exists():
        return set(json.loads(ALLOWED_USERS_FILE.read_text()))
    return set()


def save_allowed(users):
    ALLOWED_USERS_FILE.write_text(json.dumps(list(users)))


ALLOWED_USERS = load_allowed()


def is_authorized(update: Update) -> bool:
    return update.effective_user.id in ALLOWED_USERS


async def cmd_start(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    ALLOWED_USERS.add(uid)
    save_allowed(ALLOWED_USERS)
    await update.message.reply_text(
        "Behike Command Center active.\n"
        f"User {uid} authorized.\n\n"
        "Type /help for available commands."
    )


async def cmd_help(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if not is_authorized(update):
        return
    await update.message.reply_text(
        "BEHIKE COMMAND CENTER\n\n"
        "/morning  - Daily briefing\n"
        "/news     - AI news digest\n"
        "/niche    - Top Reddit niche gaps\n"
        "/focus N  - Pomodoro timer (N minutes)\n"
        "/ideas    - Uncaptured ideas\n"
        "/budget   - Monthly spending\n"
        "/status   - System status\n"
        "/audit    - Sprint audit\n"
        "/primer   - Current primer state\n"
        "/git      - Recent git activity\n"
        "/help     - This message"
    )


async def cmd_morning(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if not is_authorized(update):
        return
    await update.message.reply_text("Generating morning briefing...")

    parts = []
    now = datetime.now()
    parts.append(f"MORNING BRIEFING - {now.strftime('%A, %B %d %Y')}\n")

    # Git status
    try:
        result = subprocess.run(
            ["git", "log", "--oneline", "-5"],
            capture_output=True, text=True, cwd=str(BASE_DIR), timeout=10
        )
        parts.append("RECENT COMMITS:\n" + result.stdout.strip())
    except Exception:
        parts.append("Git: unavailable")

    # Primer state
    primer = BASE_DIR / "primer.md"
    if primer.exists():
        text = primer.read_text()
        # Extract first 500 chars
        parts.append("\nPRIMER (summary):\n" + text[:500])

    # Cron jobs
    try:
        result = subprocess.run(
            ["crontab", "-l"], capture_output=True, text=True, timeout=5
        )
        lines = [l for l in result.stdout.strip().split("\n") if l and not l.startswith("#")]
        parts.append(f"\nCRON JOBS: {len(lines)} active")
    except Exception:
        parts.append("\nCron: unavailable")

    msg = "\n".join(parts)
    # Telegram max message is 4096 chars
    if len(msg) > 4000:
        msg = msg[:4000] + "..."
    await update.message.reply_text(msg)


async def cmd_news(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if not is_authorized(update):
        return
    digest_file = BASE_DIR / "Ceiba" / "news" / "daily-digest.json"
    if not digest_file.exists():
        # Try running the news tracker
        try:
            subprocess.run(
                [sys.executable, str(BASE_DIR / "tools" / "ai_news_tracker.py")],
                capture_output=True, timeout=30, cwd=str(BASE_DIR)
            )
        except Exception:
            pass

    if digest_file.exists():
        data = json.loads(digest_file.read_text())
        items = data if isinstance(data, list) else data.get("items", [])
        msg = "AI NEWS DIGEST\n\n"
        for item in items[:10]:
            title = item.get("title", "No title")
            score = item.get("score", item.get("impact_score", 0))
            msg += f"[{score}] {title}\n"
        await update.message.reply_text(msg[:4000])
    else:
        await update.message.reply_text("No news digest available. Run ai_news_tracker.py first.")


async def cmd_niche(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if not is_authorized(update):
        return
    gaps_file = BASE_DIR / "Ceiba" / "news" / "niche-gaps.json"
    if gaps_file.exists():
        gaps = json.loads(gaps_file.read_text())
        # Sort by score descending
        gaps.sort(key=lambda g: g.get("score", 0), reverse=True)
        msg = "TOP NICHE GAPS (Reddit)\n\n"
        for g in gaps[:10]:
            score = g.get("score", 0)
            title = g.get("title", "")[:60]
            sub = g.get("subreddit", "?")
            msg += f"[{score}] r/{sub}: {title}\n"
        await update.message.reply_text(msg[:4000])
    else:
        await update.message.reply_text("No niche gaps yet. Run: python3 tools/reddit_niche_crawler.py")


async def cmd_focus(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if not is_authorized(update):
        return
    args = ctx.args
    minutes = 25
    if args and args[0].isdigit():
        minutes = int(args[0])
        if minutes > 120:
            minutes = 120

    await update.message.reply_text(f"Focus timer started: {minutes} minutes.\nI will notify you when it is done.")

    await asyncio.sleep(minutes * 60)
    await update.message.reply_text(
        f"TIMER COMPLETE ({minutes} min)\n\n"
        "Take a 5 minute break. Stretch. Drink water.\n"
        "Then /focus again."
    )


async def cmd_ideas(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if not is_authorized(update):
        return
    backlog = BASE_DIR / "Ceiba" / "IDEAS_BACKLOG.md"
    if backlog.exists():
        text = backlog.read_text()
        # Count ideas
        idea_count = text.count("##")
        future_count = text.lower().count("future")
        msg = f"IDEAS BACKLOG: {idea_count} ideas tracked\n"
        msg += f"FUTURE items: {future_count}\n\n"
        # Show first 800 chars
        msg += text[:800]
        await update.message.reply_text(msg[:4000])
    else:
        await update.message.reply_text("No IDEAS_BACKLOG.md found.")


async def cmd_budget(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if not is_authorized(update):
        return
    # Check for finance data
    finance_files = list((BASE_DIR / "Ceiba").glob("*finance*")) + list((BASE_DIR / "Ceiba").glob("*budget*"))
    if finance_files:
        msg = "BUDGET FILES FOUND:\n\n"
        for f in finance_files[:5]:
            msg += f"- {f.name}\n"
        await update.message.reply_text(msg)
    else:
        await update.message.reply_text(
            "MONTHLY BUDGET\n\n"
            "Fixed costs:\n"
            "- behike.co domain: ~$1.50/mo\n"
            "- behike.store domain: ~$2/mo\n"
            "- Gumroad: free (5% on sales)\n"
            "- Railway (BehiqueBot): ~$5/mo\n"
            "- Total fixed: ~$8.50/mo\n\n"
            "Revenue: $0 (products not yet listed)\n\n"
            "To track spending, create Ceiba/budget.json"
        )


async def cmd_status(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if not is_authorized(update):
        return
    parts = ["SYSTEM STATUS\n"]

    # Machine
    try:
        result = subprocess.run(["uname", "-n"], capture_output=True, text=True, timeout=5)
        parts.append(f"Machine: {result.stdout.strip()}")
    except Exception:
        pass

    # Python
    parts.append(f"Python: {sys.version.split()[0]}")

    # Disk
    try:
        result = subprocess.run(["df", "-h", "/"], capture_output=True, text=True, timeout=5)
        lines = result.stdout.strip().split("\n")
        if len(lines) > 1:
            parts.append(f"Disk: {lines[1].split()[3]} free")
    except Exception:
        pass

    # Products count
    try:
        products_json = BASE_DIR / "storefront" / "products.json"
        if products_json.exists():
            products = json.loads(products_json.read_text())
            parts.append(f"Products in catalog: {len(products)}")
    except Exception:
        pass

    # Gumroad-ready count
    gr = BASE_DIR / "READY-TO-SELL" / "gumroad-ready"
    if gr.exists():
        count = len(list(gr.iterdir()))
        parts.append(f"Gumroad-ready files: {count}")

    # Cover images
    covers = BASE_DIR / "READY-TO-SELL" / "product-covers"
    if covers.exists():
        pngs = len(list(covers.glob("*.png")))
        parts.append(f"Cover images: {pngs}")

    await update.message.reply_text("\n".join(parts))


async def cmd_audit(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if not is_authorized(update):
        return
    await update.message.reply_text("Running sprint audit...")
    try:
        result = subprocess.run(
            [sys.executable, str(BASE_DIR / "tools" / "sprint_audit.py")],
            capture_output=True, text=True, timeout=60, cwd=str(BASE_DIR)
        )
        output = result.stdout.strip()
        if not output:
            output = "Audit completed (no output)"
        await update.message.reply_text(output[:4000])
    except Exception as e:
        await update.message.reply_text(f"Audit failed: {e}")


async def cmd_primer(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if not is_authorized(update):
        return
    primer = BASE_DIR / "primer.md"
    if primer.exists():
        text = primer.read_text()
        await update.message.reply_text(text[:4000])
    else:
        await update.message.reply_text("No primer.md found.")


async def cmd_git(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if not is_authorized(update):
        return
    try:
        result = subprocess.run(
            ["git", "log", "--oneline", "--since=24 hours ago", "-20"],
            capture_output=True, text=True, cwd=str(BASE_DIR), timeout=10
        )
        output = result.stdout.strip()
        if not output:
            output = "No commits in the last 24 hours."
        await update.message.reply_text(f"GIT (last 24h):\n\n{output}"[:4000])
    except Exception as e:
        await update.message.reply_text(f"Git error: {e}")


def main():
    if not TOKEN:
        print("ERROR: Set TELEGRAM_CMD_BOT_TOKEN environment variable")
        print("  export TELEGRAM_CMD_BOT_TOKEN=your_bot_token")
        sys.exit(1)

    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", cmd_start))
    app.add_handler(CommandHandler("help", cmd_help))
    app.add_handler(CommandHandler("morning", cmd_morning))
    app.add_handler(CommandHandler("news", cmd_news))
    app.add_handler(CommandHandler("niche", cmd_niche))
    app.add_handler(CommandHandler("focus", cmd_focus))
    app.add_handler(CommandHandler("ideas", cmd_ideas))
    app.add_handler(CommandHandler("budget", cmd_budget))
    app.add_handler(CommandHandler("status", cmd_status))
    app.add_handler(CommandHandler("audit", cmd_audit))
    app.add_handler(CommandHandler("primer", cmd_primer))
    app.add_handler(CommandHandler("git", cmd_git))

    print("Behike Command Center starting...")
    print(f"  Base dir: {BASE_DIR}")
    print(f"  Commands: /morning /news /niche /focus /ideas /budget /status /audit /primer /git")
    app.run_polling()


if __name__ == "__main__":
    main()

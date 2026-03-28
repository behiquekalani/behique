#!/usr/bin/env python3
# Copyright 2026 Behike. All rights reserved.
"""Telegram scheduled messages for daily accountability."""

import subprocess
from datetime import time
from pathlib import Path
from telegram.ext import ContextTypes

TOOLS_DIR = Path(__file__).parent.parent / "tools"
# Puerto Rico timezone: UTC-4 (AST)
# job_queue times are in UTC, so 7am AST = 11:00 UTC


async def morning_brief(context: ContextTypes.DEFAULT_TYPE):
    """7:00 AM - Morning briefing."""
    try:
        result = subprocess.run(
            ["python3", str(TOOLS_DIR / "ceiba_morning_brief.py"), "--short"],
            capture_output=True, text=True, timeout=30
        )
        text = result.stdout[:3000] if result.stdout else "Buenos dias. Time to build."
    except Exception:
        text = "Buenos dias. Check the morning brief manually."
    await context.bot.send_message(chat_id=context.job.chat_id, text=f"*Morning Brief*\n\n{text}", parse_mode="Markdown")


async def midday_check(context: ContextTypes.DEFAULT_TYPE):
    """12:00 PM - Shipping check."""
    await context.bot.send_message(
        chat_id=context.job.chat_id,
        text="Midday check. What have you shipped today?\n\nIf nothing yet, pick ONE thing and ship it before 6pm."
    )


async def post_reminder(context: ContextTypes.DEFAULT_TYPE):
    """6:00 PM - Content posting reminder."""
    await context.bot.send_message(
        chat_id=context.job.chat_id,
        text="Time to post. Check today's content calendar:\n\n`python3 tools/content_calendar.py --today`\n\nFiles are in Ceiba/news/ready-to-post/",
        parse_mode="Markdown"
    )


async def mood_check(context: ContextTypes.DEFAULT_TYPE):
    """10:00 PM - End of day mood check."""
    await context.bot.send_message(
        chat_id=context.job.chat_id,
        text="How was today? Rate 1-10:\n`/mood [number]`\n\nRemember: showing up counts. You don't need to ship every day to make progress.",
        parse_mode="Markdown"
    )


async def weekly_summary(context: ContextTypes.DEFAULT_TYPE):
    """Sunday 8:00 PM - Weekly summary."""
    from modules.command_center import _load_json
    moods = _load_json("moods")
    budget = _load_json("budget")

    # Calculate week's mood average
    from datetime import datetime, timedelta
    today = datetime.now()
    week_scores = []
    for i in range(7):
        day = (today - timedelta(days=i)).strftime("%Y-%m-%d")
        if day in moods:
            week_scores.extend(e["score"] for e in moods[day])
    avg = sum(week_scores) / len(week_scores) if week_scores else 0

    text = f"*Weekly Summary*\n\nMood average: {avg:.1f}/10 ({len(week_scores)} check-ins)\n\nNew week starts tomorrow. What's the ONE thing you want to ship this week?"
    await context.bot.send_message(chat_id=context.job.chat_id, text=text, parse_mode="Markdown")


def setup_scheduler(app, chat_id):
    """Set up all scheduled jobs. Call after bot starts."""
    jq = app.job_queue
    # Times in UTC (AST + 4 hours)
    jq.run_daily(morning_brief, time=time(11, 0), chat_id=chat_id, name="morning_brief")
    jq.run_daily(midday_check, time=time(16, 0), chat_id=chat_id, name="midday_check")
    jq.run_daily(post_reminder, time=time(22, 0), chat_id=chat_id, name="post_reminder")
    jq.run_daily(mood_check, time=time(2, 0), chat_id=chat_id, name="mood_check")
    # Sunday = 6 in python-telegram-bot
    jq.run_daily(weekly_summary, time=time(0, 0), days=(6,), chat_id=chat_id, name="weekly_summary")
    print(f"[Scheduler] 5 daily jobs registered for chat {chat_id}")

"""
calendar_handler.py -- Local calendar for BehiqueBot.

Stores events in Ceiba/calendar/events.json.
Parses natural date/time mentions from messages.
Provides /calendar, /today, /week commands.
Pushes daily 8am reminders via notify.py queue.
"""

import json
import os
import re
import uuid
import subprocess
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional

from telegram import Update
from telegram.ext import ContextTypes

from modules.routing import run_chat


# -- Paths -----------------------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent.parent
CALENDAR_DIR = BASE_DIR / "Ceiba" / "calendar"
EVENTS_FILE = CALENDAR_DIR / "events.json"
NOTIFY_SCRIPT = BASE_DIR / "tools" / "notify.py"


def _ensure_calendar_dir():
    CALENDAR_DIR.mkdir(parents=True, exist_ok=True)


def _load_events() -> list:
    _ensure_calendar_dir()
    if not EVENTS_FILE.exists():
        return []
    with open(EVENTS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def _save_events(events: list):
    _ensure_calendar_dir()
    with open(EVENTS_FILE, "w", encoding="utf-8") as f:
        json.dump(events, f, ensure_ascii=False, indent=2)


# -- Date parsing via LLM --------------------------------------------------
def parse_event_from_text(text: str) -> Optional[dict]:
    """
    Use the LLM to extract event title, date, and time from natural text.
    Returns dict with keys: title, date (YYYY-MM-DD), time (HH:MM or null).
    Returns None if no event detected.
    """
    today = datetime.now().strftime("%Y-%m-%d")
    weekday = datetime.now().strftime("%A")

    system_prompt = f"""You are a date/time parser. Today is {today} ({weekday}).

Extract calendar event info from the user's message.
If the message contains a date/time reference and something that looks like an event, extract it.
If there is no event or date reference, return {{"event_found": false}}.

Return ONLY valid JSON in this format:
{{"event_found": true, "title": "Meeting with team", "date": "2026-03-25", "time": "15:00"}}
or
{{"event_found": true, "title": "Doctor appointment", "date": "2026-03-22", "time": null}}
or
{{"event_found": false}}

Rules:
- "tomorrow" means the day after today
- "next Monday" means the coming Monday
- Times like "3pm" become "15:00", "9am" becomes "09:00"
- If no specific time is mentioned, set time to null
- Date format must be YYYY-MM-DD
- Title should be concise, under 60 characters"""

    try:
        response = run_chat(
            "classification",
            [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": text},
            ],
            temperature=0,
            response_format={"type": "json_object"},
        )
        result = json.loads(response.choices[0].message.content)
        if result.get("event_found"):
            return {
                "title": result["title"],
                "date": result["date"],
                "time": result.get("time"),
            }
    except Exception:
        pass
    return None


# -- Event CRUD -------------------------------------------------------------
def add_event(title: str, date: str, time: str = None, user_id: str = None) -> dict:
    """Add a new event. Returns the created event dict."""
    events = _load_events()
    event = {
        "id": str(uuid.uuid4())[:8],
        "title": title,
        "date": date,
        "time": time,
        "user_id": user_id,
        "created_at": datetime.now().isoformat(),
    }
    events.append(event)
    _save_events(events)
    return event


def get_events_for_date(date_str: str) -> list:
    """Get all events for a specific date (YYYY-MM-DD)."""
    events = _load_events()
    return [e for e in events if e["date"] == date_str]


def get_events_for_week() -> list:
    """Get all events for the current week (Mon-Sun)."""
    today = datetime.now()
    monday = today - timedelta(days=today.weekday())
    sunday = monday + timedelta(days=6)

    events = _load_events()
    week_events = []
    for e in events:
        try:
            event_date = datetime.strptime(e["date"], "%Y-%m-%d")
            if monday.date() <= event_date.date() <= sunday.date():
                week_events.append(e)
        except (ValueError, KeyError):
            continue

    week_events.sort(key=lambda x: (x["date"], x.get("time") or "99:99"))
    return week_events


def format_event(event: dict) -> str:
    """Format a single event for display."""
    time_str = event.get("time") or "all day"
    return f"  {event['date']} @ {time_str} -- {event['title']}"


def format_event_list(events: list, header: str) -> str:
    """Format a list of events with a header."""
    if not events:
        return f"{header}\n\nNo events scheduled."

    lines = [header, ""]
    for event in events:
        time_str = event.get("time") or "all day"
        lines.append(f"  {event['date']} @ {time_str} -- {event['title']}")
    return "\n".join(lines)


# -- Telegram command handlers ----------------------------------------------
async def handle_calendar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /calendar command. Parses text after the command as a new event."""
    args = context.args
    if not args:
        # Show help
        await update.message.reply_text(
            "Calendar commands:\n\n"
            "/calendar <event description with date>\n"
            "  Example: /calendar dentist tomorrow at 2pm\n\n"
            "/today -- show today's events\n"
            "/week -- show this week's events"
        )
        return

    text = " ".join(args)
    parsed = parse_event_from_text(text)

    if not parsed:
        await update.message.reply_text(
            "Could not detect a date in that message. "
            "Try something like: /calendar meeting tomorrow at 3pm"
        )
        return

    user_id = str(update.message.from_user.id)
    event = add_event(
        title=parsed["title"],
        date=parsed["date"],
        time=parsed.get("time"),
        user_id=user_id,
    )

    time_display = event.get("time") or "all day"
    await update.message.reply_text(
        f"Added to calendar:\n\n"
        f"  {event['title']}\n"
        f"  {event['date']} @ {time_display}\n"
        f"  ID: {event['id']}"
    )


async def handle_today(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /today command. Shows today's events."""
    today_str = datetime.now().strftime("%Y-%m-%d")
    events = get_events_for_date(today_str)
    msg = format_event_list(events, f"Today ({today_str}):")
    await update.message.reply_text(msg)


async def handle_week(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /week command. Shows this week's events."""
    events = get_events_for_week()
    today = datetime.now()
    monday = today - timedelta(days=today.weekday())
    sunday = monday + timedelta(days=6)
    header = f"This week ({monday.strftime('%b %d')} - {sunday.strftime('%b %d')}):"
    msg = format_event_list(events, header)
    await update.message.reply_text(msg)


def detect_calendar_intent(text: str) -> bool:
    """Check if a message looks like a calendar request (for inline detection)."""
    patterns = [
        r"add to calendar",
        r"schedule",
        r"remind me",
        r"set a reminder",
        r"put on (my )?calendar",
    ]
    text_lower = text.lower()
    return any(re.search(p, text_lower) for p in patterns)


async def handle_inline_calendar(update: Update, context: ContextTypes.DEFAULT_TYPE, text: str) -> bool:
    """
    Called from process_message when calendar intent is detected in regular text.
    Returns True if an event was added, False otherwise.
    """
    parsed = parse_event_from_text(text)
    if not parsed:
        return False

    user_id = str(update.message.from_user.id)
    event = add_event(
        title=parsed["title"],
        date=parsed["date"],
        time=parsed.get("time"),
        user_id=user_id,
    )

    time_display = event.get("time") or "all day"
    await update.message.reply_text(
        f"Added to calendar:\n\n"
        f"  {event['title']}\n"
        f"  {event['date']} @ {time_display}\n"
        f"  ID: {event['id']}"
    )
    return True


# -- Daily reminder (called by scheduler) -----------------------------------
def send_daily_reminder():
    """
    Build today's event summary and queue it via notify.py.
    Meant to be called at 8am by a scheduler (cron, APScheduler, etc).
    """
    today_str = datetime.now().strftime("%Y-%m-%d")
    events = get_events_for_date(today_str)

    if not events:
        return  # No events, no notification

    lines = [f"Good morning. Here is your schedule for {today_str}:", ""]
    for e in events:
        time_str = e.get("time") or "all day"
        lines.append(f"  {time_str} -- {e['title']}")

    message = "\n".join(lines)

    # Queue via notify.py
    try:
        subprocess.run(
            [sys.executable, str(NOTIFY_SCRIPT), "--queue", message, "calendar"],
            check=True,
            capture_output=True,
        )
    except Exception:
        pass  # Fail silently, don't crash the bot

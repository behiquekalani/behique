"""
habitica_handler.py -- Habitica API integration for BehiqueBot.

Connects to Habitica v3 API for habit/daily/todo tracking.
Provides /habits, /daily, /todo, /complete, /hp commands.
Auto-suggests completing tasks when user mentions finishing something.
"""

import json
import os
import re
import ssl
import urllib.request
import urllib.parse
from typing import Optional

from telegram import Update
from telegram.ext import ContextTypes

from modules.routing import run_chat


# -- Config -----------------------------------------------------------------
HABITICA_BASE = "https://habitica.com/api/v3"
HABITICA_USER_ID = os.getenv("HABITICA_USER_ID", "")
HABITICA_API_TOKEN = os.getenv("HABITICA_API_TOKEN", "")

# SSL context for macOS
try:
    import certifi
    SSL_CONTEXT = ssl.create_default_context(cafile=certifi.where())
except ImportError:
    SSL_CONTEXT = ssl.create_default_context()


# -- API helpers -------------------------------------------------------------
def _habitica_headers() -> dict:
    return {
        "x-api-user": HABITICA_USER_ID,
        "x-api-key": HABITICA_API_TOKEN,
        "x-client": "behiquebot-ceiba",
        "Content-Type": "application/json",
    }


def _habitica_get(endpoint: str) -> Optional[dict]:
    """Make a GET request to Habitica API. Returns parsed JSON or None."""
    if not HABITICA_USER_ID or not HABITICA_API_TOKEN:
        return None

    url = f"{HABITICA_BASE}{endpoint}"
    req = urllib.request.Request(url, headers=_habitica_headers(), method="GET")
    try:
        with urllib.request.urlopen(req, timeout=15, context=SSL_CONTEXT) as resp:
            data = json.loads(resp.read())
            if data.get("success"):
                return data.get("data")
    except Exception:
        pass
    return None


def _habitica_post(endpoint: str, body: dict = None) -> Optional[dict]:
    """Make a POST request to Habitica API. Returns parsed JSON or None."""
    if not HABITICA_USER_ID or not HABITICA_API_TOKEN:
        return None

    url = f"{HABITICA_BASE}{endpoint}"
    payload = json.dumps(body or {}).encode("utf-8")
    req = urllib.request.Request(url, data=payload, headers=_habitica_headers(), method="POST")
    try:
        with urllib.request.urlopen(req, timeout=15, context=SSL_CONTEXT) as resp:
            data = json.loads(resp.read())
            if data.get("success"):
                return data.get("data")
    except Exception:
        pass
    return None


# -- Data fetchers -----------------------------------------------------------
def get_user_stats() -> Optional[dict]:
    """Fetch current user stats (HP, XP, level, gold)."""
    data = _habitica_get("/user?userFields=stats")
    if data and "stats" in data:
        return data["stats"]
    return None


def get_tasks_by_type(task_type: str) -> list:
    """Fetch tasks by type: habits, dailys, todos."""
    data = _habitica_get(f"/tasks/user?type={task_type}")
    if data and isinstance(data, list):
        return data
    return []


def score_task(task_id: str, direction: str = "up") -> Optional[dict]:
    """Score a task up or down. Returns updated stats."""
    return _habitica_post(f"/tasks/{task_id}/score/{direction}")


def find_task_by_name(name: str, task_types: list = None) -> Optional[dict]:
    """
    Search for a task by name across specified types.
    Returns the best match or None.
    """
    if task_types is None:
        task_types = ["habits", "dailys", "todos"]

    name_lower = name.lower().strip()
    best_match = None
    best_score = 0

    for t in task_types:
        tasks = get_tasks_by_type(t)
        for task in tasks:
            task_text = task.get("text", "").lower()
            # Exact match
            if task_text == name_lower:
                return task
            # Substring match
            if name_lower in task_text or task_text in name_lower:
                score = len(name_lower) / max(len(task_text), 1)
                if score > best_score:
                    best_score = score
                    best_match = task

    return best_match


# -- Formatters --------------------------------------------------------------
def format_task_list(tasks: list, header: str, max_items: int = 15) -> str:
    """Format a list of Habitica tasks for Telegram display."""
    if not tasks:
        return f"{header}\n\nNo items found."

    lines = [header, ""]
    for i, task in enumerate(tasks[:max_items]):
        text = task.get("text", "Unknown")
        completed = task.get("completed", False)
        check = "[x]" if completed else "[ ]"

        # For habits, show counter instead of checkbox
        if task.get("type") == "habit":
            counter_up = task.get("counterUp", 0)
            counter_down = task.get("counterDown", 0)
            lines.append(f"  {i+1}. {text} (+{counter_up}/-{counter_down})")
        else:
            lines.append(f"  {i+1}. {check} {text}")

    if len(tasks) > max_items:
        lines.append(f"\n  ... and {len(tasks) - max_items} more")

    return "\n".join(lines)


def format_stats(stats: dict) -> str:
    """Format user stats for display."""
    hp = stats.get("hp", 0)
    max_hp = stats.get("maxHealth", 50)
    xp = stats.get("exp", 0)
    max_xp = stats.get("toNextLevel", 0)
    level = stats.get("lvl", 1)
    gold = stats.get("gp", 0)
    mp = stats.get("mp", 0)
    max_mp = stats.get("maxMP", 0)
    class_name = stats.get("class", "warrior").title()

    return (
        f"Habitica Stats\n\n"
        f"  Level {level} {class_name}\n"
        f"  HP: {hp:.0f}/{max_hp}\n"
        f"  XP: {xp:.0f}/{max_xp}\n"
        f"  MP: {mp:.0f}/{max_mp}\n"
        f"  Gold: {gold:.1f}"
    )


# -- Telegram command handlers -----------------------------------------------
async def handle_habits(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /habits command. Lists all habits."""
    tasks = get_tasks_by_type("habits")
    if tasks is None:
        await update.message.reply_text(
            "Could not connect to Habitica. Check your API credentials in .env."
        )
        return
    msg = format_task_list(tasks, "Your Habits:")
    await update.message.reply_text(msg)


async def handle_dailies(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /daily command. Lists all dailies."""
    tasks = get_tasks_by_type("dailys")
    if tasks is None:
        await update.message.reply_text(
            "Could not connect to Habitica. Check your API credentials in .env."
        )
        return

    # Separate due today vs not due
    due_today = [t for t in tasks if t.get("isDue", False) and not t.get("completed", False)]
    completed = [t for t in tasks if t.get("isDue", False) and t.get("completed", False)]

    lines = ["Your Dailies:", ""]
    if due_today:
        lines.append(f"  Due today ({len(due_today)}):")
        for i, t in enumerate(due_today):
            lines.append(f"    {i+1}. [ ] {t.get('text', '?')}")
    if completed:
        lines.append(f"\n  Completed ({len(completed)}):")
        for i, t in enumerate(completed):
            lines.append(f"    {i+1}. [x] {t.get('text', '?')}")

    if not due_today and not completed:
        lines.append("  No dailies due today.")

    await update.message.reply_text("\n".join(lines))


async def handle_todos(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /todo command. Lists active todos."""
    tasks = get_tasks_by_type("todos")
    if tasks is None:
        await update.message.reply_text(
            "Could not connect to Habitica. Check your API credentials in .env."
        )
        return

    # Only show incomplete todos
    active = [t for t in tasks if not t.get("completed", False)]
    msg = format_task_list(active, "Your To-Dos:")
    await update.message.reply_text(msg)


async def handle_complete(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /complete TASK_NAME. Marks a task as complete."""
    args = context.args
    if not args:
        await update.message.reply_text(
            "Usage: /complete <task name>\n"
            "Example: /complete morning workout"
        )
        return

    task_name = " ".join(args)
    task = find_task_by_name(task_name)

    if not task:
        await update.message.reply_text(
            f"No matching task found for: {task_name}\n\n"
            "Try /habits, /daily, or /todo to see your tasks."
        )
        return

    result = score_task(task["id"], "up")
    if result:
        # Extract rewards from the score response
        gold_earned = result.get("gp", 0) - (result.get("_tmp", {}).get("quest", {}).get("progressDelta", 0) if isinstance(result.get("_tmp"), dict) else 0)
        xp_earned = result.get("exp", 0)

        await update.message.reply_text(
            f"Completed: {task.get('text', task_name)}\n\n"
            f"  +XP, +Gold earned.\n"
            f"  Keep it up."
        )
    else:
        await update.message.reply_text(
            f"Could not complete task: {task.get('text', task_name)}\n"
            "Check your Habitica API credentials."
        )


async def handle_hp(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /hp command. Shows current stats."""
    stats = get_user_stats()
    if not stats:
        await update.message.reply_text(
            "Could not fetch stats from Habitica. Check your API credentials in .env."
        )
        return
    await update.message.reply_text(format_stats(stats))


# -- Task completion detection -----------------------------------------------
def detect_completion_intent(text: str) -> Optional[str]:
    """
    Check if a message mentions completing a task.
    Returns the task name if detected, None otherwise.

    Matches patterns like:
    - "finished the workout"
    - "done with homework"
    - "completed morning routine"
    - "just did my meditation"
    """
    patterns = [
        r"(?:finished|done with|completed|just did|knocked out|wrapped up|got done with)\s+(?:the\s+|my\s+|a\s+)?(.+)",
        r"(.+?)(?:\s+is\s+)?(?:done|finished|completed|checked off)",
    ]
    text_lower = text.lower().strip()
    for pattern in patterns:
        match = re.search(pattern, text_lower)
        if match:
            task_name = match.group(1).strip().rstrip(".")
            if len(task_name) > 2:
                return task_name
    return None


async def suggest_habitica_completion(
    update: Update, context: ContextTypes.DEFAULT_TYPE, task_name: str
) -> bool:
    """
    When user mentions finishing something, check Habitica for a matching task
    and suggest completing it. Returns True if a suggestion was made.
    """
    if not HABITICA_USER_ID or not HABITICA_API_TOKEN:
        return False

    task = find_task_by_name(task_name)
    if not task:
        return False

    # Don't suggest if already completed
    if task.get("completed", False):
        return False

    task_text = task.get("text", task_name)
    task_id = task["id"]

    # Store the pending completion in bot_data for callback
    pending_key = f"habitica_pending_{update.message.message_id}"
    context.bot_data[pending_key] = task_id

    await update.message.reply_text(
        f"Sounds like you finished something. "
        f"Found matching Habitica task: \"{task_text}\"\n\n"
        f"Use /complete {task_text} to mark it done and earn XP."
    )
    return True

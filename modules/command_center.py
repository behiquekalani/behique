#!/usr/bin/env python3
# Copyright 2026 Behike. All rights reserved.
"""Telegram Command Center - controls the entire Behike business from Telegram."""

import json
import os
import subprocess
import asyncio
from datetime import datetime, timedelta
from pathlib import Path
from telegram import Update
from telegram.ext import ContextTypes, CommandHandler

DATA_DIR = Path(__file__).parent.parent / "Ceiba" / "telegram-data"
TOOLS_DIR = Path(__file__).parent.parent / "tools"
DATA_DIR.mkdir(parents=True, exist_ok=True)


def _load_json(name):
    path = DATA_DIR / f"{name}.json"
    if path.exists():
        with open(path) as f:
            return json.load(f)
    return {}


def _save_json(name, data):
    path = DATA_DIR / f"{name}.json"
    with open(path, "w") as f:
        json.dump(data, f, indent=2)


# --- Content Commands ---

async def cmd_news(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Top 5 AI stories today."""
    try:
        result = subprocess.run(
            ["python3", str(TOOLS_DIR / "ai_news_tracker.py"), "--top", "5"],
            capture_output=True, text=True, timeout=30
        )
        text = result.stdout[:3000] if result.stdout else "No stories found. Run the fetch first."
        await update.message.reply_text(f"*AI News Today*\n\n{text}", parse_mode="Markdown")
    except Exception as e:
        await update.message.reply_text(f"Error: {e}")


async def cmd_content(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Today's content calendar."""
    today = datetime.now().strftime("%Y-%m-%d")
    cal_file = Path(__file__).parent.parent / "Ceiba" / "news" / f"calendar-{today}.json"
    if cal_file.exists():
        with open(cal_file) as f:
            cal = json.load(f)
        lines = ["*Today's Content Calendar*\n"]
        for item in cal.get("posts", [])[:8]:
            lines.append(f"- {item.get('time', '?')} | @{item.get('account', '?')} | {item.get('type', '?')}")
        await update.message.reply_text("\n".join(lines), parse_mode="Markdown")
    else:
        await update.message.reply_text("No calendar for today. Run `/pipeline` first.")


async def cmd_pipeline(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Run the daily content pipeline."""
    await update.message.reply_text("Running pipeline... this takes ~60 seconds.")
    try:
        result = subprocess.run(
            ["python3", str(TOOLS_DIR / "ai_news_pipeline.py"), "--daily", "--no-tts"],
            capture_output=True, text=True, timeout=120
        )
        lines = result.stdout.split("\n")[-10:]
        await update.message.reply_text("*Pipeline Complete*\n\n" + "\n".join(lines), parse_mode="Markdown")
    except Exception as e:
        await update.message.reply_text(f"Pipeline error: {e}")


# --- Finance Commands ---

async def cmd_budget(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Quick budget entry. Usage: /budget food 25.50"""
    args = context.args
    if len(args) < 2:
        await update.message.reply_text("Usage: `/budget category amount`\nExample: `/budget food 25.50`", parse_mode="Markdown")
        return
    category = args[0].lower()
    try:
        amount = float(args[1])
    except ValueError:
        await update.message.reply_text("Amount must be a number.")
        return

    today = datetime.now().strftime("%Y-%m-%d")
    month = datetime.now().strftime("%Y-%m")
    budget = _load_json("budget")
    if month not in budget:
        budget[month] = {}
    if category not in budget[month]:
        budget[month][category] = []
    budget[month][category].append({"amount": amount, "date": today})
    _save_json("budget", budget)

    total = sum(e["amount"] for e in budget[month][category])
    await update.message.reply_text(f"Added ${amount:.2f} to *{category}*\nMonth total for {category}: ${total:.2f}", parse_mode="Markdown")


async def cmd_spent(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Today's total spending."""
    today = datetime.now().strftime("%Y-%m-%d")
    month = datetime.now().strftime("%Y-%m")
    budget = _load_json("budget")
    month_data = budget.get(month, {})
    total = 0
    lines = ["*Today's Spending*\n"]
    for cat, entries in month_data.items():
        day_total = sum(e["amount"] for e in entries if e["date"] == today)
        if day_total > 0:
            lines.append(f"- {cat}: ${day_total:.2f}")
            total += day_total
    lines.append(f"\n*Total: ${total:.2f}*")
    await update.message.reply_text("\n".join(lines), parse_mode="Markdown")


async def cmd_balance(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Monthly budget summary."""
    month = datetime.now().strftime("%Y-%m")
    budget = _load_json("budget")
    month_data = budget.get(month, {})
    lines = [f"*Budget Summary ({month})*\n"]
    grand_total = 0
    for cat, entries in sorted(month_data.items()):
        total = sum(e["amount"] for e in entries)
        grand_total += total
        lines.append(f"- {cat}: ${total:.2f}")
    lines.append(f"\n*Grand total: ${grand_total:.2f}*")
    await update.message.reply_text("\n".join(lines), parse_mode="Markdown")


# --- Focus/Wellness Commands ---

async def cmd_focus(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start a Pomodoro. Usage: /focus [minutes]"""
    minutes = int(context.args[0]) if context.args else 25
    await update.message.reply_text(f"Focus mode: {minutes} minutes. Go build something.")
    await asyncio.sleep(minutes * 60)
    await update.message.reply_text(f"Time is up. {minutes} minutes done. Take a break. You earned it.")


async def cmd_break_timer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Break timer. Usage: /break [minutes]"""
    minutes = int(context.args[0]) if context.args else 5
    await update.message.reply_text(f"Break: {minutes} minutes. Stretch. Water. Breathe.")
    await asyncio.sleep(minutes * 60)
    await update.message.reply_text("Break over. Back to building.")


async def cmd_mood(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Mood check-in. Usage: /mood [1-10]"""
    if not context.args:
        await update.message.reply_text("How are you? `/mood 7`", parse_mode="Markdown")
        return
    score = int(context.args[0])
    score = max(1, min(10, score))
    moods = _load_json("moods")
    today = datetime.now().strftime("%Y-%m-%d")
    now = datetime.now().strftime("%H:%M")
    if today not in moods:
        moods[today] = []
    moods[today].append({"score": score, "time": now})
    _save_json("moods", moods)
    emoji = ["", "", "", "", "", "", "", "", "", ""][score - 1]
    await update.message.reply_text(f"Mood logged: {score}/10 {emoji}")


async def cmd_breathe(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """60-second breathing guide."""
    await update.message.reply_text("Breathing exercise. 4-7-8 pattern.\n\nStarting now...")
    for i in range(4):
        await asyncio.sleep(1)
        await update.message.reply_text("Inhale... (4 seconds)")
        await asyncio.sleep(4)
        await update.message.reply_text("Hold... (7 seconds)")
        await asyncio.sleep(7)
        await update.message.reply_text("Exhale... (8 seconds)")
        await asyncio.sleep(8)
    await update.message.reply_text("Done. 4 cycles complete. How do you feel?")


# --- Business Commands ---

async def cmd_products(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """List all products with prices."""
    products = [
        ("The Behike Method", "$24.99"),
        ("AI Employee Guide", "$29.99"),
        ("Claude Code Course", "$39.99"),
        ("Ecommerce Playbook", "$14.99"),
        ("Solopreneur OS", "$19.99"),
        ("Behike Finance", "$14.99"),
        ("Behike Wellness", "$9.99"),
        ("Mastery for Builders", "$14.99"),
        ("AI Chatbot Guide", "$9.99"),
        ("Starter Pack (5 products)", "$59.99"),
        ("Content Franchise Kit", "$99.99"),
    ]
    lines = ["*Behike Products*\n"]
    for name, price in products:
        lines.append(f"- {name}: {price}")
    lines.append("\nbehike.gumroad.com")
    await update.message.reply_text("\n".join(lines), parse_mode="Markdown")


async def cmd_stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Business stats dashboard."""
    pdf_count = len(list(Path(__file__).parent.parent.glob("Ceiba/projects/content-empire/products/**/*.pdf")))
    tool_count = len(list(Path(__file__).parent.parent.glob("tools/*.py")))
    lines = [
        "*Behike Stats*\n",
        f"Products (PDF): {pdf_count}",
        f"Tools built: {tool_count}",
        f"Revenue: $0 (not launched yet)",
        f"Subscribers: 0",
    ]
    await update.message.reply_text("\n".join(lines), parse_mode="Markdown")


# --- System Commands ---

async def cmd_morning(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Morning briefing."""
    try:
        result = subprocess.run(
            ["python3", str(TOOLS_DIR / "ceiba_morning_brief.py"), "--short"],
            capture_output=True, text=True, timeout=30
        )
        text = result.stdout[:3000] if result.stdout else "Morning brief unavailable."
        await update.message.reply_text(text)
    except Exception as e:
        await update.message.reply_text(f"Brief error: {e}")


async def cmd_status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """System health check."""
    import shutil
    disk = shutil.disk_usage("/")
    free_gb = disk.free / (1024**3)
    lines = [
        "*System Status*\n",
        f"Disk free: {free_gb:.1f} GB",
        f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
        f"Tools: {len(list(TOOLS_DIR.glob('*.py')))} Python scripts",
    ]
    await update.message.reply_text("\n".join(lines), parse_mode="Markdown")


# --- Quick Capture ---

async def cmd_task(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Add task to MASTER_TODO. Usage: /task description"""
    if not context.args:
        await update.message.reply_text("Usage: `/task buy domain`", parse_mode="Markdown")
        return
    task_text = " ".join(context.args)
    todo_file = Path(__file__).parent.parent / "Ceiba" / "MASTER_TODO.md"
    with open(todo_file, "a") as f:
        f.write(f"\n### [TELEGRAM] {task_text}\n- Added: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n- Source: Telegram /task command\n")
    await update.message.reply_text(f"Task added: _{task_text}_", parse_mode="Markdown")


# --- Registration ---

def register_command_center(app):
    """Register all command center handlers with the Telegram app."""
    commands = {
        "news": cmd_news,
        "content": cmd_content,
        "pipeline": cmd_pipeline,
        "budget": cmd_budget,
        "spent": cmd_spent,
        "balance": cmd_balance,
        "focus": cmd_focus,
        "brk": cmd_break_timer,
        "mood": cmd_mood,
        "breathe": cmd_breathe,
        "products": cmd_products,
        "stats": cmd_stats,
        "morning": cmd_morning,
        "status": cmd_status,
        "task": cmd_task,
    }
    for name, handler in commands.items():
        app.add_handler(CommandHandler(name, handler))
    print(f"[CommandCenter] Registered {len(commands)} commands")

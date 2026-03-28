# Habitica Scheduled Automations
# Automated reminders, streak tracking, weekly reports, boss alerts
# Copyright 2026 Behike. All rights reserved.

import os
import logging
from datetime import datetime, timedelta

from telegram import Bot

from habitica_api import HabiticaClient, HabiticaAPIError

logging.basicConfig(
    format="%(asctime)s [%(name)s] %(levelname)s: %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------

TELEGRAM_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID", "")

# Streak milestone thresholds
STREAK_MILESTONES = [3, 7, 14, 30, 60, 100, 365]

# Boss damage danger threshold (HP below this = alert)
HP_DANGER_THRESHOLD = 10.0


def _get_bot() -> Bot:
    return Bot(token=TELEGRAM_TOKEN)


def _get_client() -> HabiticaClient:
    return HabiticaClient()


# ---------------------------------------------------------------------------
# 1. Daily Reminder - Send morning reminder of undone dailies at 7am
# ---------------------------------------------------------------------------


async def daily_reminder():
    """Send a morning message listing pending dailies for the day.

    Intended to run at 7:00 AM AST via scheduler (APScheduler, cron, etc.).
    """
    bot = _get_bot()
    client = _get_client()

    try:
        dailies = client.get_dailies()
    except HabiticaAPIError as e:
        logger.error("Failed to fetch dailies: %s", e)
        return

    # Filter to due and not yet completed
    pending = [d for d in dailies if d.get("isDue", True) and not d.get("completed", False)]

    if not pending:
        text = (
            "Buenos dias! No tienes dailies pendientes por ahora.\n"
            "Aprovecha el dia para avanzar en tus todos."
        )
    else:
        lines = [
            f"Buenos dias! Tienes {len(pending)} dailies pendientes hoy:\n"
        ]
        for d in pending:
            streak = d.get("streak", 0)
            streak_text = f" (racha: {streak} dias)" if streak > 0 else ""
            lines.append(f"  - {d['text']}{streak_text}")

        lines.append("\nA darle! Cada tarea completada es XP ganado.")
        text = "\n".join(lines)

    try:
        await bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=text)
        logger.info("Daily reminder sent. %d pending dailies.", len(pending))
    except Exception as e:
        logger.error("Failed to send daily reminder: %s", e)


# ---------------------------------------------------------------------------
# 2. Streak Check - Celebrate streak milestones
# ---------------------------------------------------------------------------


async def streak_check():
    """Check all dailies for streak milestones and celebrate them.

    Intended to run once daily, after cron (e.g., 1:00 AM or 8:00 AM).
    """
    bot = _get_bot()
    client = _get_client()

    try:
        dailies = client.get_dailies()
    except HabiticaAPIError as e:
        logger.error("Failed to fetch dailies for streak check: %s", e)
        return

    celebrations = []
    for d in dailies:
        streak = d.get("streak", 0)
        if streak in STREAK_MILESTONES:
            celebrations.append((d["text"], streak))

    if not celebrations:
        logger.info("No streak milestones hit today.")
        return

    lines = ["Rachas alcanzadas hoy:\n"]
    for task_name, days in celebrations:
        if days >= 100:
            lines.append(f"  {task_name}: {days} dias seguidos! Legendario!")
        elif days >= 30:
            lines.append(f"  {task_name}: {days} dias seguidos! Increible!")
        elif days >= 14:
            lines.append(f"  {task_name}: {days} dias seguidos! Imparable!")
        elif days >= 7:
            lines.append(f"  {task_name}: {days} dias seguidos! Gran semana!")
        else:
            lines.append(f"  {task_name}: {days} dias seguidos! Buen inicio!")

    lines.append("\nLa constancia es tu mejor arma. Sigue asi!")

    try:
        await bot.send_message(chat_id=TELEGRAM_CHAT_ID, text="\n".join(lines))
        logger.info("Streak celebration sent for %d milestones.", len(celebrations))
    except Exception as e:
        logger.error("Failed to send streak celebration: %s", e)


# ---------------------------------------------------------------------------
# 3. Weekly Report - Sunday summary
# ---------------------------------------------------------------------------


async def weekly_report():
    """Send a Sunday summary of tasks completed, XP earned, and streaks.

    Intended to run Sunday at 8:00 PM AST.
    """
    bot = _get_bot()
    client = _get_client()

    try:
        stats = client.get_user_stats()
        dailies = client.get_dailies()
        todos = client.get_todos()
        habits = client.get_habits()
    except HabiticaAPIError as e:
        logger.error("Failed to fetch data for weekly report: %s", e)
        return

    # Count completed dailies (today's snapshot)
    completed_dailies = sum(1 for d in dailies if d.get("completed", False))
    total_dailies = sum(1 for d in dailies if d.get("isDue", True))

    # Count completed todos
    completed_todos = sum(1 for t in todos if t.get("completed", False))

    # Find top streaks
    streaks = [(d["text"], d.get("streak", 0)) for d in dailies if d.get("streak", 0) > 0]
    streaks.sort(key=lambda x: x[1], reverse=True)
    top_streaks = streaks[:5]

    # Find most active habits
    active_habits = [(h["text"], round(h.get("value", 0), 1)) for h in habits]
    active_habits.sort(key=lambda x: x[1], reverse=True)
    top_habits = active_habits[:5]

    lines = [
        "REPORTE SEMANAL\n",
        f"Nivel: {stats['lvl']} ({stats['class'].capitalize()})",
        f"HP: {stats['hp']}/{stats['maxHealth']}",
        f"XP: {int(stats['exp'])}/{stats['toNextLevel']}",
        f"Oro: {stats['gp']}",
        "",
        f"Dailies hoy: {completed_dailies}/{total_dailies} completadas",
        f"Todos completados esta semana: {completed_todos}",
    ]

    if top_streaks:
        lines.append("\nMejores rachas:")
        for name, days in top_streaks:
            lines.append(f"  {name}: {days} dias")

    if top_habits:
        lines.append("\nHabitos mas fuertes:")
        for name, value in top_habits:
            sign = "+" if value >= 0 else ""
            lines.append(f"  {name}: {sign}{value}")

    lines.append("\nSigue asi! Cada semana que te presentas cuenta.")

    try:
        await bot.send_message(chat_id=TELEGRAM_CHAT_ID, text="\n".join(lines))
        logger.info("Weekly report sent.")
    except Exception as e:
        logger.error("Failed to send weekly report: %s", e)


# ---------------------------------------------------------------------------
# 4. Boss Damage Alert - Alert when party boss is about to deal damage
# ---------------------------------------------------------------------------


async def boss_damage_alert():
    """Check party members' HP and alert if anyone is dangerously low.

    When a boss quest is active, low HP means the member could die on
    next cron. This sends a warning so healers can act.

    Intended to run every 2-4 hours during active boss quests.
    """
    bot = _get_bot()
    client = _get_client()

    try:
        quest = client.get_quest_progress()
    except HabiticaAPIError as e:
        logger.error("Failed to fetch quest progress: %s", e)
        return

    # Only alert during active boss quests
    if not quest or not quest.get("active"):
        return

    # Check if it's a boss quest (has hp in progress)
    boss_hp = quest.get("progress", {}).get("hp")
    if boss_hp is None:
        return  # collection quest, no boss damage

    try:
        members = client.get_party_members()
    except HabiticaAPIError as e:
        logger.error("Failed to fetch party members: %s", e)
        return

    in_danger = []
    for m in members:
        hp = m.get("stats", {}).get("hp", 50)
        name = m.get("profile", {}).get("name", "???")
        if hp < HP_DANGER_THRESHOLD:
            in_danger.append((name, round(hp, 1)))

    if not in_danger:
        return

    lines = [
        "ALERTA DE BOSS\n",
        f"Boss HP restante: {round(boss_hp, 1)}\n",
        "Miembros en peligro:",
    ]
    for name, hp in in_danger:
        lines.append(f"  {name}: {hp} HP")

    lines.append(
        "\nSanadores, es hora de curar! "
        "Si no puedes completar tus dailies, usa la posada (/user/sleep)."
    )

    try:
        await bot.send_message(chat_id=TELEGRAM_CHAT_ID, text="\n".join(lines))
        logger.info("Boss damage alert sent. %d members in danger.", len(in_danger))
    except Exception as e:
        logger.error("Failed to send boss damage alert: %s", e)


# ---------------------------------------------------------------------------
# Scheduler setup (for use with APScheduler or standalone)
# ---------------------------------------------------------------------------


def setup_scheduler():
    """Configure and return an APScheduler instance with all automation jobs.

    Requires: pip install apscheduler

    Usage:
        scheduler = setup_scheduler()
        scheduler.start()
    """
    try:
        from apscheduler.schedulers.asyncio import AsyncIOScheduler
        from apscheduler.triggers.cron import CronTrigger
        from apscheduler.triggers.interval import IntervalTrigger
    except ImportError:
        logger.error("APScheduler not installed. Run: pip install apscheduler")
        raise

    scheduler = AsyncIOScheduler(timezone="America/Puerto_Rico")

    # Morning reminder at 7:00 AM AST
    scheduler.add_job(
        daily_reminder,
        CronTrigger(hour=7, minute=0),
        id="daily_reminder",
        name="Morning dailies reminder",
    )

    # Streak check at 8:00 AM AST
    scheduler.add_job(
        streak_check,
        CronTrigger(hour=8, minute=0),
        id="streak_check",
        name="Streak milestone check",
    )

    # Weekly report Sunday 8:00 PM AST
    scheduler.add_job(
        weekly_report,
        CronTrigger(day_of_week="sun", hour=20, minute=0),
        id="weekly_report",
        name="Sunday weekly report",
    )

    # Boss damage alert every 3 hours
    scheduler.add_job(
        boss_damage_alert,
        IntervalTrigger(hours=3),
        id="boss_damage_alert",
        name="Boss damage HP alert",
    )

    logger.info("Scheduler configured with %d jobs.", len(scheduler.get_jobs()))
    return scheduler


# ---------------------------------------------------------------------------
# Standalone runner
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import asyncio

    print("Habitica Automations - La Ceiba")
    print("================================")
    print("Funciones disponibles:")
    print("  daily_reminder()     - Recordatorio matutino de dailies")
    print("  streak_check()       - Celebrar rachas alcanzadas")
    print("  weekly_report()      - Reporte semanal dominical")
    print("  boss_damage_alert()  - Alerta de dano de boss")
    print()
    print("Para ejecutar con scheduler:")
    print("  scheduler = setup_scheduler()")
    print("  scheduler.start()")
    print()
    print("Para ejecutar una funcion manualmente:")
    print("  asyncio.run(daily_reminder())")

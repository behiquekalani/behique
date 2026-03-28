# Habitica Telegram Bot - La Ceiba Community
# Spanish-language bot for Habitica party management
# Copyright 2026 Behike. All rights reserved.

import os
import random
import logging
from difflib import SequenceMatcher

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
)

from habitica_api import HabiticaClient, HabiticaAPIError

logging.basicConfig(
    format="%(asctime)s [%(name)s] %(levelname)s: %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------

TELEGRAM_TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]

# Class name translations
CLASS_NAMES = {
    "warrior": "Guerrero",
    "mage": "Mago",
    "healer": "Sanador",
    "rogue": "Picaro",
}

# Priority labels
PRIORITY_LABELS = {
    0.1: "Trivial",
    1: "Facil",
    1.5: "Media",
    2: "Dificil",
}

# ---------------------------------------------------------------------------
# Motivational quotes pool (20, LATAM Spanish, "tu" form)
# ---------------------------------------------------------------------------

MOTIVACION_QUOTES = [
    "No tienes que ser perfecto, solo tienes que ser constante.",
    "Cada habito que completas es una victoria contra la version de ti que se rinde.",
    "El progreso no se mide en niveles, se mide en dias que decidiste no parar.",
    "Tu racha no define tu valor, pero si define tu disciplina.",
    "Hoy es el unico dia que importa. Manana ya veras.",
    "Los que llegan lejos no son los mas fuertes, son los que no se detienen.",
    "Un paso pequeno sigue siendo un paso. Muevete.",
    "La motivacion te empieza, la disciplina te termina.",
    "No esperes sentirte listo. Empieza y el impulso llega solo.",
    "Tus dailies son promesas que te haces a ti mismo. Cumplelas.",
    "El XP que ganas aqui refleja el esfuerzo que pones alla afuera.",
    "Si puedes abrir esta app, puedes completar una tarea. Hazlo.",
    "La perfeccion es enemiga del progreso. Marca la tarea y sigue.",
    "Tu yo del futuro te va a agradecer lo que hiciste hoy.",
    "No compitas con otros. Compite con quien eras ayer.",
    "Las excusas no dan XP. Las acciones si.",
    "Cada dia que te presentas, el boss pierde HP. Sigue.",
    "Tu equipo cuenta contigo. No los dejes abajo.",
    "El dolor de la disciplina pesa gramos. El del arrepentimiento, toneladas.",
    "Recuerda por que empezaste. Esa razon sigue ahi.",
]

# ---------------------------------------------------------------------------
# Daily challenge suggestions
# ---------------------------------------------------------------------------

RETOS = [
    "Haz 20 minutos de ejercicio sin excusas.",
    "Lee 10 paginas de un libro que tengas pendiente.",
    "Escribe 3 cosas por las que estas agradecido hoy.",
    "Medita 5 minutos. Solo respira.",
    "Organiza un espacio de tu casa que este desordenado.",
    "Toma 8 vasos de agua hoy. Lleva la cuenta.",
    "Habla con alguien que no hayas contactado en un mes.",
    "Aprende algo nuevo en 15 minutos (video, articulo, tutorial).",
    "Cocina algo saludable en vez de pedir delivery.",
    "Desconectate de redes sociales por 2 horas.",
    "Sal a caminar 15 minutos. Sin telefono.",
    "Completa la tarea que mas llevas posponiendo.",
    "Escribe tu meta mas importante y 3 pasos para lograrla.",
    "Acuestate 30 minutos antes de lo normal.",
    "Haz una lista de 5 cosas que te hacen feliz.",
]

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _get_client() -> HabiticaClient:
    """Build a HabiticaClient from env vars."""
    return HabiticaClient()


def _fuzzy_match(query: str, tasks: list[dict], threshold: float = 0.4) -> dict | None:
    """Find the best matching task by name using fuzzy matching."""
    query_lower = query.lower().strip()
    best_match = None
    best_score = threshold

    for task in tasks:
        text = task.get("text", "").lower()
        score = SequenceMatcher(None, query_lower, text).ratio()
        if score > best_score:
            best_score = score
            best_match = task
        # Also check startswith for quick prefix matches
        if text.startswith(query_lower) and score >= threshold:
            best_match = task
            break

    return best_match


def _hp_bar(current: float, maximum: float, length: int = 10) -> str:
    """Render a simple text-based HP/XP bar."""
    filled = int((current / maximum) * length) if maximum > 0 else 0
    return "█" * filled + "░" * (length - filled)


# ---------------------------------------------------------------------------
# Command Handlers
# ---------------------------------------------------------------------------


async def cmd_stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """/stats - Show user stats (HP, XP, Gold, Level, Class)."""
    try:
        client = _get_client()
        stats = client.get_user_stats()
    except HabiticaAPIError as e:
        await update.message.reply_text(f"Error al conectar con Habitica: {e.message}")
        return

    clase = CLASS_NAMES.get(stats["class"], stats["class"])
    hp_bar = _hp_bar(stats["hp"], stats["maxHealth"])
    xp_bar = _hp_bar(stats["exp"], stats["toNextLevel"])
    mp_bar = _hp_bar(stats["mp"], stats["maxMP"])

    text = (
        f"⚔ {stats['name']} - Nivel {stats['lvl']} ({clase})\n"
        f"\n"
        f"HP: {hp_bar} {stats['hp']}/{stats['maxHealth']}\n"
        f"XP: {xp_bar} {int(stats['exp'])}/{stats['toNextLevel']}\n"
        f"MP: {mp_bar} {int(stats['mp'])}/{stats['maxMP']}\n"
        f"Oro: {stats['gp']}\n"
    )

    await update.message.reply_text(text)


async def cmd_habits(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """/habits - List habits with + and - indicators."""
    try:
        client = _get_client()
        habits = client.get_habits()
    except HabiticaAPIError as e:
        await update.message.reply_text(f"Error: {e.message}")
        return

    if not habits:
        await update.message.reply_text("No tienes habitos registrados.")
        return

    lines = ["Tus habitos:\n"]
    buttons = []
    for h in habits:
        directions = ""
        if h.get("up"):
            directions += "+"
        if h.get("down"):
            directions += "-"
        value = round(h.get("value", 0), 1)
        sign = "+" if value >= 0 else ""
        lines.append(f"  [{directions}] {h['text']} ({sign}{value})")

        # Build inline buttons for scoring
        row = []
        if h.get("up"):
            row.append(InlineKeyboardButton(
                f"+ {h['text'][:15]}", callback_data=f"score|{h['_id']}|up"
            ))
        if h.get("down"):
            row.append(InlineKeyboardButton(
                f"- {h['text'][:15]}", callback_data=f"score|{h['_id']}|down"
            ))
        if row:
            buttons.append(row)

    markup = InlineKeyboardMarkup(buttons) if buttons else None
    await update.message.reply_text("\n".join(lines), reply_markup=markup)


async def cmd_dailies(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """/dailies - List today's dailies with completion status."""
    try:
        client = _get_client()
        dailies = client.get_dailies()
    except HabiticaAPIError as e:
        await update.message.reply_text(f"Error: {e.message}")
        return

    if not dailies:
        await update.message.reply_text("No tienes dailies registradas.")
        return

    # Filter to only due dailies
    due = [d for d in dailies if d.get("isDue", True)]
    done = [d for d in due if d.get("completed", False)]
    pending = [d for d in due if not d.get("completed", False)]

    lines = [f"Dailies de hoy: {len(done)}/{len(due)} completadas\n"]

    if pending:
        lines.append("Pendientes:")
        for d in pending:
            streak = d.get("streak", 0)
            streak_text = f" (racha: {streak})" if streak > 0 else ""
            lines.append(f"  [ ] {d['text']}{streak_text}")

    if done:
        lines.append("\nCompletadas:")
        for d in done:
            lines.append(f"  [x] {d['text']}")

    await update.message.reply_text("\n".join(lines))


async def cmd_todos(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """/todos - List todos sorted by priority."""
    try:
        client = _get_client()
        todos = client.get_todos()
    except HabiticaAPIError as e:
        await update.message.reply_text(f"Error: {e.message}")
        return

    # Filter out completed
    active = [t for t in todos if not t.get("completed", False)]

    if not active:
        await update.message.reply_text("No tienes todos pendientes. Buen trabajo!")
        return

    # Sort by priority descending (2 = hard, 0.1 = trivial)
    active.sort(key=lambda t: t.get("priority", 1), reverse=True)

    lines = [f"Todos pendientes ({len(active)}):\n"]
    for t in active:
        prio = t.get("priority", 1)
        label = PRIORITY_LABELS.get(prio, "?")
        lines.append(f"  [{label}] {t['text']}")

    await update.message.reply_text("\n".join(lines))


async def cmd_complete(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """/complete [task name] - Complete a task by name (fuzzy match)."""
    if not context.args:
        await update.message.reply_text("Usa: /complete <nombre de la tarea>")
        return

    query = " ".join(context.args)

    try:
        client = _get_client()
        all_tasks = client.get_tasks()
    except HabiticaAPIError as e:
        await update.message.reply_text(f"Error: {e.message}")
        return

    # Only score completable tasks (dailies, todos, habits with up)
    scoreable = [
        t for t in all_tasks
        if t["type"] in ("daily", "todo") or (t["type"] == "habit" and t.get("up"))
    ]

    match = _fuzzy_match(query, scoreable)
    if not match:
        await update.message.reply_text(
            f"No encontre una tarea parecida a \"{query}\".\n"
            "Intenta con mas caracteres del nombre."
        )
        return

    try:
        result = client.score_task(match["_id"], "up")
        delta = result.get("data", {})
        xp_gained = delta.get("exp", 0)
        gp_gained = delta.get("gp", 0)

        await update.message.reply_text(
            f"Tarea completada: {match['text']}\n"
            f"XP: +{int(xp_gained) if xp_gained else 0}  "
            f"Oro: +{round(gp_gained, 1) if gp_gained else 0}"
        )
    except HabiticaAPIError as e:
        await update.message.reply_text(f"Error al completar: {e.message}")


async def cmd_party(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """/party - Show party info and quest progress."""
    try:
        client = _get_client()
        party_data = client.get_party()
        party = party_data["data"]
    except HabiticaAPIError as e:
        await update.message.reply_text(f"Error: {e.message}")
        return

    name = party.get("name", "Sin nombre")
    member_count = party.get("memberCount", 0)
    lines = [f"Party: {name} ({member_count} miembros)\n"]

    quest = party.get("quest", {})
    if quest.get("key"):
        quest_key = quest["key"]
        active = quest.get("active", False)

        if active:
            progress = quest.get("progress", {})
            boss_hp = progress.get("hp")
            if boss_hp is not None:
                lines.append(f"Quest activa: {quest_key}")
                lines.append(f"Boss HP: {round(boss_hp, 1)}")
                lines.append(f"Dano del equipo acumulado: {round(progress.get('up', 0), 1)}")
            else:
                # Collection quest
                collect = progress.get("collect", {})
                lines.append(f"Quest activa: {quest_key} (recoleccion)")
                for item_key, count in collect.items():
                    lines.append(f"  {item_key}: {count}")
        else:
            # Pending quest
            members = quest.get("members", {})
            accepted = sum(1 for v in members.values() if v is True)
            total = len(members)
            lines.append(f"Quest pendiente: {quest_key}")
            lines.append(f"Aceptada por: {accepted}/{total}")
    else:
        lines.append("No hay quest activa.")

    await update.message.reply_text("\n".join(lines))


async def cmd_motivacion(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """/motivacion - Random motivational quote in Spanish."""
    quote = random.choice(MOTIVACION_QUOTES)
    await update.message.reply_text(f"\"{quote}\"")


async def cmd_reto(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """/reto - Daily challenge suggestion in Spanish."""
    reto = random.choice(RETOS)
    await update.message.reply_text(f"Reto del dia:\n\n{reto}\n\nAceptas el reto?")


# ---------------------------------------------------------------------------
# Callback handler for inline buttons (habit scoring)
# ---------------------------------------------------------------------------


async def handle_score_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle inline button presses for scoring habits."""
    query = update.callback_query
    await query.answer()

    parts = query.data.split("|")
    if len(parts) != 3 or parts[0] != "score":
        return

    _, task_id, direction = parts

    try:
        client = _get_client()
        client.score_task(task_id, direction)
        arrow = "+" if direction == "up" else "-"
        await query.edit_message_text(
            f"{query.message.text}\n\nHabito marcado ({arrow}). Buen trabajo!"
        )
    except HabiticaAPIError as e:
        await query.edit_message_text(f"Error al marcar habito: {e.message}")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main():
    """Start the bot."""
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

    # Commands
    app.add_handler(CommandHandler("stats", cmd_stats))
    app.add_handler(CommandHandler("habits", cmd_habits))
    app.add_handler(CommandHandler("dailies", cmd_dailies))
    app.add_handler(CommandHandler("todos", cmd_todos))
    app.add_handler(CommandHandler("complete", cmd_complete))
    app.add_handler(CommandHandler("party", cmd_party))
    app.add_handler(CommandHandler("motivacion", cmd_motivacion))
    app.add_handler(CommandHandler("reto", cmd_reto))

    # Inline button callbacks
    app.add_handler(CallbackQueryHandler(handle_score_callback))

    logger.info("Bot iniciado. Escuchando comandos...")
    app.run_polling()


if __name__ == "__main__":
    main()

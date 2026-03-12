import logging
import os
import json
from datetime import datetime
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, ContextTypes, filters

from modules.classifier import classify_input
from modules.memory import save_entry, update_entry, find_related_entry, log_to_archive, get_daily_summary

load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# ── VOICE HANDLER ──────────────────────────────────────────────────────────────
async def handle_voice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    from openai import OpenAI
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    voice = update.message.voice
    file = await context.bot.get_file(voice.file_id)

    # Download voice file
    file_path = f"/tmp/{voice.file_id}.ogg"
    await file.download_to_drive(file_path)

    # Transcribe with Whisper
    with open(file_path, "rb") as audio_file:
        transcript = client.audio.transcriptions.create(
            model="whisper-1",
            file=audio_file
        )

    text = transcript.text.strip()
    logger.info(f"Voice transcribed: {text}")

    # Process the transcribed text exactly like a text message
    await process_message(update, context, text, source="voice")


# ── TEXT HANDLER ───────────────────────────────────────────────────────────────
async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()
    await process_message(update, context, text, source="text")


# ── CORE PROCESSOR ─────────────────────────────────────────────────────────────
async def process_message(update: Update, context: ContextTypes.DEFAULT_TYPE, text: str, source: str):
    user_id = str(update.message.from_user.id)
    timestamp = datetime.now().isoformat()

    # 1. Always log to raw archive first (never lost)
    log_to_archive(user_id, text, source, timestamp)

    # 2. Check if this is an update to an existing entry
    related = find_related_entry(user_id, text)

    if related:
        # Update the living document
        updated = update_entry(user_id, related["id"], text, timestamp)
        response = build_update_response(updated, text)
    else:
        # Classify and create new entry
        classification = classify_input(text)
        entry = save_entry(user_id, text, classification, source, timestamp)
        response = build_new_entry_response(entry)

    await update.message.reply_text(response, parse_mode="Markdown")


# ── RESPONSE BUILDERS ──────────────────────────────────────────────────────────
def build_new_entry_response(entry: dict) -> str:
    category = entry["category"]
    niche = entry["niche"]
    pillar = entry["life_pillar"]
    entry_id = entry["id"][:8]

    category_emoji = {
        "CREATIVE": "🎨",
        "BUSINESS": "💼",
        "KNOWLEDGE": "🧠",
        "PERSONAL": "🌱",
        "TECHNICAL": "⚙️"
    }.get(category, "📌")

    pillar_emoji = {
        "health": "💚",
        "wealth": "💰",
        "relationships": "🤝",
        "general": "✨"
    }.get(pillar, "✨")

    return (
        f"{category_emoji} *{category}* → {niche}\n"
        f"{pillar_emoji} Life pillar: *{pillar}*\n"
        f"🆔 `{entry_id}`\n\n"
        f"_Saved. Send a follow-up to add to this idea._"
    )


def build_update_response(entry: dict, new_text: str) -> str:
    updates_count = len(entry.get("updates", []))
    return (
        f"🔄 *Updated existing idea*\n"
        f"📌 {entry['seed'][:60]}{'...' if len(entry['seed']) > 60 else ''}\n\n"
        f"➕ Added update #{updates_count}\n"
        f"_Original seed preserved. Total updates: {updates_count}_"
    )


# ── MAIN ───────────────────────────────────────────────────────────────────────
def main():
    logger.info("Behique is running...")
    app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()

    app.add_handler(MessageHandler(filters.VOICE, handle_voice))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))

    app.run_polling()


if __name__ == "__main__":
    main()

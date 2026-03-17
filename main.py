import logging
import os
import json
from datetime import datetime
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, CommandHandler, ContextTypes, filters

from modules.classifier import classify_input
from modules.memory import save_entry, update_entry, find_related_entry, log_to_archive, get_daily_summary
from modules.ebay_command import handle_ebay_command

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

    # 2. Check if this is a Telegram reply to one of Behique's messages
    replied_entry_id = None
    if update.message.reply_to_message:
        # Look up which entry this reply message ID maps to
        replied_entry_id = context.bot_data.get(
            str(update.message.reply_to_message.message_id)
        )

    if replied_entry_id:
        # Direct reply — update that specific entry
        updated = update_entry(user_id, replied_entry_id, text, timestamp)
        if updated:
            response = build_update_response(updated, text)
        else:
            # Fallback — save as new if entry not found
            classification = classify_input(text)
            entry = save_entry(user_id, text, classification, source, timestamp)
            response = build_new_entry_response(entry)
    else:
        # 3. No reply — check AI context matching for related ideas
        related = find_related_entry(user_id, text)
        if related:
            updated = update_entry(user_id, related["id"], text, timestamp)
            response = build_update_response(updated, text)
        else:
            # Brand new idea
            classification = classify_input(text)
            entry = save_entry(user_id, text, classification, source, timestamp)
            # Store the bot's reply message ID → entry ID mapping
            sent = await update.message.reply_text(
                build_new_entry_response(entry), parse_mode="Markdown"
            )
            context.bot_data[str(sent.message_id)] = entry["id"]
            return

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

    app.add_handler(CommandHandler("ebay", handle_ebay_command))
    app.add_handler(MessageHandler(filters.VOICE, handle_voice))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))

    app.run_polling()


if __name__ == "__main__":
    main()

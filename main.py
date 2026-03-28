import logging
import os
import json
from datetime import datetime
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, CommandHandler, ContextTypes, filters

from modules.classifier import classify_input
from modules.memory import save_entry, update_entry, find_related_entry, log_to_archive, get_daily_summary
from modules.idea_splitter import split_ideas
from modules.idea_matcher import match_idea
from modules.ebay_command import handle_ebay_command
from modules.transcribe_command import handle_transcribe_command, handle_auto_transcribe
from modules.link_handler import extract_urls, handle_link

load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN") or os.getenv("TELEGRAM_TOKEN")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# ── VOICE HANDLER ──────────────────────────────────────────────────────────────
async def handle_voice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    import subprocess
    import tempfile
    from openai import OpenAI

    ogg_path = None
    mp3_path = None

    try:
        client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

        voice = update.message.voice
        if not voice:
            logger.warning("handle_voice called but no voice in message")
            return

        file = await context.bot.get_file(voice.file_id)

        # Download voice file to a temp directory
        tmp_dir = tempfile.mkdtemp(prefix="behique_voice_")
        ogg_path = os.path.join(tmp_dir, f"{voice.file_id}.oga")
        await file.download_to_drive(ogg_path)
        logger.info(f"Voice downloaded: {ogg_path} ({voice.duration}s)")

        # Convert OGA/OGG to MP3 with ffmpeg (OpenAI Whisper API is picky about codecs)
        mp3_path = os.path.join(tmp_dir, f"{voice.file_id}.mp3")
        ffmpeg_result = subprocess.run(
            ["ffmpeg", "-y", "-i", ogg_path, "-acodec", "libmp3lame", "-ar", "16000", "-ac", "1", mp3_path],
            capture_output=True, text=True, timeout=30
        )
        if ffmpeg_result.returncode != 0:
            logger.error(f"ffmpeg conversion failed: {ffmpeg_result.stderr}")
            await update.message.reply_text("Error processing voice message. Could not convert audio.")
            return

        # Transcribe with OpenAI Whisper API
        with open(mp3_path, "rb") as audio_file:
            transcript = client.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file
            )

        text = transcript.text.strip()
        if not text:
            await update.message.reply_text("Could not detect any speech in that voice message.")
            return

        logger.info(f"Voice transcribed: {text}")

        # Process the transcribed text exactly like a text message
        await process_message(update, context, text, source="voice")

    except subprocess.TimeoutExpired:
        logger.error("ffmpeg timed out during voice conversion")
        await update.message.reply_text("Voice processing timed out. Try a shorter message.")
    except Exception as e:
        logger.error(f"Voice handler error: {e}", exc_info=True)
        await update.message.reply_text(f"Error processing voice message: {str(e)[:200]}")
    finally:
        # Clean up temp files
        if ogg_path and os.path.exists(os.path.dirname(ogg_path)):
            import shutil
            shutil.rmtree(os.path.dirname(ogg_path), ignore_errors=True)


# ── TEXT HANDLER ───────────────────────────────────────────────────────────────
async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()

    # Auto-detect video URLs and transcribe them (YouTube, etc.)
    if await handle_auto_transcribe(update, context):
        return  # Handled as transcription

    # Detect URLs — route to link intake pipeline
    urls = extract_urls(text)
    if urls:
        # If the message is ONLY a URL (no other text), route entirely to link handler
        stripped = text.strip()
        for url in urls:
            stripped = stripped.replace(url, "").strip()

        if not stripped:
            # Pure URL message: route to link handler for all URLs
            for url in urls:
                await handle_link(update, context, url)
            return
        else:
            # Mixed message (URL + text): capture the URL as a reference,
            # then also process the text as a normal idea
            for url in urls:
                await handle_link(update, context, url)
            await process_message(update, context, stripped, source="text")
            return

    await process_message(update, context, text, source="text")


# ── CORE PROCESSOR ─────────────────────────────────────────────────────────────
async def process_message(update: Update, context: ContextTypes.DEFAULT_TYPE, text: str, source: str):
    user_id = str(update.message.from_user.id)
    timestamp = datetime.now().isoformat()

    # 1. Always log the full raw message to archive first (never lost)
    log_to_archive(user_id, text, source, timestamp)

    # 2. Check if this is a Telegram reply to one of Behique's messages
    replied_entry_id = None
    if update.message.reply_to_message:
        replied_entry_id = context.bot_data.get(
            str(update.message.reply_to_message.message_id)
        )

    if replied_entry_id:
        # Direct reply: update that specific entry (no splitting needed)
        updated = update_entry(user_id, replied_entry_id, text, timestamp)
        if updated:
            response = build_update_response(updated, text)
        else:
            classification = classify_input(text)
            entry = save_entry(user_id, text, classification, source, timestamp)
            response = build_new_entry_response(entry)
        await update.message.reply_text(response, parse_mode="Markdown")
        return

    # 3. Split the message into individual ideas
    ideas = split_ideas(text)
    total = len(ideas)

    if total > 1:
        logger.info(f"Message split into {total} ideas")

    # 4. Process each idea independently
    responses = []
    for i, idea_text in enumerate(ideas):
        result = await _process_single_idea(
            update, context, user_id, idea_text, source, timestamp
        )
        responses.append(result)

    # 5. Send response(s)
    if total == 1:
        # Single idea: send normally and track the message ID
        resp_text, entry = responses[0]
        sent = await update.message.reply_text(resp_text, parse_mode="Markdown")
        if entry and not entry.get("_was_update"):
            context.bot_data[str(sent.message_id)] = entry["id"]
    else:
        # Multiple ideas: send a combined response
        parts = []
        for idx, (resp_text, entry) in enumerate(responses):
            parts.append(f"*Idea {idx + 1}/{total}:*\n{resp_text}")
        combined = "\n\n---\n\n".join(parts)
        await update.message.reply_text(combined, parse_mode="Markdown")


async def _process_single_idea(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    user_id: str,
    idea_text: str,
    source: str,
    timestamp: str,
) -> tuple:
    """
    Process one idea through the matcher and classifier pipeline.
    Returns (response_text, entry_dict).
    The entry_dict has a temporary '_was_update' key if it was an update.
    """
    # First, try keyword-based matching against recent ideas
    match_result = match_idea(user_id, idea_text)

    if match_result["is_update"] and match_result["matched_id"]:
        updated = update_entry(user_id, match_result["matched_id"], idea_text, timestamp)
        if updated:
            updated["_was_update"] = True
            return build_update_response(updated, idea_text), updated

    # No match found, or match failed. Try the existing LLM-based matcher as backup.
    related = find_related_entry(user_id, idea_text)
    if related:
        updated = update_entry(user_id, related["id"], idea_text, timestamp)
        if updated:
            updated["_was_update"] = True
            return build_update_response(updated, idea_text), updated

    # Brand new idea
    classification = classify_input(idea_text)
    entry = save_entry(user_id, idea_text, classification, source, timestamp)
    return build_new_entry_response(entry), entry


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
    app.add_handler(CommandHandler("transcribe", handle_transcribe_command))
    app.add_handler(MessageHandler(filters.VOICE, handle_voice))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))

    app.run_polling()


if __name__ == "__main__":
    main()

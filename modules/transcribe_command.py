"""
transcribe_command.py — Telegram /transcribe handler for BehiqueBot.

Send a URL (Instagram Reel, TikTok, YouTube Short, etc.) and get back
the transcribed text directly in Telegram.

Usage in Telegram:
    /transcribe https://www.instagram.com/reel/ABC123/
    /transcribe https://www.youtube.com/shorts/xyz

Or just paste a URL as a regular message — the bot auto-detects links
to video platforms and offers to transcribe.
"""

import logging
import os
import re
import shutil
import subprocess
import tempfile
from pathlib import Path

from telegram import Update
from telegram.ext import ContextTypes

logger = logging.getLogger(__name__)

# Where transcripts are saved (same as ceiba_transcribe.py)
OUTPUT_DIR = Path(os.getenv(
    "TRANSCRIBE_OUTPUT_DIR",
    str(Path.home() / "behique" / "Ceiba" / "07-Transcripts")
))

# Whisper model — tiny for speed on Railway, base for local
WHISPER_MODEL = os.getenv("WHISPER_MODEL", "tiny")

# Video URL patterns we auto-detect
VIDEO_URL_PATTERNS = [
    r"https?://(?:www\.)?instagram\.com/reel/",
    r"https?://(?:www\.)?tiktok\.com/",
    r"https?://(?:vm\.)?tiktok\.com/",
    r"https?://(?:www\.)?youtube\.com/shorts/",
    r"https?://youtu\.be/",
    r"https?://(?:www\.)?youtube\.com/watch",
    r"https?://(?:www\.)?twitter\.com/.*/video",
    r"https?://(?:www\.)?x\.com/.*/video",
]

VIDEO_URL_RE = re.compile("|".join(VIDEO_URL_PATTERNS), re.IGNORECASE)


def is_video_url(text: str) -> bool:
    """Check if text contains a video platform URL."""
    return bool(VIDEO_URL_RE.search(text))


def extract_url(text: str) -> str | None:
    """Extract first URL from text."""
    match = re.search(r"https?://\S+", text)
    return match.group(0) if match else None


async def handle_transcribe_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /transcribe <url> command."""
    if not context.args:
        await update.message.reply_text(
            "🎙️ *Transcribe*\n\n"
            "Send a video URL to transcribe:\n"
            "`/transcribe https://instagram.com/reel/ABC123/`\n\n"
            "Supports: Instagram Reels, TikTok, YouTube Shorts, YouTube videos",
            parse_mode="Markdown"
        )
        return

    url = context.args[0]
    await _transcribe_and_reply(update, url)


async def handle_auto_transcribe(update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
    """
    Check if a regular text message contains a video URL.
    If so, auto-transcribe it. Returns True if handled.
    """
    text = update.message.text.strip()
    if not is_video_url(text):
        return False

    url = extract_url(text)
    if not url:
        return False

    await update.message.reply_text(
        "🎙️ Detected video link — transcribing...",
        parse_mode="Markdown"
    )
    await _transcribe_and_reply(update, url)
    return True


async def _transcribe_and_reply(update: Update, url: str):
    """Download, transcribe, and reply with the transcript."""
    status_msg = await update.message.reply_text("⏳ Downloading video...")

    tmp_dir = tempfile.mkdtemp(prefix="behique_transcribe_")

    try:
        # Step 1: Download with yt-dlp
        output_template = os.path.join(tmp_dir, "%(title).80s.%(ext)s")
        cmd_dl = [
            "yt-dlp",
            "--no-playlist",
            "-f", "bestaudio/best",
            "-o", output_template,
            "--print", "after_move:filepath",
            "--print", "%(title)s",
            "--no-warnings",
            url,
        ]

        result = subprocess.run(cmd_dl, capture_output=True, text=True, timeout=120)
        if result.returncode != 0:
            await status_msg.edit_text(f"❌ Download failed:\n`{result.stderr[:200]}`", parse_mode="Markdown")
            return

        lines = result.stdout.strip().split("\n")
        title = lines[0].strip() if len(lines) >= 2 else "Unknown"
        filepath = lines[1].strip() if len(lines) >= 2 else lines[0].strip()

        if not os.path.isfile(filepath):
            # Fallback: find any file in tmp_dir
            for f in os.listdir(tmp_dir):
                full = os.path.join(tmp_dir, f)
                if os.path.isfile(full):
                    filepath = full
                    break
            else:
                await status_msg.edit_text("❌ Downloaded file not found")
                return

        # Step 2: Extract audio with ffmpeg
        await status_msg.edit_text("🔊 Extracting audio...")
        wav_path = os.path.join(tmp_dir, "audio.wav")
        cmd_ff = [
            "ffmpeg", "-y", "-i", filepath,
            "-vn", "-acodec", "pcm_s16le", "-ar", "16000", "-ac", "1",
            wav_path,
        ]
        ff_result = subprocess.run(cmd_ff, capture_output=True, text=True, timeout=60)
        if ff_result.returncode != 0:
            await status_msg.edit_text("❌ Audio extraction failed")
            return

        # Step 3: Transcribe with Whisper
        await status_msg.edit_text("🧠 Transcribing with Whisper...")

        import whisper
        model = whisper.load_model(WHISPER_MODEL)
        whisper_result = model.transcribe(wav_path)

        text = whisper_result.get("text", "").strip()
        language = whisper_result.get("language", "unknown")

        if not text:
            await status_msg.edit_text("⚠️ No speech detected in this video.")
            return

        # Step 4: Format and send response
        # Telegram max message = 4096 chars
        header = f"🎙️ *Transcript* — {title[:60]}\n🌐 Language: `{language}`\n\n"

        if len(header) + len(text) > 4000:
            # Split into chunks
            chunks = [text[i:i+3500] for i in range(0, len(text), 3500)]
            await status_msg.edit_text(header + chunks[0], parse_mode="Markdown")
            for chunk in chunks[1:]:
                await update.message.reply_text(chunk)
        else:
            await status_msg.edit_text(header + text, parse_mode="Markdown")

        # Step 5: Save to disk (if running locally)
        try:
            _save_transcript(title, url, text, language, whisper_result)
            logger.info(f"Transcript saved for: {title}")
        except Exception as e:
            logger.warning(f"Could not save transcript to disk: {e}")

    except subprocess.TimeoutExpired:
        await status_msg.edit_text("❌ Operation timed out. Try a shorter video.")
    except Exception as e:
        logger.error(f"Transcription error: {e}", exc_info=True)
        await status_msg.edit_text(f"❌ Error: {str(e)[:200]}")
    finally:
        shutil.rmtree(tmp_dir, ignore_errors=True)


def _save_transcript(title: str, source: str, text: str, language: str, result: dict):
    """Save transcript to Ceiba vault (same format as ceiba_transcribe.py)."""
    import json
    from datetime import datetime

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    safe_title = re.sub(r'[\\/*?:"<>|]', "", title)
    safe_title = re.sub(r"\s+", "_", safe_title.strip())[:80]
    date_prefix = datetime.now().strftime("%Y-%m-%d")
    base_name = f"{date_prefix}_{safe_title}"

    txt_path = OUTPUT_DIR / f"{base_name}.txt"
    json_path = OUTPUT_DIR / f"{base_name}.json"

    # Plain text
    txt_path.write_text(
        f"# Transcription: {title}\n# Source: {source}\n# Language: {language}\n\n{text}",
        encoding="utf-8"
    )

    # JSON with segments
    segments = []
    for seg in result.get("segments", []):
        segments.append({
            "start": round(seg["start"], 3),
            "end": round(seg["end"], 3),
            "text": seg["text"].strip(),
        })

    json_data = {
        "title": title,
        "source": source,
        "language": language,
        "date": date_prefix,
        "text": text,
        "segments": segments,
        "via": "telegram_bot",
    }
    json_path.write_text(json.dumps(json_data, ensure_ascii=False, indent=2), encoding="utf-8")

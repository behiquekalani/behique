import os
import json
import logging
from datetime import datetime
from dotenv import load_dotenv
from openai import OpenAI
from telegram import Update
from telegram.ext import Application, MessageHandler, CommandHandler, filters, ContextTypes

load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
DATA_FILE = "behique_data.json"

client = OpenAI(api_key=OPENAI_API_KEY)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

CATEGORIES = {
    "idea": "💡 Ideas",
    "task_personal": "✅ Personal Tasks",
    "task_business": "💼 Business Tasks",
    "event": "📅 Events",
    "project": "🏢 Projects",
    "contact": "👤 Contacts",
    "journal": "📓 Journal",
    "reminder": "⏰ Reminders"
}

def load_data():
    if not os.path.exists(DATA_FILE):
        data = {cat: [] for cat in CATEGORIES}
        save_data(data)
        return data
    with open(DATA_FILE, "r") as f:
        return json.load(f)

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=2)

def classify_input(text):
    prompt = f"""You are Behique, a personal AI assistant. Analyze the following input and return a JSON object with these fields:

- category: one of [idea, task_personal, task_business, event, project, contact, journal, reminder]
- title: a short title (max 6 words)
- summary: a one sentence summary
- urgency: one of [low, medium, high, critical] — only if relevant, otherwise null
- deadline: extract any date/time mentioned in plain text, otherwise null
- project: extract any project or business name mentioned, otherwise null
- tags: list of 1-3 relevant tags

Input: "{text}"

Respond ONLY with valid JSON, no extra text."""

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}],
        response_format={"type": "json_object"}
    )
    return json.loads(response.choices[0].message.content)

def save_entry(category, entry):
    data = load_data()
    if category not in data:
        data[category] = []
    data[category].append(entry)
    save_data(data)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 I'm Behique — your personal AI chief of staff.\n\n"
        "Just tell me anything. An idea, a task, a reminder, a thought.\n"
        "I'll classify it and save it for you.\n\n"
        "Try saying: *Change brake pads before Tuesday 2pm*",
        parse_mode="Markdown"
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    await update.message.reply_text("🧠 Processing...")

    try:
        result = classify_input(text)

        category = result.get("category", "journal")
        title = result.get("title", "Untitled")
        summary = result.get("summary", text)
        urgency = result.get("urgency")
        deadline = result.get("deadline")
        project = result.get("project")
        tags = result.get("tags", [])

        entry = {
            "id": datetime.now().isoformat(),
            "title": title,
            "raw": text,
            "summary": summary,
            "urgency": urgency,
            "deadline": deadline,
            "project": project,
            "tags": tags,
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M")
        }

        save_entry(category, entry)

        category_label = CATEGORIES.get(category, "📥 Inbox")
        urgency_line = f"⚡ Urgency: {urgency.upper()}" if urgency else ""
        deadline_line = f"📅 Deadline: {deadline}" if deadline else ""
        project_line = f"🏢 Project: {project}" if project else ""
        tags_line = f"🏷 Tags: {', '.join(tags)}" if tags else ""

        details = "\n".join(filter(None, [urgency_line, deadline_line, project_line, tags_line]))

        reply = (
            f"✅ *{title}*\n"
            f"Saved to {category_label}\n\n"
            f"{summary}\n\n"
            f"{details}"
        ).strip()

        await update.message.reply_text(reply, parse_mode="Markdown")

    except Exception as e:
        logger.error(f"Error: {e}")
        await update.message.reply_text("❌ Something went wrong. Try again.")

async def handle_voice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🎙 Transcribing your voice message...")

    try:
        file = await update.message.voice.get_file()
        file_path = "voice_temp.ogg"
        await file.download_to_drive(file_path)

        with open(file_path, "rb") as audio:
            transcription = client.audio.transcriptions.create(
                model="whisper-1",
                file=audio
            )

        text = transcription.text
        await update.message.reply_text(f"📝 I heard: _{text}_", parse_mode="Markdown")

        update.message.text = text
        await handle_message(update, context)

        os.remove(file_path)

    except Exception as e:
        logger.error(f"Voice error: {e}")
        await update.message.reply_text("❌ Couldn't process voice. Try again.")

async def show_all(update: Update, context: ContextTypes.DEFAULT_TYPE):
    data = load_data()
    reply = "📂 *Everything in Behique:*\n\n"

    for category, label in CATEGORIES.items():
        entries = data.get(category, [])
        if entries:
            reply += f"{label} ({len(entries)})\n"
            for e in entries[-3:]:
                reply += f"  • {e['title']}\n"
            reply += "\n"

    if reply == "📂 *Everything in Behique:*\n\n":
        reply = "Nothing saved yet. Just tell me something!"

    await update.message.reply_text(reply, parse_mode="Markdown")

def main():
    app = Application.builder().token(TELEGRAM_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("all", show_all))
    app.add_handler(MessageHandler(filters.VOICE, handle_voice))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    logger.info("Behique is running...")
    app.run_polling()

if __name__ == "__main__":
    main()
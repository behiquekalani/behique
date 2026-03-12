import json
import os
import uuid
from datetime import datetime
from openai import OpenAI

# ── STORAGE PATHS ──────────────────────────────────────────────────────────────
DATA_DIR = "data"
ENTRIES_FILE = os.path.join(DATA_DIR, "entries.json")
ARCHIVE_DIR = os.path.join(DATA_DIR, "archive")

def ensure_dirs():
    os.makedirs(DATA_DIR, exist_ok=True)
    os.makedirs(ARCHIVE_DIR, exist_ok=True)

def load_entries() -> list:
    ensure_dirs()
    if not os.path.exists(ENTRIES_FILE):
        return []
    with open(ENTRIES_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_entries(entries: list):
    ensure_dirs()
    with open(ENTRIES_FILE, "w", encoding="utf-8") as f:
        json.dump(entries, f, ensure_ascii=False, indent=2)


# ── RAW ARCHIVE (never touched, always grows) ──────────────────────────────────
def log_to_archive(user_id: str, text: str, source: str, timestamp: str):
    """Log every single raw input to a daily archive file. Never deleted, never edited."""
    ensure_dirs()
    date_str = timestamp[:10]  # YYYY-MM-DD
    archive_file = os.path.join(ARCHIVE_DIR, f"{date_str}.jsonl")

    entry = {
        "timestamp": timestamp,
        "user_id": user_id,
        "source": source,  # "text" or "voice"
        "raw": text
    }

    with open(archive_file, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")


# ── FIND RELATED ENTRY (for living document updates) ───────────────────────────
def find_related_entry(user_id: str, text: str) -> dict | None:
    """
    Use OpenAI to check if this message is an update to an existing idea.
    Returns the most related entry if found, None otherwise.
    """
    entries = load_entries()
    user_entries = [e for e in entries if e.get("user_id") == user_id]

    if not user_entries:
        return None

    # Only check the last 20 entries for relevance (recency bias)
    recent = user_entries[-20:]

    # Build a quick summary list for the AI to evaluate
    summaries = "\n".join([
        f"ID: {e['id'][:8]} | {e['category']} | {e['classification']['summary']}"
        for e in recent
    ])

    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    system = """You are a memory matcher for a personal assistant.
Given a new message and a list of recent ideas, determine if the new message is clearly
a follow-up, update, or addition to one of the existing ideas.

Only match if you are confident (>80%) it's related.
If it's a new standalone idea, return null.

Respond ONLY with JSON: {"match_id": "abc12345"} or {"match_id": null}"""

    user_msg = f"New message: \"{text}\"\n\nRecent ideas:\n{summaries}"

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": user_msg}
            ],
            temperature=0,
            response_format={"type": "json_object"}
        )

        result = json.loads(response.choices[0].message.content)
        match_id_prefix = result.get("match_id")

        if not match_id_prefix:
            return None

        # Find the full entry by ID prefix
        for entry in recent:
            if entry["id"].startswith(match_id_prefix):
                return entry

        return None

    except Exception:
        return None


# ── SAVE NEW ENTRY ─────────────────────────────────────────────────────────────
def save_entry(user_id: str, text: str, classification: dict, source: str, timestamp: str) -> dict:
    entries = load_entries()

    entry = {
        "id": str(uuid.uuid4()),
        "user_id": user_id,
        "seed": text,                    # Original — never modified
        "source": source,
        "timestamp": timestamp,
        "category": classification["category"],
        "niche": classification["niche"],
        "life_pillar": classification["life_pillar"],
        "classification": classification,
        "updates": [],                   # All future additions go here
        "tags": classification.get("tags", [])
    }

    entries.append(entry)
    save_entries(entries)
    return entry


# ── UPDATE EXISTING ENTRY (living document) ────────────────────────────────────
def update_entry(user_id: str, entry_id: str, new_text: str, timestamp: str) -> dict:
    entries = load_entries()

    for entry in entries:
        if entry["id"] == entry_id and entry["user_id"] == user_id:
            update = {
                "timestamp": timestamp,
                "text": new_text,
                "update_number": len(entry["updates"]) + 1
            }
            entry["updates"].append(update)
            entry["last_updated"] = timestamp
            save_entries(entries)
            return entry

    return None


# ── DAILY SUMMARY (optional, for future use) ───────────────────────────────────
def get_daily_summary(user_id: str, date_str: str = None) -> dict:
    """Get all entries and archive logs for a given day."""
    if not date_str:
        date_str = datetime.now().strftime("%Y-%m-%d")

    # Archive logs for the day
    archive_file = os.path.join(ARCHIVE_DIR, f"{date_str}.jsonl")
    raw_logs = []
    if os.path.exists(archive_file):
        with open(archive_file, "r", encoding="utf-8") as f:
            for line in f:
                raw_logs.append(json.loads(line.strip()))

    # Entries created on this day
    entries = load_entries()
    day_entries = [
        e for e in entries
        if e.get("user_id") == user_id and e["timestamp"].startswith(date_str)
    ]

    return {
        "date": date_str,
        "raw_log_count": len(raw_logs),
        "entries_created": len(day_entries),
        "raw_logs": raw_logs,
        "entries": day_entries
    }

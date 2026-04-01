"""
persistent_bot_data.py -- Persist bot_data mapping across Railway redeploys.

Stores message_id -> entry_id mappings in a JSON file so reply-based
thread continuation works even after bot restarts.
"""

import json
import logging
import os

logger = logging.getLogger(__name__)

DATA_DIR = "data"
BOT_DATA_FILE = os.path.join(DATA_DIR, "bot_data.json")


def load_bot_data():
    """Load persistent bot_data from disk."""
    os.makedirs(DATA_DIR, exist_ok=True)
    if not os.path.exists(BOT_DATA_FILE):
        return {"message_to_entry": {}, "user_sessions": {}}

    try:
        with open(BOT_DATA_FILE, "r") as f:
            data = json.load(f)
        logger.info(f"Loaded {len(data.get('message_to_entry', {}))} message mappings from disk")
        return data
    except Exception as e:
        logger.warning(f"Failed to load bot_data: {e}")
        return {"message_to_entry": {}, "user_sessions": {}}


def save_bot_data(data):
    """Save bot_data to disk."""
    os.makedirs(DATA_DIR, exist_ok=True)
    try:
        # Keep only the last 1000 mappings to prevent file bloat
        msg_map = data.get("message_to_entry", {})
        if len(msg_map) > 1000:
            # Keep most recent 500
            sorted_keys = sorted(msg_map.keys(), key=lambda k: int(k) if k.isdigit() else 0, reverse=True)
            data["message_to_entry"] = {k: msg_map[k] for k in sorted_keys[:500]}

        with open(BOT_DATA_FILE, "w") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception as e:
        logger.warning(f"Failed to save bot_data: {e}")


def map_message_to_entry(bot_data, message_id, entry_id):
    """Store a message_id -> entry_id mapping."""
    if "message_to_entry" not in bot_data:
        bot_data["message_to_entry"] = {}
    bot_data["message_to_entry"][str(message_id)] = entry_id
    save_bot_data(bot_data)


def get_entry_for_message(bot_data, message_id):
    """Look up which entry a message belongs to."""
    return bot_data.get("message_to_entry", {}).get(str(message_id))


def update_user_session(bot_data, user_id, data):
    """Update session data for a user (last activity, current thread, etc)."""
    if "user_sessions" not in bot_data:
        bot_data["user_sessions"] = {}
    bot_data["user_sessions"][str(user_id)] = data
    save_bot_data(bot_data)

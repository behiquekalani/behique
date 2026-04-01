"""
ceiba_sync.py -- Sync BehiqueBot activity to Ceiba's memory system.

Writes a structured JSON file that Ceiba can read at session start
to see what Kalani sent between Claude Code sessions.
"""

import json
import logging
import os
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

SYNC_DIR = os.path.expanduser("~/behique/bridge")
SYNC_FILE = os.path.join(SYNC_DIR, "behiquebot_sync.json")


def sync_to_ceiba(entries, daily_summary=None):
    """
    Write bot activity to a file Ceiba can read.
    Called after every new entry or update.
    """
    try:
        os.makedirs(SYNC_DIR, exist_ok=True)

        # Load existing sync data
        existing = {}
        if os.path.exists(SYNC_FILE):
            try:
                with open(SYNC_FILE, "r") as f:
                    existing = json.load(f)
            except:
                existing = {}

        # Get recent entries (last 48 hours)
        cutoff = (datetime.now() - timedelta(hours=48)).isoformat()
        recent = [e for e in entries if e.get("timestamp", "") > cutoff]

        # Build sync payload
        sync_data = {
            "last_sync": datetime.now().isoformat(),
            "total_entries": len(entries),
            "recent_entries": len(recent),
            "entries": [{
                "id": e.get("id", ""),
                "seed": e.get("seed", "")[:200],
                "category": e.get("category", ""),
                "niche": e.get("niche", ""),
                "tags": e.get("tags", []),
                "timestamp": e.get("timestamp", ""),
                "source": e.get("source", "text"),
                "updates_count": len(e.get("updates", [])),
            } for e in recent],
            "categories": _count_by_field(recent, "category"),
            "pillars": _count_by_field(recent, "life_pillar"),
            "daily_summary": daily_summary or existing.get("daily_summary", ""),
            "unread_by_ceiba": existing.get("unread_by_ceiba", 0) + len(recent) - existing.get("recent_entries", 0),
        }

        with open(SYNC_FILE, "w") as f:
            json.dump(sync_data, f, ensure_ascii=False, indent=2)

        logger.info(f"Synced {len(recent)} recent entries to Ceiba")
        return True

    except Exception as e:
        logger.warning(f"Ceiba sync failed: {e}")
        return False


def mark_read_by_ceiba():
    """Called by Ceiba when it reads the sync file."""
    try:
        if not os.path.exists(SYNC_FILE):
            return
        with open(SYNC_FILE, "r") as f:
            data = json.load(f)
        data["unread_by_ceiba"] = 0
        data["last_read_by_ceiba"] = datetime.now().isoformat()
        with open(SYNC_FILE, "w") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception as e:
        logger.warning(f"Failed to mark read: {e}")


def _count_by_field(entries, field):
    """Count entries by a field value."""
    counts = {}
    for e in entries:
        val = e.get(field, "unknown")
        counts[val] = counts.get(val, 0) + 1
    return counts

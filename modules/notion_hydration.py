"""
notion_hydration.py -- Load entries from Notion on startup.

Survives Railway redeploys by treating Notion as source of truth.
Called once on bot startup to populate local entries.json.
"""

import json
import logging
import os
from datetime import datetime

logger = logging.getLogger(__name__)

NOTION_TOKEN = os.environ.get("NOTION_TOKEN", "")
NOTION_DATABASE_ID = os.environ.get("NOTION_DATABASE_ID", "")
DATA_DIR = "data"
ENTRIES_FILE = os.path.join(DATA_DIR, "entries.json")


def hydrate_from_notion():
    """
    Pull all entries from Notion database and write to local entries.json.
    Called on bot startup to restore state after Railway redeploy.
    """
    if not NOTION_TOKEN or not NOTION_DATABASE_ID:
        logger.warning("Notion credentials not set. Skipping hydration.")
        return []

    try:
        import httpx

        headers = {
            "Authorization": f"Bearer {NOTION_TOKEN}",
            "Notion-Version": "2022-06-28",
            "Content-Type": "application/json"
        }

        url = f"https://api.notion.com/v1/databases/{NOTION_DATABASE_ID}/query"
        entries = []
        has_more = True
        start_cursor = None

        while has_more:
            body = {"page_size": 100}
            if start_cursor:
                body["start_cursor"] = start_cursor

            response = httpx.post(url, headers=headers, json=body, timeout=30)

            if response.status_code != 200:
                logger.error(f"Notion API error: {response.status_code} {response.text[:200]}")
                break

            data = response.json()
            has_more = data.get("has_more", False)
            start_cursor = data.get("next_cursor")

            for page in data.get("results", []):
                entry = _parse_notion_page(page)
                if entry:
                    entries.append(entry)

        # Save to local file
        os.makedirs(DATA_DIR, exist_ok=True)

        # Merge with existing entries (don't overwrite local-only entries)
        existing = []
        if os.path.exists(ENTRIES_FILE):
            try:
                with open(ENTRIES_FILE, "r") as f:
                    existing = json.load(f)
            except:
                existing = []

        # Merge by ID
        existing_ids = {e.get("id") for e in existing}
        notion_ids = {e.get("id") for e in entries}

        # Keep local entries that aren't in Notion
        local_only = [e for e in existing if e.get("id") not in notion_ids]

        merged = entries + local_only

        with open(ENTRIES_FILE, "w") as f:
            json.dump(merged, f, ensure_ascii=False, indent=2)

        logger.info(f"Hydrated {len(entries)} entries from Notion, {len(local_only)} local-only, {len(merged)} total")
        return merged

    except ImportError:
        logger.error("httpx not installed. Run: pip install httpx")
        return []
    except Exception as e:
        logger.error(f"Hydration failed: {e}")
        return []


def _parse_notion_page(page):
    """Parse a Notion page into our entry format."""
    try:
        props = page.get("properties", {})

        # Extract text properties
        def get_title(prop):
            title = prop.get("title", [])
            return title[0]["plain_text"] if title else ""

        def get_rich_text(prop):
            rt = prop.get("rich_text", [])
            return rt[0]["plain_text"] if rt else ""

        def get_select(prop):
            sel = prop.get("select")
            return sel["name"] if sel else ""

        def get_multi_select(prop):
            ms = prop.get("multi_select", [])
            return [item["name"] for item in ms]

        entry = {
            "id": page["id"],
            "notion_page_id": page["id"],
            "seed": get_title(props.get("Seed", props.get("Name", {}))),
            "category": get_select(props.get("Category", {})),
            "niche": get_rich_text(props.get("Niche", {})),
            "life_pillar": get_select(props.get("Life Pillar", {})),
            "tags": get_multi_select(props.get("Tags", {})),
            "source": get_rich_text(props.get("Source", {})) or "notion",
            "timestamp": page.get("created_time", datetime.now().isoformat()),
            "updates": [],
            "classification": {
                "category": get_select(props.get("Category", {})),
                "niche": get_rich_text(props.get("Niche", {})),
                "life_pillar": get_select(props.get("Life Pillar", {})),
                "summary": get_rich_text(props.get("Summary", {})),
                "tags": get_multi_select(props.get("Tags", {})),
            }
        }

        # Get updates from page blocks (children)
        # Note: this would need a separate API call per page
        # For now, we just get the properties

        return entry if entry["seed"] else None

    except Exception as e:
        logger.warning(f"Failed to parse Notion page {page.get('id', '?')}: {e}")
        return None

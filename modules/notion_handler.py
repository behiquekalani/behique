"""
notion_handler.py — Saves BehiqueBot entries to Notion as persistent cloud storage.
Railway resets wipe local JSON. Notion doesn't. This fixes that.
"""

import os
import requests
from datetime import datetime

NOTION_SECRET = os.getenv("NOTION_SECRET")
NOTION_DATABASE_ID = os.getenv("NOTION_DATABASE_ID")
NOTION_VERSION = "2022-06-28"

HEADERS = {
    "Authorization": f"Bearer {NOTION_SECRET}",
    "Content-Type": "application/json",
    "Notion-Version": NOTION_VERSION
}


def _category_color(category: str) -> str:
    colors = {
        "CREATIVE": "purple",
        "BUSINESS": "green",
        "KNOWLEDGE": "blue",
        "PERSONAL": "pink",
        "TECHNICAL": "orange"
    }
    return colors.get(category, "default")


def _pillar_color(pillar: str) -> str:
    colors = {
        "health": "red",
        "wealth": "yellow",
        "relationships": "pink",
        "general": "gray"
    }
    return colors.get(pillar, "default")


def save_to_notion(entry: dict) -> str | None:
    """
    Creates a new page in the BehiqueBot Ideas database.
    Returns the Notion page ID on success, None on failure.
    """
    if not NOTION_SECRET or not NOTION_DATABASE_ID:
        return None

    classification = entry.get("classification", {})
    summary = classification.get("summary", entry.get("seed", "")[:100])
    tags = classification.get("tags", [])
    created = entry.get("timestamp", datetime.now().isoformat())

    # Build tag string for name
    tag_str = " · ".join(tags[:3]) if tags else ""
    title = f"{summary}"

    payload = {
        "parent": {"database_id": NOTION_DATABASE_ID},
        "properties": {
            "Name": {
                "title": [{"text": {"content": title}}]
            },
            "Category": {
                "select": {
                    "name": entry.get("category", "PERSONAL"),
                    "color": _category_color(entry.get("category", "PERSONAL"))
                }
            },
            "Pillar": {
                "select": {
                    "name": entry.get("life_pillar", "general"),
                    "color": _pillar_color(entry.get("life_pillar", "general"))
                }
            },
            "Status": {
                "select": {"name": "new"}
            },
            "Raw Text": {
                "rich_text": [{"text": {"content": entry.get("seed", "")[:2000]}}]
            },
            "Source": {
                "rich_text": [{"text": {"content": entry.get("source", "text")}}]
            },
            "Created": {
                "date": {"start": created[:19] + "Z" if "T" in created else created}
            }
        },
        "children": [
            {
                "object": "block",
                "type": "paragraph",
                "paragraph": {
                    "rich_text": [{"text": {"content": f"🌱 Original: {entry.get('seed', '')}"}}]
                }
            },
            {
                "object": "block",
                "type": "paragraph",
                "paragraph": {
                    "rich_text": [{"text": {"content": f"🏷️ Tags: {', '.join(tags)}" if tags else "🏷️ Tags: none"}}]
                }
            },
            {
                "object": "block",
                "type": "paragraph",
                "paragraph": {
                    "rich_text": [{"text": {"content": f"🆔 Entry ID: {entry.get('id', '')}"}}]
                }
            }
        ]
    }

    try:
        response = requests.post(
            "https://api.notion.com/v1/pages",
            headers=HEADERS,
            json=payload,
            timeout=10
        )
        if response.status_code == 200:
            return response.json().get("id")
        else:
            print(f"[Notion] Save failed: {response.status_code} {response.text[:200]}")
            return None
    except Exception as e:
        print(f"[Notion] Error: {e}")
        return None


def update_in_notion(notion_page_id: str, new_text: str, update_number: int) -> bool:
    """
    Appends an update block to an existing Notion page.
    """
    if not NOTION_SECRET or not notion_page_id:
        return False

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")

    payload = {
        "children": [
            {
                "object": "block",
                "type": "paragraph",
                "paragraph": {
                    "rich_text": [
                        {
                            "text": {
                                "content": f"🔄 Update #{update_number} [{timestamp}]: {new_text}"
                            }
                        }
                    ]
                }
            }
        ]
    }

    try:
        response = requests.patch(
            f"https://api.notion.com/v1/blocks/{notion_page_id}/children",
            headers=HEADERS,
            json=payload,
            timeout=10
        )
        return response.status_code == 200
    except Exception as e:
        print(f"[Notion] Update error: {e}")
        return False

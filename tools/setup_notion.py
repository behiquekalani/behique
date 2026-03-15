#!/usr/bin/env python3
"""Creates the BehiqueBot Ideas database in Notion and outputs the database ID."""

import urllib.request
import urllib.error
import json
import os
import ssl

try:
    import certifi
    has_certifi = True
except ImportError:
    has_certifi = False

NOTION_SECRET = "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"

def notion_request(method, endpoint, data=None):
    url = f"https://api.notion.com/v1/{endpoint}"
    headers = {
        "Authorization": f"Bearer {NOTION_SECRET}",
        "Content-Type": "application/json",
        "Notion-Version": "2022-06-28"
    }
    body = json.dumps(data).encode() if data else None
    req = urllib.request.Request(url, data=body, headers=headers, method=method)
    
    # Create SSL context — fall back to unverified on macOS cert issues
    if has_certifi:
        context = ssl.create_default_context(cafile=certifi.where())
    else:
        context = ssl._create_unverified_context()

    try:
        with urllib.request.urlopen(req, context=context) as response:
            return json.loads(response.read())
    except urllib.error.HTTPError as e:
        print(f"Error {e.code}: {e.read().decode()}")
        return None

# Step 1: Search for a parent page to attach the database to
print("Searching for pages in your Notion workspace...")
result = notion_request("POST", "search", {"filter": {"value": "page", "property": "object"}})

if not result or not result.get("results"):
    print("No pages found. Create a page in Notion first, then run this again.")
    exit(1)

pages = result["results"]
print(f"\nFound {len(pages)} pages. Using first available as parent:")
parent = pages[0]
parent_id = parent["id"]
parent_title = parent.get("properties", {}).get("title", {}).get("title", [{}])
parent_name = parent_title[0].get("text", {}).get("content", "Untitled") if parent_title else "Untitled"
print(f"  → {parent_name} ({parent_id})")

# Step 2: Create the BehiqueBot Ideas database
print("\nCreating BehiqueBot Ideas database...")
db = notion_request("POST", "databases", {
    "parent": {"type": "page_id", "page_id": parent_id},
    "title": [{"type": "text", "text": {"content": "BehiqueBot Ideas"}}],
    "properties": {
        "Name": {"title": {}},
        "Category": {
            "select": {
                "options": [
                    {"name": "CREATIVE", "color": "purple"},
                    {"name": "BUSINESS", "color": "green"},
                    {"name": "KNOWLEDGE", "color": "blue"},
                    {"name": "PERSONAL", "color": "pink"},
                    {"name": "TECHNICAL", "color": "orange"}
                ]
            }
        },
        "Pillar": {
            "select": {
                "options": [
                    {"name": "health", "color": "red"},
                    {"name": "wealth", "color": "yellow"},
                    {"name": "relationships", "color": "pink"},
                    {"name": "general", "color": "gray"}
                ]
            }
        },
        "Status": {
            "select": {
                "options": [
                    {"name": "new", "color": "blue"},
                    {"name": "processed", "color": "green"},
                    {"name": "archived", "color": "gray"}
                ]
            }
        },
        "Raw Text": {"rich_text": {}},
        "Source": {"rich_text": {}},
        "Created": {"date": {}}
    }
})

if not db:
    print("Failed to create database.")
    exit(1)

db_id = db["id"].replace("-", "")
print(f"\n✓ Database created successfully!")
print(f"\nDATABASE ID: {db_id}")
print(f"\nAdd this to your Railway environment variables:")
print(f"NOTION_DATABASE_ID={db_id}")

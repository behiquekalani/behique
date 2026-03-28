#!/usr/bin/env python3
"""
Set up BehiqueBot command menu in Telegram.
Run once after adding new commands.

Usage: python3 tools/setup_telegram_commands.py
Requires: TELEGRAM_BOT_TOKEN env variable set (or edit BOT_TOKEN below)
"""

import os
import requests

BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "YOUR_BOT_TOKEN_HERE")

commands = [
    {"command": "brief", "description": "Morning briefing -- current project, next actions, blockers"},
    {"command": "build", "description": "Look up a product by name"},
    {"command": "todo", "description": "Show top 3 tasks for today"},
    {"command": "revenue", "description": "Revenue check (Gumroad link)"},
    {"command": "idea", "description": "Capture an idea immediately"},
    {"command": "products", "description": "List all 25+ products with prices"},
    {"command": "status", "description": "System status -- products, pages, content counts"},
    {"command": "audit", "description": "Run sprint audit -- security/PII/bug check"},
    {"command": "help", "description": "Show all commands"},
]

# Register commands via Telegram Bot API
url = f"https://api.telegram.org/bot{BOT_TOKEN}/setMyCommands"
response = requests.post(url, json={"commands": commands})
print("Response:", response.json())
if response.json().get("ok"):
    print("Commands registered successfully.")
else:
    print("Error registering commands.")

#!/usr/bin/env python3
"""
ceiba_lite.py — Ceiba Offline Mode
Runs on Ollama (qwen2.5:7b) when Claude Max is rate limited.
Not as powerful as full Ceiba, but keeps you moving.

Usage: python3 ~/behique/ceiba_lite.py
"""

import os
import sys
import json
import urllib.request
import urllib.error
from datetime import datetime

OLLAMA_URL = "http://127.0.0.1:11434/api/generate"
MODEL = "qwen2.5:7b"
BEHIQUE_PATH = os.path.expanduser("~/behique")

BANNER = """
╔══════════════════════════════════════════════╗
║         CEIBA LITE — OFFLINE MODE            ║
║   Running on Ollama · qwen2.5:7b · Local     ║
║   Full Ceiba unavailable (Claude Max limit)  ║
║   Type 'quit' to exit · 'status' for update  ║
╚══════════════════════════════════════════════╝
"""

def read_file(path):
    try:
        with open(path, "r") as f:
            return f.read()
    except:
        return ""

def build_context():
    """Load memory stack so Ceiba Lite knows who Kalani is."""
    primer = read_file(os.path.join(BEHIQUE_PATH, "primer.md"))
    claude_md = read_file(os.path.join(BEHIQUE_PATH, "CLAUDE.md"))
    missions = read_file(os.path.join(BEHIQUE_PATH, "Ceiba/01-Projects/MISSIONS.md"))

    context = f"""You are Ceiba Lite — a simplified version of Kalani's AI assistant, running locally on Ollama when Claude Max is rate limited.

You know everything about Kalani from his memory stack. Be direct, honest, and helpful. Keep responses short unless depth is needed. You're not as powerful as full Ceiba, but you can keep him moving.

MEMORY STACK:
--- PRIMER (current state) ---
{primer[:2000]}

--- CLAUDE.md (identity + projects) ---
{claude_md[:2000]}

--- MISSIONS ---
{missions[:1500]}

RULES:
- Be direct. No fluff.
- If you don't know something, say so.
- Keep him focused on revenue-generating tasks.
- Reference his actual projects, not generic advice.
- You're a fallback, not a replacement. Tell him when he needs full Ceiba for complex tasks.
"""
    return context


def ask_ollama(system_context, conversation_history, user_message):
    """Send a message to Ollama and get a response."""
    # Build the full prompt with conversation history
    history_text = ""
    for msg in conversation_history[-6:]:  # Last 3 exchanges
        role = "Kalani" if msg["role"] == "user" else "Ceiba"
        history_text += f"{role}: {msg['content']}\n"

    full_prompt = f"{system_context}\n\nCONVERSATION:\n{history_text}Kalani: {user_message}\nCeiba:"

    payload = {
        "model": MODEL,
        "prompt": full_prompt,
        "stream": False,
        "options": {
            "temperature": 0.7,
            "num_predict": 500
        }
    }

    try:
        data = json.dumps(payload).encode()
        req = urllib.request.Request(OLLAMA_URL, data=data,
                                      headers={"Content-Type": "application/json"},
                                      method="POST")
        with urllib.request.urlopen(req, timeout=60) as response:
            result = json.loads(response.read())
            return result.get("response", "").strip()
    except Exception as e:
        return f"[Error reaching Ollama: {e}. Is Ollama running? Check menu bar.]"


def show_status():
    """Quick project status from primer.md"""
    primer = read_file(os.path.join(BEHIQUE_PATH, "primer.md"))
    print("\n" + "="*50)
    print("CURRENT STATUS (from primer.md):")
    print("="*50)
    # Print first 800 chars of primer
    print(primer[:800])
    print("="*50 + "\n")


def main():
    print(BANNER)
    print(f"Loading your memory stack from {BEHIQUE_PATH}...")

    system_context = build_context()
    conversation_history = []

    print("✓ Memory loaded. Ceiba Lite is ready.\n")
    print("Full Ceiba is temporarily unavailable due to Claude Max rate limits.")
    print("I have your full context loaded. Let's keep moving.\n")

    # Show current focus
    print("Current date:", datetime.now().strftime("%A, %B %d %Y — %H:%M"))
    print("\nType your message. Commands: 'status', 'quit'\n")

    while True:
        try:
            user_input = input("You: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nCeiba Lite shutting down. Come back when you're ready.")
            break

        if not user_input:
            continue

        if user_input.lower() == "quit":
            print("Ceiba Lite off. See you when full Ceiba is back.")
            break

        if user_input.lower() == "status":
            show_status()
            continue

        print("\nCeiba: ", end="", flush=True)
        response = ask_ollama(system_context, conversation_history, user_input)
        print(response)
        print()

        conversation_history.append({"role": "user", "content": user_input})
        conversation_history.append({"role": "assistant", "content": response})


if __name__ == "__main__":
    main()

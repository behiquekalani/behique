#!/usr/bin/env python3
"""
ceiba_bridge.py — Talk to Cobo's secure bridge from Ceiba CLI.

Usage:
    ceiba bridge status              # Check bridge + Ollama + n8n
    ceiba bridge ask "question"      # Ask Ollama on Cobo (free)
    ceiba bridge claude "prompt"     # Route through Cobo's Anthropic key
    ceiba bridge exec "command"      # Run allowlisted command on Cobo
    ceiba bridge models              # List Ollama models on Cobo
"""

import argparse
import json
import os
import sys
import urllib.request
import urllib.error
from pathlib import Path

COBO_IP = os.getenv("COBO_IP", "192.168.0.151")
BRIDGE_PORT = os.getenv("BRIDGE_PORT", "9876")
BRIDGE_URL = f"http://{COBO_IP}:{BRIDGE_PORT}"
OLLAMA_URL = f"http://{COBO_IP}:11434"

# Token from env or file
BRIDGE_TOKEN = os.getenv("BRIDGE_AUTH_TOKEN", "")
if not BRIDGE_TOKEN:
    token_file = Path.home() / ".behique_bridge_token"
    if token_file.exists():
        BRIDGE_TOKEN = token_file.read_text().strip()


def bridge_request(path: str, method: str = "GET", data: dict | None = None, timeout: int = 30) -> dict:
    """Make authenticated request to Cobo bridge."""
    url = f"{BRIDGE_URL}{path}"
    body = json.dumps(data).encode() if data else None
    req = urllib.request.Request(url, data=body, method=method)
    req.add_header("Authorization", f"Bearer {BRIDGE_TOKEN}")
    if body:
        req.add_header("Content-Type", "application/json")

    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        error_body = e.read().decode() if e.fp else ""
        try:
            return {"error": json.loads(error_body)}
        except Exception:
            return {"error": error_body, "status": e.code}
    except urllib.error.URLError as e:
        return {"error": f"Connection failed: {e.reason}"}
    except Exception as e:
        return {"error": str(e)}


def ollama_request(path: str, data: dict | None = None, timeout: int = 60) -> dict:
    """Direct request to Ollama on Cobo (no auth needed)."""
    url = f"{OLLAMA_URL}{path}"
    body = json.dumps(data).encode() if data else None
    req = urllib.request.Request(url, data=body)
    if body:
        req.add_header("Content-Type", "application/json")

    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return json.loads(resp.read().decode())
    except Exception as e:
        return {"error": str(e)}


def cmd_status():
    """Check all Cobo services."""
    print(f"── Cobo Bridge Status ({COBO_IP}) ──\n")

    # Ping bridge
    result = bridge_request("/")
    if "error" in result:
        print(f"  ❌ Bridge: {result['error']}")
    else:
        print(f"  ✅ Bridge: {result.get('status', 'active')}")
        print(f"     Exec: {'enabled' if result.get('execEnabled') else 'disabled'}")
        print(f"     Anthropic: {'configured' if result.get('anthropicConfigured') else 'not set'}")

    # Check Ollama
    models = ollama_request("/api/tags")
    if "error" in models:
        print(f"  ❌ Ollama: {models['error']}")
    else:
        names = [m["name"] for m in models.get("models", [])]
        print(f"  ✅ Ollama: {len(names)} models — {', '.join(names[:5])}")

    # Check n8n
    try:
        req = urllib.request.Request(f"http://{COBO_IP}:5678")
        with urllib.request.urlopen(req, timeout=3) as resp:
            print(f"  ✅ n8n: responding (HTTP {resp.status})")
    except Exception:
        print(f"  ⚠️  n8n: not responding")

    print()


def cmd_ask(prompt: str, model: str = "llama3.2"):
    """Ask Ollama on Cobo (free, local)."""
    print(f"[Cobo/Ollama] Asking {model}...")
    result = ollama_request("/api/generate", {
        "model": model,
        "prompt": prompt,
        "stream": False
    }, timeout=120)

    if "error" in result:
        print(f"❌ {result['error']}")
    else:
        print(result.get("response", "(no response)"))


def cmd_claude(prompt: str, model: str = None):
    """Route through Cobo's Anthropic API key."""
    print("[Cobo/Claude] Sending...")
    result = bridge_request("/claude", "POST", {
        "messages": [{"role": "user", "content": prompt}],
        "model": model,
        "max_tokens": 2048
    }, timeout=60)

    if "error" in result:
        print(f"❌ {result.get('error', result)}")
    else:
        # Extract text from Anthropic response
        content = result.get("content", [])
        for block in content:
            if block.get("type") == "text":
                print(block["text"])


def cmd_exec(command: str, args: list = None):
    """Run allowlisted command on Cobo."""
    result = bridge_request("/exec", "POST", {
        "command": command,
        "args": args or []
    })

    if "error" in result:
        print(f"❌ {result.get('error', result)}")
        if "details" in result:
            print(f"   {result['details']}")
    else:
        print(result.get("stdout", ""))


def cmd_models():
    """List Ollama models on Cobo."""
    result = ollama_request("/api/tags")
    if "error" in result:
        print(f"❌ {result['error']}")
        return

    models = result.get("models", [])
    if not models:
        print("No models installed on Cobo.")
        return

    print(f"── Ollama Models on Cobo ({len(models)}) ──\n")
    for m in models:
        size_gb = m.get("size", 0) / (1024**3)
        print(f"  • {m['name']} ({size_gb:.1f} GB)")


def main():
    parser = argparse.ArgumentParser(description="Ceiba Bridge — Talk to Cobo")
    sub = parser.add_subparsers(dest="command")

    sub.add_parser("status", help="Check Cobo services")
    sub.add_parser("models", help="List Ollama models")

    ask_p = sub.add_parser("ask", help="Ask Ollama (free)")
    ask_p.add_argument("prompt", nargs="+")
    ask_p.add_argument("--model", default="llama3.2")

    claude_p = sub.add_parser("claude", help="Route through Cobo's Anthropic key")
    claude_p.add_argument("prompt", nargs="+")
    claude_p.add_argument("--model", default=None)

    exec_p = sub.add_parser("exec", help="Run allowlisted command")
    exec_p.add_argument("cmd_name")
    exec_p.add_argument("args", nargs="*")

    args = parser.parse_args()

    if args.command == "status" or not args.command:
        cmd_status()
    elif args.command == "models":
        cmd_models()
    elif args.command == "ask":
        cmd_ask(" ".join(args.prompt), args.model)
    elif args.command == "claude":
        cmd_claude(" ".join(args.prompt), args.model)
    elif args.command == "exec":
        cmd_exec(args.cmd_name, args.args)


if __name__ == "__main__":
    main()

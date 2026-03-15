#!/usr/bin/env python3
"""
routing.py — The Spine's Routing Layer
Evaluates a task and routes it to the right model.

80% Ollama (free) · 15% Sonnet · 5% Opus

Usage:
    from routing import route, complete

    # Get the right model for a task
    result = route("rewrite primer.md LIVE STATE block")
    # result.model = "ollama", result.reason = "vault housekeeping"

    # Or run the task end-to-end
    response = complete("classify this message: 'new product idea for eBay'")
"""

import os
import json
import urllib.request
import urllib.error
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional


# --- Configuration ---

OLLAMA_URL = os.environ.get("OLLAMA_URL", "http://192.168.0.151:11434")
OLLAMA_MODEL = os.environ.get("OLLAMA_MODEL", "llama3.2")

# Anthropic is called via API only when explicitly needed.
# Claude Code / Cursor handle their own Claude calls — routing.py
# is for the autonomous parts of the system (BehiqueBot, n8n jobs,
# overnight pipelines) that need to pick a model themselves.
ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")


class Tier(Enum):
    """Model tiers, cheapest first."""
    OLLAMA = "ollama"
    SONNET = "sonnet"
    OPUS = "opus"


@dataclass
class RouteResult:
    tier: Tier
    model: str
    reason: str
    task: str


# --- Routing rules ---
# Each rule is (keywords, tier, reason). First match wins.
# Order matters: put specific patterns before broad ones.

RULES: list[tuple[list[str], Tier, str]] = [
    # Vault housekeeping → Ollama (free)
    (["primer.md", "rewrite primer", "update primer"], Tier.OLLAMA, "vault housekeeping"),
    (["vault_index", "update vault", "update index"], Tier.OLLAMA, "vault housekeeping"),
    (["breadcrumb", "update breadcrumb"], Tier.OLLAMA, "vault housekeeping"),
    (["session checkpoint", "auto checkpoint"], Tier.OLLAMA, "session checkpoint"),
    (["wiki link", "add links", "link parser"], Tier.OLLAMA, "wiki link maintenance"),

    # Classification → Ollama
    (["classify", "categorize", "tag", "label"], Tier.OLLAMA, "classification"),
    (["which category", "what pillar", "life pillar"], Tier.OLLAMA, "classification"),

    # Summarization of short content → Ollama
    (["summarize", "summary", "tldr", "recap"], Tier.OLLAMA, "summarization"),
    (["commit message", "changelog"], Tier.OLLAMA, "summarization"),

    # Simple extraction / formatting → Ollama
    (["extract", "parse", "format", "reformat"], Tier.OLLAMA, "extraction"),
    (["json", "csv", "markdown table"], Tier.OLLAMA, "formatting"),

    # Code generation → Sonnet
    (["write code", "implement", "build", "create function", "debug"], Tier.SONNET, "code generation"),
    (["refactor", "fix bug", "add feature", "test"], Tier.SONNET, "code generation"),
    (["python", "javascript", "typescript", "react"], Tier.SONNET, "code generation"),

    # Architecture / strategy → Sonnet
    (["architect", "design", "plan", "strategy", "tradeoff"], Tier.SONNET, "architecture"),
    (["should we", "best approach", "how to structure"], Tier.SONNET, "architecture"),
    (["compare", "evaluate", "pros and cons"], Tier.SONNET, "analysis"),

    # Research → Sonnet
    (["research", "find out", "investigate", "look into"], Tier.SONNET, "research"),
    (["market", "competitor", "pricing", "opportunity"], Tier.SONNET, "research"),

    # Deep creative / high-stakes → Opus (rare)
    (["rebrand", "vision", "north star", "manifesto"], Tier.OPUS, "deep creative"),
    (["investor", "pitch deck", "fundraise"], Tier.OPUS, "high-stakes"),
]


def route(task: str) -> RouteResult:
    """Score a task and return the recommended model tier."""
    task_lower = task.lower()

    for keywords, tier, reason in RULES:
        if any(kw in task_lower for kw in keywords):
            model = _model_for_tier(tier)
            return RouteResult(tier=tier, model=model, reason=reason, task=task)

    # Default: if we can't classify it, use Ollama.
    # Worst case it's slow or weak and the caller retries on Sonnet.
    return RouteResult(
        tier=Tier.OLLAMA,
        model=_model_for_tier(Tier.OLLAMA),
        reason="default (unmatched — saving credits)",
        task=task,
    )


def _model_for_tier(tier: Tier) -> str:
    if tier == Tier.OLLAMA:
        return OLLAMA_MODEL
    elif tier == Tier.SONNET:
        return "claude-sonnet-4-6"
    elif tier == Tier.OPUS:
        return "claude-opus-4-6"
    return OLLAMA_MODEL


# --- Execution ---

def complete(task: str, system: str = "", fallback: bool = True) -> str:
    """Route a task to the right model and return the response.

    Args:
        task: The prompt / instruction to complete.
        system: Optional system prompt.
        fallback: If True, fall back to next tier on failure.

    Returns:
        The model's response text.
    """
    result = route(task)
    response = _call(result.tier, task, system)

    if response is None and fallback:
        # Ollama failed → try Sonnet
        if result.tier == Tier.OLLAMA and ANTHROPIC_API_KEY:
            response = _call(Tier.SONNET, task, system)
        # Sonnet failed → try Ollama (maybe API is down, local still works)
        elif result.tier == Tier.SONNET:
            response = _call(Tier.OLLAMA, task, system)

    return response or "[routing error: all models failed]"


def _call(tier: Tier, prompt: str, system: str = "") -> Optional[str]:
    if tier == Tier.OLLAMA:
        return _call_ollama(prompt, system)
    elif tier in (Tier.SONNET, Tier.OPUS):
        return _call_anthropic(tier, prompt, system)
    return None


def _call_ollama(prompt: str, system: str = "") -> Optional[str]:
    payload = {
        "model": OLLAMA_MODEL,
        "prompt": prompt,
        "system": system,
        "stream": False,
        "options": {"temperature": 0.3, "num_predict": 1000},
    }
    try:
        data = json.dumps(payload).encode()
        req = urllib.request.Request(
            f"{OLLAMA_URL}/api/generate",
            data=data,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=120) as resp:
            result = json.loads(resp.read())
            return result.get("response", "").strip() or None
    except Exception:
        return None


def _call_anthropic(tier: Tier, prompt: str, system: str = "") -> Optional[str]:
    if not ANTHROPIC_API_KEY:
        return None

    model = _model_for_tier(tier)
    messages = [{"role": "user", "content": prompt}]
    payload = {
        "model": model,
        "max_tokens": 2000,
        "messages": messages,
    }
    if system:
        payload["system"] = system

    try:
        data = json.dumps(payload).encode()
        req = urllib.request.Request(
            "https://api.anthropic.com/v1/messages",
            data=data,
            headers={
                "Content-Type": "application/json",
                "x-api-key": ANTHROPIC_API_KEY,
                "anthropic-version": "2023-06-01",
            },
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=120) as resp:
            result = json.loads(resp.read())
            content = result.get("content", [])
            if content and content[0].get("type") == "text":
                return content[0]["text"].strip()
    except Exception:
        return None
    return None


# --- CLI for testing ---

if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: python3 routing.py 'describe your task here'")
        print("\nExamples:")
        print("  python3 routing.py 'classify this message as business or personal'")
        print("  python3 routing.py 'write a Python function to parse eBay listings'")
        print("  python3 routing.py 'rewrite primer.md LIVE STATE block'")
        print("  python3 routing.py 'design the n8n webhook architecture'")
        sys.exit(0)

    task = " ".join(sys.argv[1:])
    result = route(task)

    print(f"Task:   {result.task}")
    print(f"Tier:   {result.tier.value}")
    print(f"Model:  {result.model}")
    print(f"Reason: {result.reason}")

    if "--run" in sys.argv:
        sys.argv.remove("--run")
        task = " ".join(a for a in sys.argv[1:] if a != "--run")
        print(f"\nRunning on {result.model}...")
        response = complete(task)
        print(f"\nResponse:\n{response}")

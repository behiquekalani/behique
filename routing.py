#!/usr/bin/env python3
"""
routing.py — The Spine's Routing Layer
Evaluates a task and routes it to the right model.

Best tool for the job: Ollama · ChatGPT · Sonnet · Opus

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
import logging
import ssl
import urllib.request
import urllib.error
from dataclasses import dataclass
from enum import Enum
from typing import Optional

# Python 3.14 on macOS needs explicit cert handling
try:
    import certifi
    _SSL_CTX = ssl.create_default_context(cafile=certifi.where())
except ImportError:
    _SSL_CTX = ssl.create_default_context()

log = logging.getLogger("routing")
if not log.handlers:
    _h = logging.StreamHandler()
    _h.setFormatter(logging.Formatter("[routing] %(levelname)s: %(message)s"))
    log.addHandler(_h)
    log.setLevel(os.environ.get("ROUTING_LOG_LEVEL", "WARNING").upper())


# --- Configuration ---

OLLAMA_URL = os.environ.get("OLLAMA_URL", "http://192.168.0.151:11434")
OLLAMA_MODEL = os.environ.get("OLLAMA_MODEL", "llama3.2")

# API keys — routing.py is for the autonomous parts of the system
# (BehiqueBot, n8n jobs, overnight pipelines) that pick their own model.
ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "")


class Tier(Enum):
    """Model tiers — best tool for the job, not cheapest."""
    OLLAMA = "ollama"       # Classification, tagging, simple extraction — not because cheap, because sufficient
    CHATGPT = "chatgpt"     # Prompt drafting for Claude — cross-model prompting beats self-prompting
    SONNET = "sonnet"       # Code gen, architecture, deep reasoning
    OPUS = "opus"           # Rare, high-stakes creative/strategic


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
    # Prompt engineering → ChatGPT FIRST (most specific, cross-model > self-prompting)
    (["write a prompt", "draft prompt", "system prompt", "prompt for claude"], Tier.CHATGPT, "prompt drafting — ChatGPT writes better Claude prompts"),
    (["improve this prompt", "optimize prompt", "prompt engineering"], Tier.CHATGPT, "prompt optimization"),

    # Vault housekeeping → Ollama
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
    (["extract text", "extract data", "parse json", "parse csv", "reformat"], Tier.OLLAMA, "extraction"),
    (["to json", "to csv", "to markdown table", "convert format"], Tier.OLLAMA, "formatting"),

    # Code generation → Sonnet
    (["write code", "implement", "build", "create function", "debug"], Tier.SONNET, "code generation"),
    (["refactor", "fix bug", "add feature", "write test", "run test"], Tier.SONNET, "code generation"),
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
            log.info("routed to %s (%s) — matched '%s'", tier.value, reason, task[:80])
            return RouteResult(tier=tier, model=model, reason=reason, task=task)

    log.info("no rule matched — defaulting to ollama for: %s", task[:80])
    return RouteResult(
        tier=Tier.OLLAMA,
        model=_model_for_tier(Tier.OLLAMA),
        reason="default (unmatched — saving credits)",
        task=task,
    )


def _model_for_tier(tier: Tier) -> str:
    if tier == Tier.OLLAMA:
        return OLLAMA_MODEL
    elif tier == Tier.CHATGPT:
        return "gpt-4o"
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
        # ChatGPT failed → try Sonnet (both are cloud APIs, different providers)
        elif result.tier == Tier.CHATGPT and ANTHROPIC_API_KEY:
            response = _call(Tier.SONNET, task, system)
        # Sonnet/Opus failed → try Ollama (API down, local still works)
        elif result.tier in (Tier.SONNET, Tier.OPUS):
            response = _call(Tier.OLLAMA, task, system)

    return response or "[routing error: all models failed]"


def _call(tier: Tier, prompt: str, system: str = "") -> Optional[str]:
    if tier == Tier.OLLAMA:
        return _call_ollama(prompt, system)
    elif tier == Tier.CHATGPT:
        return _call_openai(prompt, system)
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
    except Exception as e:
        log.warning("ollama call failed: %s", e)
        return None


def _call_openai(prompt: str, system: str = "") -> Optional[str]:
    if not OPENAI_API_KEY:
        return None

    messages = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": prompt})

    payload = {
        "model": "gpt-4o",
        "messages": messages,
        "max_tokens": 2000,
        "temperature": 0.7,
    }
    try:
        data = json.dumps(payload).encode()
        req = urllib.request.Request(
            "https://api.openai.com/v1/chat/completions",
            data=data,
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {OPENAI_API_KEY}",
            },
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=120, context=_SSL_CTX) as resp:
            result = json.loads(resp.read())
            choices = result.get("choices", [])
            if choices:
                return choices[0]["message"]["content"].strip()
    except Exception as e:
        log.warning("openai call failed: %s", e)
        return None
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
        with urllib.request.urlopen(req, timeout=120, context=_SSL_CTX) as resp:
            result = json.loads(resp.read())
            content = result.get("content", [])
            if content and content[0].get("type") == "text":
                return content[0]["text"].strip()
    except Exception as e:
        log.warning("anthropic call failed: %s", e)
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

    run_mode = "--run" in sys.argv
    task = " ".join(a for a in sys.argv[1:] if a != "--run")
    result = route(task)

    print(f"Task:   {result.task}")
    print(f"Tier:   {result.tier.value}")
    print(f"Model:  {result.model}")
    print(f"Reason: {result.reason}")

    if run_mode:
        log.setLevel(logging.INFO)
        print(f"\nRunning on {result.model}...")
        response = complete(task)
        print(f"\nResponse:\n{response}")

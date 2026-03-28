#!/usr/bin/env python3
"""
Boardroom Mode -- Multi-specialist agent review system.

Spawns specialist "advisors" (marketing, finance, legal, operations, content)
that each review a question/document/decision from their perspective.
Uses local Ollama for $0 cost. Falls back gracefully.

Usage:
    python3 boardroom.py "Should we price the AI Employee Guide at $19.99 or $29.99?"
    python3 boardroom.py --file product-listing.md "Review this listing"
    python3 boardroom.py --specialists marketing,finance "Is this pricing right?"
    python3 boardroom.py --all "Review our content strategy"

Specialists:
    marketing  -- audience, positioning, messaging, growth
    finance    -- pricing, margins, ROI, cash flow
    legal      -- compliance, risk, terms, IP
    operations -- logistics, tools, automation, scalability
    content    -- copy quality, hooks, engagement, storytelling
    strategy   -- competitive advantage, market fit, long-term vision
"""
import json
import sys
import os
import urllib.request
import urllib.error
import argparse
import time
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed

# Ollama endpoints (Ceiba local, then Cobo)
OLLAMA_URLS = [
    "http://localhost:11434",
    "http://192.168.0.151:11434",
]

DEFAULT_MODEL = "qwen2.5:7b"

SPECIALISTS = {
    "marketing": {
        "emoji": "\U0001f4e3",
        "title": "Marketing Advisor",
        "system": (
            "You are a sharp marketing strategist. You think about target audience, "
            "positioning, messaging, content hooks, growth channels, and competitive "
            "differentiation. You speak in clear, actionable terms. Be direct and specific. "
            "Give concrete recommendations, not vague advice. Keep it under 200 words."
        ),
    },
    "finance": {
        "emoji": "\U0001f4b0",
        "title": "Finance Advisor",
        "system": (
            "You are a financial analyst focused on small business and solo creators. "
            "You think about pricing strategy, profit margins, unit economics, cash flow, "
            "and ROI. You ground everything in numbers. Be direct. If you need assumptions, "
            "state them clearly. Keep it under 200 words."
        ),
    },
    "legal": {
        "emoji": "\u2696\ufe0f",
        "title": "Legal Advisor",
        "system": (
            "You are a legal advisor for digital businesses and content creators. "
            "You think about terms of service, intellectual property, content licensing, "
            "compliance (DMCA, GDPR, FTC disclosure), and risk mitigation. Flag real risks, "
            "not hypothetical ones. Be practical, not paranoid. Keep it under 200 words."
        ),
    },
    "operations": {
        "emoji": "\u2699\ufe0f",
        "title": "Operations Advisor",
        "system": (
            "You are an operations specialist for lean startups and solo founders. "
            "You think about workflow efficiency, tool selection, automation opportunities, "
            "scalability bottlenecks, and time management. You hate waste and love systems. "
            "Be specific about tools and processes. Keep it under 200 words."
        ),
    },
    "content": {
        "emoji": "\u270d\ufe0f",
        "title": "Content Advisor",
        "system": (
            "You are a content strategist and copywriter. You think about hooks, "
            "storytelling, engagement, platform-specific optimization (Instagram, TikTok, "
            "YouTube), content calendars, and audience retention. You know what makes people "
            "stop scrolling. Be specific and give examples. Keep it under 200 words."
        ),
    },
    "strategy": {
        "emoji": "\U0001f3af",
        "title": "Strategy Advisor",
        "system": (
            "You are a business strategist. You think about competitive moats, market timing, "
            "value ladders, long-term positioning, and opportunity cost. You see the big picture "
            "but ground it in what's actionable THIS WEEK. Challenge assumptions. "
            "Keep it under 200 words."
        ),
    },
}

DEFAULT_SPECIALISTS = ["marketing", "finance", "operations", "content"]


def ollama_query(system_prompt, user_prompt, model=DEFAULT_MODEL):
    """Query Ollama with a system + user prompt."""
    for base_url in OLLAMA_URLS:
        try:
            payload = json.dumps({
                "model": model,
                "system": system_prompt,
                "prompt": user_prompt,
                "stream": False,
            }).encode("utf-8")

            req = urllib.request.Request(
                f"{base_url}/api/generate",
                data=payload,
                headers={"Content-Type": "application/json"},
                method="POST",
            )
            resp = urllib.request.urlopen(req, timeout=120)
            result = json.loads(resp.read())
            return result.get("response", "").strip()
        except Exception:
            continue
    return None


def run_specialist(name, question, context="", model=DEFAULT_MODEL):
    """Run a single specialist review."""
    spec = SPECIALISTS[name]
    prompt = question
    if context:
        prompt = f"Context:\n{context}\n\nQuestion/Decision:\n{question}"

    start = time.time()
    response = ollama_query(spec["system"], prompt, model=model)
    elapsed = time.time() - start

    return {
        "name": name,
        "emoji": spec["emoji"],
        "title": spec["title"],
        "response": response,
        "elapsed": elapsed,
    }


def run_boardroom(question, specialists=None, context="", parallel=True, model=DEFAULT_MODEL):
    """Run a full boardroom session."""
    specs = specialists or DEFAULT_SPECIALISTS
    specs = [s for s in specs if s in SPECIALISTS]

    print(f"\n{'=' * 60}")
    print(f"  BOARDROOM SESSION")
    print(f"{'=' * 60}")
    print(f"  Question: {question[:80]}{'...' if len(question) > 80 else ''}")
    print(f"  Advisors: {', '.join(specs)}")
    print(f"{'=' * 60}\n")

    results = []

    if parallel:
        with ThreadPoolExecutor(max_workers=len(specs)) as executor:
            futures = {
                executor.submit(run_specialist, name, question, context, model): name
                for name in specs
            }
            for future in as_completed(futures):
                name = futures[future]
                try:
                    result = future.result()
                    results.append(result)
                    print(f"  {result['emoji']} {result['title']} responded ({result['elapsed']:.1f}s)")
                except Exception as e:
                    print(f"  [ERROR] {name}: {e}")
    else:
        for name in specs:
            print(f"  Consulting {SPECIALISTS[name]['title']}...")
            result = run_specialist(name, question, context, model)
            results.append(result)
            print(f"  {result['emoji']} responded ({result['elapsed']:.1f}s)")

    # Print results
    print(f"\n{'=' * 60}")
    print(f"  ADVISOR RESPONSES")
    print(f"{'=' * 60}\n")

    for r in results:
        if r["response"]:
            print(f"{r['emoji']} {r['title'].upper()}")
            print(f"{'-' * 40}")
            print(r["response"])
            print()
        else:
            print(f"{r['emoji']} {r['title'].upper()}")
            print(f"  [No response - Ollama may be unavailable]")
            print()

    # Generate synthesis if we got multiple responses
    if len([r for r in results if r["response"]]) >= 2:
        print(f"{'=' * 60}")
        print(f"  BOARDROOM SYNTHESIS")
        print(f"{'=' * 60}\n")

        all_advice = "\n\n".join(
            f"{r['title']}: {r['response']}"
            for r in results if r["response"]
        )
        synthesis_prompt = (
            f"You received advice from multiple specialists on this question:\n"
            f"{question}\n\n"
            f"Their responses:\n{all_advice}\n\n"
            f"Synthesize their advice into 3-5 clear action items. Note any conflicts "
            f"between advisors and recommend which side to take. Be decisive. Keep it under 150 words."
        )
        synthesis = ollama_query(
            "You are a CEO synthesizing advisor input into clear decisions.",
            synthesis_prompt,
        )
        if synthesis:
            print(synthesis)
        print()

    return results


def main():
    parser = argparse.ArgumentParser(description="Boardroom Mode -- multi-specialist review")
    parser.add_argument("question", nargs="?", help="The question or decision to review")
    parser.add_argument("--file", help="File to include as context")
    parser.add_argument("--specialists", help="Comma-separated list of specialists")
    parser.add_argument("--all", action="store_true", help="Use all available specialists")
    parser.add_argument("--list", action="store_true", help="List available specialists")
    parser.add_argument("--model", default=DEFAULT_MODEL, help="Ollama model to use")
    parser.add_argument("--save", help="Save session to file")

    args = parser.parse_args()

    if args.list:
        print("\nAvailable specialists:")
        for name, spec in SPECIALISTS.items():
            print(f"  {spec['emoji']} {name:12s} -- {spec['title']}")
        print(f"\nDefault: {', '.join(DEFAULT_SPECIALISTS)}")
        return

    if not args.question:
        parser.print_help()
        return

    context = ""
    if args.file:
        try:
            with open(args.file) as f:
                context = f.read()
        except Exception as e:
            print(f"Error reading file: {e}")
            return

    specs = None
    if args.all:
        specs = list(SPECIALISTS.keys())
    elif args.specialists:
        specs = [s.strip() for s in args.specialists.split(",")]

    results = run_boardroom(args.question, specialists=specs, context=context, model=args.model)

    if args.save:
        output = {
            "question": args.question,
            "specialists": [r["name"] for r in results],
            "responses": {r["name"]: r["response"] for r in results},
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        }
        with open(args.save, "w") as f:
            json.dump(output, f, indent=2)
        print(f"Session saved to {args.save}")


if __name__ == "__main__":
    main()

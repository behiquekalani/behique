#!/usr/bin/env python3
"""
ChatGPT Relay — Lets Ceiba send prompts to GPT-4o and save responses.
Usage:
  python3 chatgpt_relay.py --prompt "Design an agent kernel" --output designs/output.md
  python3 chatgpt_relay.py --prompt-file prompts/kernel.txt --output designs/kernel.md
  python3 chatgpt_relay.py --prompt "Quick question" --model gpt-4o-mini
"""

import argparse
import os
import sys
import time
import json
from pathlib import Path

try:
    from openai import OpenAI
except ImportError:
    print("❌ openai package not installed. Run: pip3 install openai")
    sys.exit(1)

# Auto-load .env from project root
DOTENV_PATH = Path(__file__).resolve().parent.parent / ".env"
if DOTENV_PATH.exists():
    for line in DOTENV_PATH.read_text().splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            key, _, value = line.partition("=")
            os.environ.setdefault(key.strip(), value.strip())


# Cost per 1M tokens (as of March 2026 — update if pricing changes)
COST_TABLE = {
    "gpt-4o": {"input": 2.50, "output": 10.00},
    "gpt-4o-mini": {"input": 0.15, "output": 0.60},
    "gpt-4.1": {"input": 2.00, "output": 8.00},
    "gpt-4.1-mini": {"input": 0.40, "output": 1.60},
}

SYSTEM_PROMPT = """You are a senior software architect and systems designer working with an AI agent cluster.
You produce clean, detailed, production-ready architecture documents, code, and specifications.
Output in well-structured Markdown with proper code blocks, tables, and diagrams where helpful.
Be thorough but practical — this code will actually be built and deployed."""


def estimate_cost(model: str, prompt_tokens: int, completion_tokens: int) -> float:
    """Estimate cost in USD based on token usage."""
    costs = COST_TABLE.get(model, COST_TABLE["gpt-4o"])
    input_cost = (prompt_tokens / 1_000_000) * costs["input"]
    output_cost = (completion_tokens / 1_000_000) * costs["output"]
    return input_cost + output_cost


def send_prompt(client: OpenAI, model: str, prompt: str, max_retries: int = 3) -> dict:
    """Send prompt to OpenAI with retries and exponential backoff."""
    for attempt in range(1, max_retries + 1):
        try:
            print(f"📡 Sending to {model}... (attempt {attempt}/{max_retries})")
            response = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": prompt},
                ],
                temperature=0.7,
                max_tokens=16000,
            )

            content = response.choices[0].message.content
            usage = response.usage

            return {
                "content": content,
                "model": model,
                "prompt_tokens": usage.prompt_tokens,
                "completion_tokens": usage.completion_tokens,
                "total_tokens": usage.total_tokens,
                "cost_usd": estimate_cost(model, usage.prompt_tokens, usage.completion_tokens),
            }

        except Exception as e:
            print(f"⚠️  Attempt {attempt} failed: {e}")
            if attempt < max_retries:
                wait = 2 ** attempt
                print(f"   Retrying in {wait}s...")
                time.sleep(wait)
            else:
                print("❌ All retries exhausted.")
                raise


def main():
    parser = argparse.ArgumentParser(description="ChatGPT Relay — Send prompts to GPT-4o from CLI")
    parser.add_argument("--prompt", "-p", type=str, help="Direct prompt text")
    parser.add_argument("--prompt-file", "-f", type=str, help="Read prompt from file")
    parser.add_argument("--output", "-o", type=str, help="Save response to file (markdown)")
    parser.add_argument("--model", "-m", type=str, default="gpt-4o", help="Model (default: gpt-4o)")
    parser.add_argument("--system", "-s", type=str, help="Custom system prompt (overrides default)")
    parser.add_argument("--log", type=str, help="Append usage stats to log file")

    args = parser.parse_args()

    # Get prompt
    if args.prompt_file:
        prompt_path = Path(args.prompt_file)
        if not prompt_path.exists():
            print(f"❌ Prompt file not found: {args.prompt_file}")
            sys.exit(1)
        prompt = prompt_path.read_text().strip()
    elif args.prompt:
        prompt = args.prompt
    else:
        print("❌ Provide --prompt or --prompt-file")
        sys.exit(1)

    # Check API key
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        print("❌ OPENAI_API_KEY not set. Export it first:")
        print("   export OPENAI_API_KEY='sk-...'")
        sys.exit(1)

    # Override system prompt if provided
    global SYSTEM_PROMPT
    if args.system:
        SYSTEM_PROMPT = args.system

    # Send
    client = OpenAI(api_key=api_key)
    result = send_prompt(client, args.model, prompt)

    # Output
    content = result["content"]

    if args.output:
        out_path = Path(args.output)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(content)
        print(f"✅ Saved to {args.output}")
    else:
        print("\n" + "=" * 60)
        print(content)
        print("=" * 60)

    # Stats
    cost_str = f"${result['cost_usd']:.4f}"
    print(f"\n📊 {result['model']} | {result['prompt_tokens']} in + {result['completion_tokens']} out = {result['total_tokens']} tokens | ~{cost_str}")

    # Log
    if args.log:
        log_entry = {
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
            "model": result["model"],
            "prompt_tokens": result["prompt_tokens"],
            "completion_tokens": result["completion_tokens"],
            "total_tokens": result["total_tokens"],
            "cost_usd": result["cost_usd"],
            "output_file": args.output or "(stdout)",
            "prompt_preview": prompt[:100] + "..." if len(prompt) > 100 else prompt,
        }
        log_path = Path(args.log)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        with open(log_path, "a") as f:
            f.write(json.dumps(log_entry) + "\n")
        print(f"📝 Usage logged to {args.log}")


if __name__ == "__main__":
    main()

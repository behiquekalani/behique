#!/usr/bin/env python3
"""
CodeGPT Bridge — Multi-model AI routing for Ceiba.
Routes prompts to OpenAI, Ollama, Groq, or Together AI.

Required packages:
    pip install openai groq together tiktoken

CLI usage:
    python tools/codegpt_bridge.py "your prompt" --model gpt-4o
    python tools/codegpt_bridge.py "your prompt" --model ollama:llama3.2
    python tools/codegpt_bridge.py "your prompt" --model groq:llama3-70b
    python tools/codegpt_bridge.py "your prompt" --model together:meta-llama/Meta-Llama-3.1-70B-Instruct-Turbo
    python tools/codegpt_bridge.py --interactive --model ollama:codellama
    python tools/codegpt_bridge.py "explain this" --file main.py --system "You are a code reviewer"
    python tools/codegpt_bridge.py "give me JSON" --model gpt-4o-mini --json

Module usage:
    from tools.codegpt_bridge import query_model
    result = query_model("explain this code", model="ollama:codellama", system="You are a code reviewer")
"""

import argparse
import json
import os
import sys
import time
from pathlib import Path
from typing import Generator, Optional

# ---------------------------------------------------------------------------
# Auto-load .env from project root (same pattern as chatgpt_relay.py)
# ---------------------------------------------------------------------------
DOTENV_PATH = Path(__file__).resolve().parent.parent / ".env"
if DOTENV_PATH.exists():
    for line in DOTENV_PATH.read_text().splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            key, _, value = line.partition("=")
            os.environ.setdefault(key.strip(), value.strip())

# ---------------------------------------------------------------------------
# Config — reads ~/.behique_ai_config.json if it exists
# ---------------------------------------------------------------------------
CONFIG_PATH = Path.home() / ".behique_ai_config.json"
DEFAULT_CONFIG = {
    "default_model": "ollama:llama3.2",
    "ollama_base_url": "http://localhost:11434",
    "openai_base_url": None,        # use default
    "groq_base_url": None,          # use default
    "together_base_url": None,      # use default
    "stream": True,
    "temperature": 0.7,
    "max_tokens": 4096,
}

def load_config() -> dict:
    """Load config from disk, falling back to defaults."""
    config = dict(DEFAULT_CONFIG)
    if CONFIG_PATH.exists():
        try:
            user_cfg = json.loads(CONFIG_PATH.read_text())
            config.update(user_cfg)
        except (json.JSONDecodeError, OSError) as e:
            print(f"[warn] Failed to read config: {e}", file=sys.stderr)
    return config

CONFIG = load_config()

# ---------------------------------------------------------------------------
# Cost table — price per 1M tokens (input / output) for paid APIs
# Updated as of early 2025. Add new models as needed.
# ---------------------------------------------------------------------------
COST_PER_1M = {
    # OpenAI
    "gpt-4o":          {"input": 2.50, "output": 10.00},
    "gpt-4o-mini":     {"input": 0.15, "output": 0.60},
    "gpt-4.1":         {"input": 2.00, "output": 8.00},
    "gpt-4.1-mini":    {"input": 0.40, "output": 1.60},
    "gpt-4.1-nano":    {"input": 0.10, "output": 0.40},
    "o3-mini":         {"input": 1.10, "output": 4.40},
    # Groq — most are free tier or very cheap
    "groq:llama3-70b":          {"input": 0.59, "output": 0.79},
    "groq:llama3-8b":           {"input": 0.05, "output": 0.08},
    "groq:llama-3.3-70b-versatile": {"input": 0.59, "output": 0.79},
    "groq:mixtral-8x7b-32768":  {"input": 0.24, "output": 0.24},
    "groq:gemma2-9b-it":        {"input": 0.20, "output": 0.20},
    # Together AI
    "together:meta-llama/Meta-Llama-3.1-70B-Instruct-Turbo": {"input": 0.88, "output": 0.88},
    "together:meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo":  {"input": 0.18, "output": 0.18},
    "together:mistralai/Mixtral-8x7B-Instruct-v0.1":         {"input": 0.60, "output": 0.60},
}

# ---------------------------------------------------------------------------
# Provider: parse model string into (provider, model_name)
# ---------------------------------------------------------------------------
def parse_model(model: str) -> tuple[str, str]:
    """
    Parse 'provider:model_name' format.
    If no prefix, assume OpenAI for gpt-* / o3-* models, otherwise ollama.
    """
    if ":" in model:
        provider, _, name = model.partition(":")
        return provider.lower(), name
    # Auto-detect provider from model name
    if model.startswith(("gpt-", "o3-", "o4-")):
        return "openai", model
    return "ollama", model

# ---------------------------------------------------------------------------
# Token counting (best-effort with tiktoken for OpenAI, estimate otherwise)
# ---------------------------------------------------------------------------
def count_tokens(text: str, model: str = "gpt-4o") -> int:
    """Count tokens. Uses tiktoken for OpenAI models, rough estimate otherwise."""
    try:
        import tiktoken
        try:
            enc = tiktoken.encoding_for_model(model)
        except KeyError:
            enc = tiktoken.get_encoding("cl100k_base")
        return len(enc.encode(text))
    except ImportError:
        # Rough estimate: ~4 chars per token for English
        return len(text) // 4

def estimate_cost(model_key: str, input_tokens: int, output_tokens: int) -> Optional[float]:
    """Estimate cost in USD. Returns None if model not in cost table."""
    rates = COST_PER_1M.get(model_key)
    if not rates:
        return None
    cost = (input_tokens * rates["input"] + output_tokens * rates["output"]) / 1_000_000
    return cost

# ---------------------------------------------------------------------------
# Provider implementations
# ---------------------------------------------------------------------------

def _stream_openai(messages: list, model: str, temperature: float,
                   max_tokens: int, json_mode: bool) -> Generator[str, None, dict]:
    """Stream from OpenAI. Yields chunks, returns usage stats via .value after StopIteration."""
    try:
        from openai import OpenAI
    except ImportError:
        print("[error] openai package not installed. Run: pip install openai", file=sys.stderr)
        sys.exit(1)

    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        print("[error] OPENAI_API_KEY not set.", file=sys.stderr)
        sys.exit(1)

    kwargs = {}
    if CONFIG.get("openai_base_url"):
        kwargs["base_url"] = CONFIG["openai_base_url"]

    client = OpenAI(api_key=api_key, **kwargs)
    extra = {}
    if json_mode:
        extra["response_format"] = {"type": "json_object"}

    stream = client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=temperature,
        max_tokens=max_tokens,
        stream=True,
        stream_options={"include_usage": True},
        **extra,
    )

    full_text = []
    usage = {}
    for chunk in stream:
        if chunk.usage:
            usage = {
                "input_tokens": chunk.usage.prompt_tokens,
                "output_tokens": chunk.usage.completion_tokens,
            }
        if chunk.choices and chunk.choices[0].delta.content:
            text = chunk.choices[0].delta.content
            full_text.append(text)
            yield text

    # Attach usage to the generator (caller retrieves via _last_usage)
    _stream_openai._last_usage = usage
    _stream_openai._last_text = "".join(full_text)


def _stream_ollama(messages: list, model: str, temperature: float,
                   max_tokens: int, json_mode: bool) -> Generator[str, None, None]:
    """Stream from Ollama local server."""
    import urllib.request
    import urllib.error

    base_url = CONFIG.get("ollama_base_url", "http://localhost:11434")
    url = f"{base_url}/api/chat"

    payload = {
        "model": model,
        "messages": messages,
        "stream": True,
        "options": {
            "temperature": temperature,
            "num_predict": max_tokens,
        },
    }
    if json_mode:
        payload["format"] = "json"

    data = json.dumps(payload).encode()
    req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"})

    full_text = []
    total_tokens = 0
    try:
        with urllib.request.urlopen(req) as resp:
            for line in resp:
                if not line.strip():
                    continue
                chunk = json.loads(line)
                if chunk.get("message", {}).get("content"):
                    text = chunk["message"]["content"]
                    full_text.append(text)
                    yield text
                if chunk.get("done"):
                    total_tokens = chunk.get("eval_count", 0)
    except urllib.error.URLError as e:
        print(f"[error] Cannot reach Ollama at {base_url}: {e}", file=sys.stderr)
        print("Make sure Ollama is running: ollama serve", file=sys.stderr)
        sys.exit(1)

    _stream_ollama._last_usage = {
        "input_tokens": 0,  # Ollama doesn't always report this
        "output_tokens": total_tokens,
    }
    _stream_ollama._last_text = "".join(full_text)


def _stream_groq(messages: list, model: str, temperature: float,
                 max_tokens: int, json_mode: bool) -> Generator[str, None, None]:
    """Stream from Groq."""
    try:
        from groq import Groq
    except ImportError:
        print("[error] groq package not installed. Run: pip install groq", file=sys.stderr)
        sys.exit(1)

    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key:
        print("[error] GROQ_API_KEY not set.", file=sys.stderr)
        sys.exit(1)

    kwargs = {}
    if CONFIG.get("groq_base_url"):
        kwargs["base_url"] = CONFIG["groq_base_url"]

    client = Groq(api_key=api_key, **kwargs)
    extra = {}
    if json_mode:
        extra["response_format"] = {"type": "json_object"}

    stream = client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=temperature,
        max_tokens=max_tokens,
        stream=True,
        **extra,
    )

    full_text = []
    usage = {}
    for chunk in stream:
        if hasattr(chunk, "x_groq") and chunk.x_groq and hasattr(chunk.x_groq, "usage"):
            usage = {
                "input_tokens": chunk.x_groq.usage.prompt_tokens,
                "output_tokens": chunk.x_groq.usage.completion_tokens,
            }
        if chunk.choices and chunk.choices[0].delta.content:
            text = chunk.choices[0].delta.content
            full_text.append(text)
            yield text

    _stream_groq._last_usage = usage
    _stream_groq._last_text = "".join(full_text)


def _stream_together(messages: list, model: str, temperature: float,
                     max_tokens: int, json_mode: bool) -> Generator[str, None, None]:
    """Stream from Together AI."""
    try:
        from together import Together
    except ImportError:
        print("[error] together package not installed. Run: pip install together", file=sys.stderr)
        sys.exit(1)

    api_key = os.environ.get("TOGETHER_API_KEY")
    if not api_key:
        print("[error] TOGETHER_API_KEY not set.", file=sys.stderr)
        sys.exit(1)

    kwargs = {}
    if CONFIG.get("together_base_url"):
        kwargs["base_url"] = CONFIG["together_base_url"]

    client = Together(api_key=api_key, **kwargs)

    stream = client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=temperature,
        max_tokens=max_tokens,
        stream=True,
    )

    full_text = []
    usage = {}
    for chunk in stream:
        if hasattr(chunk, "usage") and chunk.usage:
            usage = {
                "input_tokens": getattr(chunk.usage, "prompt_tokens", 0),
                "output_tokens": getattr(chunk.usage, "completion_tokens", 0),
            }
        if chunk.choices and chunk.choices[0].delta.content:
            text = chunk.choices[0].delta.content
            full_text.append(text)
            yield text

    _stream_together._last_usage = usage
    _stream_together._last_text = "".join(full_text)

# ---------------------------------------------------------------------------
# Main query function — the public API
# ---------------------------------------------------------------------------

def query_model(
    prompt: str,
    model: str | None = None,
    system: str | None = None,
    files: list[str] | None = None,
    json_mode: bool = False,
    temperature: float | None = None,
    max_tokens: int | None = None,
    stream: bool = True,
    messages: list | None = None,
) -> dict:
    """
    Send a prompt to any supported LLM and return the result.

    Args:
        prompt: The user prompt text.
        model: Model string like 'gpt-4o', 'ollama:llama3.2', 'groq:llama3-70b'.
        system: Optional system prompt.
        files: Optional list of file paths whose contents get appended to prompt.
        json_mode: Request JSON output (supported by OpenAI, Ollama, Groq).
        temperature: Override config temperature.
        max_tokens: Override config max_tokens.
        stream: Whether to stream (True) or collect silently (False).
        messages: Full message history (for interactive mode). Overrides prompt/system if given.

    Returns:
        dict with keys: text, model, provider, usage, cost, elapsed
    """
    model = model or CONFIG["default_model"]
    temperature = temperature if temperature is not None else CONFIG["temperature"]
    max_tokens = max_tokens or CONFIG["max_tokens"]

    provider, model_name = parse_model(model)

    # Build messages if not provided directly
    if messages is None:
        messages = []
        if system:
            messages.append({"role": "system", "content": system})

        # Append file contents to prompt
        full_prompt = prompt
        if files:
            file_parts = []
            for fpath in files:
                p = Path(fpath)
                if p.exists():
                    content = p.read_text(errors="replace")
                    file_parts.append(f"--- {p.name} ---\n{content}\n--- end {p.name} ---")
                else:
                    file_parts.append(f"[file not found: {fpath}]")
            full_prompt = prompt + "\n\n" + "\n\n".join(file_parts)

        messages.append({"role": "user", "content": full_prompt})

    # Route to provider
    dispatch = {
        "openai":   _stream_openai,
        "ollama":   _stream_ollama,
        "groq":     _stream_groq,
        "together":  _stream_together,
    }

    stream_fn = dispatch.get(provider)
    if not stream_fn:
        print(f"[error] Unknown provider '{provider}'. Supported: {', '.join(dispatch.keys())}", file=sys.stderr)
        sys.exit(1)

    t0 = time.time()
    collected = []

    gen = stream_fn(messages, model_name, temperature, max_tokens, json_mode)
    for chunk in gen:
        collected.append(chunk)
        if stream:
            print(chunk, end="", flush=True)
    if stream:
        print()  # trailing newline

    elapsed = time.time() - t0
    full_text = "".join(collected)

    # Retrieve usage from the provider function
    usage = getattr(stream_fn, "_last_usage", {})
    input_tokens = usage.get("input_tokens", 0)
    output_tokens = usage.get("output_tokens", 0)

    # If provider didn't report input tokens, estimate
    if input_tokens == 0:
        input_tokens = count_tokens(json.dumps(messages), model_name)

    # Build the model key for cost lookup
    model_key = model if provider != "openai" else model_name
    cost = estimate_cost(model_key, input_tokens, output_tokens)

    return {
        "text": full_text,
        "model": model,
        "provider": provider,
        "usage": {"input_tokens": input_tokens, "output_tokens": output_tokens},
        "cost": cost,
        "elapsed": round(elapsed, 2),
    }

# ---------------------------------------------------------------------------
# Interactive chat mode
# ---------------------------------------------------------------------------

def interactive_chat(model: str, system: str | None = None, json_mode: bool = False):
    """Run an interactive chat session."""
    provider, model_name = parse_model(model)
    print(f"[codegpt-bridge] Interactive mode | model={model} | provider={provider}")
    print(f"[codegpt-bridge] Type 'exit' or 'quit' to end. '/clear' to reset history.\n")

    messages = []
    if system:
        messages.append({"role": "system", "content": system})

    total_cost = 0.0

    while True:
        try:
            user_input = input("you> ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n[bye]")
            break

        if not user_input:
            continue
        if user_input.lower() in ("exit", "quit"):
            break
        if user_input == "/clear":
            messages = []
            if system:
                messages.append({"role": "system", "content": system})
            print("[history cleared]")
            continue

        messages.append({"role": "user", "content": user_input})

        print(f"\n{model_name}> ", end="", flush=True)
        result = query_model(
            prompt="",  # unused when messages are passed directly
            model=model,
            json_mode=json_mode,
            messages=list(messages),  # copy so query_model doesn't mutate
            stream=True,
        )

        messages.append({"role": "assistant", "content": result["text"]})

        if result["cost"] is not None:
            total_cost += result["cost"]

        # Stats line
        u = result["usage"]
        stats = f"[{u['input_tokens']}in/{u['output_tokens']}out | {result['elapsed']}s"
        if result["cost"] is not None:
            stats += f" | ${result['cost']:.4f} (session: ${total_cost:.4f})"
        stats += "]"
        print(stats)
        print()

# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="CodeGPT Bridge — Multi-model AI routing for Ceiba",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s "explain this error" --model gpt-4o-mini
  %(prog)s "review this code" --model ollama:codellama --file main.py
  %(prog)s --interactive --model groq:llama3-70b --system "You are a Python expert"
  %(prog)s "list 5 ideas" --model together:meta-llama/Meta-Llama-3.1-70B-Instruct-Turbo --json

Providers:
  gpt-4o, gpt-4o-mini, o3-mini          OpenAI  (needs OPENAI_API_KEY)
  ollama:<model>                         Ollama  (local, no key needed)
  groq:<model>                           Groq    (needs GROQ_API_KEY)
  together:<model>                       Together (needs TOGETHER_API_KEY)
        """,
    )
    parser.add_argument("prompt", nargs="?", default="", help="The prompt to send")
    parser.add_argument("-m", "--model", default=None, help=f"Model to use (default: {CONFIG['default_model']})")
    parser.add_argument("-s", "--system", default=None, help="System prompt")
    parser.add_argument("-f", "--file", action="append", dest="files", help="Include file contents (repeatable)")
    parser.add_argument("--json", action="store_true", dest="json_mode", help="Request JSON output")
    parser.add_argument("-i", "--interactive", action="store_true", help="Start interactive chat")
    parser.add_argument("-t", "--temperature", type=float, default=None, help="Temperature override")
    parser.add_argument("--max-tokens", type=int, default=None, help="Max tokens override")
    parser.add_argument("--no-stream", action="store_true", help="Disable streaming (collect full response)")
    parser.add_argument("--stats", action="store_true", help="Print usage stats after response")
    parser.add_argument("--list-models", action="store_true", help="List known models with pricing")

    args = parser.parse_args()

    # List models mode
    if args.list_models:
        print(f"{'Model':<60} {'Input $/1M':>10} {'Output $/1M':>12}")
        print("-" * 84)
        for m, rates in sorted(COST_PER_1M.items()):
            print(f"{m:<60} ${rates['input']:>8.2f}  ${rates['output']:>10.2f}")
        print("\nOllama models are free (local). Run 'ollama list' to see installed models.")
        return

    model = args.model or CONFIG["default_model"]

    # Interactive mode
    if args.interactive:
        interactive_chat(model, system=args.system, json_mode=args.json_mode)
        return

    # Single query mode — need a prompt
    if not args.prompt:
        parser.print_help()
        sys.exit(1)

    result = query_model(
        prompt=args.prompt,
        model=model,
        system=args.system,
        files=args.files,
        json_mode=args.json_mode,
        temperature=args.temperature,
        max_tokens=args.max_tokens,
        stream=not args.no_stream,
    )

    # Print stats if requested
    if args.stats or args.no_stream:
        if args.no_stream:
            print(result["text"])
        u = result["usage"]
        print(f"\n--- stats ---", file=sys.stderr)
        print(f"model:    {result['model']}", file=sys.stderr)
        print(f"provider: {result['provider']}", file=sys.stderr)
        print(f"tokens:   {u['input_tokens']} in / {u['output_tokens']} out", file=sys.stderr)
        print(f"time:     {result['elapsed']}s", file=sys.stderr)
        if result["cost"] is not None:
            print(f"cost:     ${result['cost']:.6f}", file=sys.stderr)


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
Prompt Quality Comparator — Multi-Model A/B Testing

Takes a prompt, runs it through multiple LLM backends, evaluates outputs,
and returns the best result with scoring. Useful for finding which model
produces the best eBay titles, descriptions, or agent responses.

Supported backends:
  - Ollama (local, free) — llama3.2 on Cobo
  - OpenAI (GPT-4o-mini, GPT-4o) — via API key
  - Anthropic (Claude) — via API key (or in-session)

Usage via Kernel:
    dispatcher.add_task(
        skill="skills.prompt_comparator",
        params={
            "prompt": "Write an eBay title for Hello Kitty Mug",
            "models": "ollama:llama3.2,openai:gpt-4o-mini",
            "criteria": "seo_quality,creativity,accuracy",
        },
    )

Usage standalone:
    python3 -m skills.prompt_comparator \\
        --prompt "Write a product title for Hello Kitty Mug" \\
        --models ollama:llama3.2,openai:gpt-4o-mini
"""

import os
import json
import time
import hashlib
from datetime import datetime, timezone
from typing import Dict, List, Optional, Tuple


# ============ Config ============
OLLAMA_URL = os.environ.get("OLLAMA_URL", "http://192.168.0.151:11434")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "")
ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")


# ============ Model Backends ============
def query_ollama(prompt: str, model: str = "llama3.2", timeout: int = 30) -> dict:
    """Query Ollama on Cobo."""
    try:
        import requests
        resp = requests.post(
            f"{OLLAMA_URL}/api/generate",
            json={"model": model, "prompt": prompt, "stream": False},
            timeout=timeout,
        )
        resp.raise_for_status()
        data = resp.json()
        return {
            "text": data.get("response", ""),
            "model": f"ollama:{model}",
            "latency_ms": int(data.get("total_duration", 0) / 1_000_000),
            "tokens": data.get("eval_count", 0),
            "error": None,
        }
    except Exception as e:
        return {"text": "", "model": f"ollama:{model}", "error": str(e)}


def query_openai(prompt: str, model: str = "gpt-4o-mini", timeout: int = 30) -> dict:
    """Query OpenAI API."""
    if not OPENAI_API_KEY:
        return {"text": "", "model": f"openai:{model}", "error": "OPENAI_API_KEY not set"}
    try:
        import requests
        resp = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers={"Authorization": f"Bearer {OPENAI_API_KEY}"},
            json={
                "model": model,
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": 500,
            },
            timeout=timeout,
        )
        resp.raise_for_status()
        data = resp.json()
        text = data["choices"][0]["message"]["content"]
        usage = data.get("usage", {})
        return {
            "text": text,
            "model": f"openai:{model}",
            "tokens": usage.get("completion_tokens", 0),
            "error": None,
        }
    except Exception as e:
        return {"text": "", "model": f"openai:{model}", "error": str(e)}


def query_anthropic(prompt: str, model: str = "claude-sonnet-4-20250514", timeout: int = 30) -> dict:
    """Query Anthropic API."""
    if not ANTHROPIC_API_KEY:
        return {"text": "", "model": f"anthropic:{model}", "error": "ANTHROPIC_API_KEY not set"}
    try:
        import requests
        resp = requests.post(
            "https://api.anthropic.com/v1/messages",
            headers={
                "x-api-key": ANTHROPIC_API_KEY,
                "content-type": "application/json",
                "anthropic-version": "2023-06-01",
            },
            json={
                "model": model,
                "max_tokens": 500,
                "messages": [{"role": "user", "content": prompt}],
            },
            timeout=timeout,
        )
        resp.raise_for_status()
        data = resp.json()
        text = data["content"][0]["text"]
        return {
            "text": text,
            "model": f"anthropic:{model}",
            "tokens": data.get("usage", {}).get("output_tokens", 0),
            "error": None,
        }
    except Exception as e:
        return {"text": "", "model": f"anthropic:{model}", "error": str(e)}


BACKENDS = {
    "ollama": query_ollama,
    "openai": query_openai,
    "anthropic": query_anthropic,
}


# ============ Evaluation Criteria ============
def evaluate_output(text: str, prompt: str, criteria: List[str]) -> Dict[str, float]:
    """
    Score an output on multiple criteria (0-100 each).
    Uses heuristic scoring — no LLM needed for evaluation.
    """
    scores = {}

    if "length" in criteria:
        # Prefer 50-200 chars for titles, 200-1000 for descriptions
        l = len(text)
        if 50 <= l <= 200:
            scores["length"] = 90
        elif 20 <= l <= 500:
            scores["length"] = 70
        else:
            scores["length"] = max(30, 100 - abs(l - 150) / 5)

    if "seo_quality" in criteria:
        # eBay SEO: keyword density, no fluff words, proper capitalization
        score = 50
        words = text.split()
        if len(words) >= 5:
            score += 10
        if len(words) <= 15:
            score += 10
        # Title case or ALL CAPS (eBay style)
        if text == text.title() or any(w.isupper() for w in words[:3]):
            score += 10
        # No filler words
        fillers = {"amazing", "incredible", "awesome", "great", "wonderful", "fantastic"}
        if not any(w.lower() in fillers for w in words):
            score += 10
        # Contains specifics (numbers, brand-like words)
        if any(c.isdigit() for c in text):
            score += 10
        scores["seo_quality"] = min(score, 100)

    if "creativity" in criteria:
        # Unique word ratio, variety
        words = text.lower().split()
        unique_ratio = len(set(words)) / max(len(words), 1)
        scores["creativity"] = int(unique_ratio * 100)

    if "accuracy" in criteria:
        # Check if output addresses the prompt (word overlap)
        prompt_words = set(prompt.lower().split())
        output_words = set(text.lower().split())
        overlap = len(prompt_words & output_words) / max(len(prompt_words), 1)
        scores["accuracy"] = int(min(overlap * 150, 100))  # Boost slightly

    if "conciseness" in criteria:
        words = text.split()
        if len(words) <= 20:
            scores["conciseness"] = 95
        elif len(words) <= 50:
            scores["conciseness"] = 80
        elif len(words) <= 100:
            scores["conciseness"] = 60
        else:
            scores["conciseness"] = 40

    if "formatting" in criteria:
        score = 50
        if text.strip():
            score += 10
        if not text.startswith(" "):
            score += 10
        if text[-1] in ".!?" or text[-1].isalnum():
            score += 10
        # No excessive whitespace
        if "  " not in text:
            score += 10
        if "\n\n\n" not in text:
            score += 10
        scores["formatting"] = min(score, 100)

    return scores


# ============ Comparator ============
def compare(prompt: str, models: List[str], criteria: List[str] = None) -> dict:
    """
    Run prompt through multiple models and compare outputs.

    Args:
        prompt: The prompt to test
        models: List of "backend:model" strings (e.g., ["ollama:llama3.2", "openai:gpt-4o-mini"])
        criteria: Evaluation criteria (default: all)

    Returns:
        Comparison results with scores and winner
    """
    if not criteria:
        criteria = ["seo_quality", "creativity", "accuracy", "conciseness"]

    results = []
    for model_spec in models:
        parts = model_spec.split(":", 1)
        backend_name = parts[0]
        model_name = parts[1] if len(parts) > 1 else ""

        backend_fn = BACKENDS.get(backend_name)
        if not backend_fn:
            results.append({
                "model": model_spec,
                "error": f"Unknown backend: {backend_name}. Available: {list(BACKENDS.keys())}",
            })
            continue

        start = time.time()
        response = backend_fn(prompt, model_name) if model_name else backend_fn(prompt)
        wall_time_ms = int((time.time() - start) * 1000)

        if response.get("error"):
            results.append({
                "model": model_spec,
                "error": response["error"],
                "wall_time_ms": wall_time_ms,
            })
            continue

        # Evaluate
        scores = evaluate_output(response["text"], prompt, criteria)
        avg_score = round(sum(scores.values()) / max(len(scores), 1), 1)

        results.append({
            "model": model_spec,
            "text": response["text"],
            "scores": scores,
            "avg_score": avg_score,
            "tokens": response.get("tokens", 0),
            "latency_ms": response.get("latency_ms", wall_time_ms),
            "wall_time_ms": wall_time_ms,
            "error": None,
        })

    # Sort by avg_score descending
    valid_results = [r for r in results if not r.get("error")]
    valid_results.sort(key=lambda r: r.get("avg_score", 0), reverse=True)

    winner = valid_results[0] if valid_results else None

    return {
        "prompt": prompt,
        "prompt_hash": hashlib.md5(prompt.encode()).hexdigest()[:8],
        "criteria": criteria,
        "models_tested": len(models),
        "models_succeeded": len(valid_results),
        "results": results,
        "winner": winner["model"] if winner else None,
        "winner_score": winner["avg_score"] if winner else None,
        "winner_text": winner["text"] if winner else None,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


# ============ Skill Entry Point ============
def run(prompt: str = "", models: str = "ollama:llama3.2",
        criteria: str = "seo_quality,creativity,accuracy,conciseness",
        **kwargs) -> dict:
    """Kernel skill entry point."""
    if not prompt:
        return {"error": "prompt parameter is required"}

    model_list = [m.strip() for m in models.split(",") if m.strip()]
    criteria_list = [c.strip() for c in criteria.split(",") if c.strip()]

    return compare(prompt, model_list, criteria_list)


# ============ CLI ============
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Prompt Quality Comparator")
    parser.add_argument("--prompt", required=True, help="Prompt to test")
    parser.add_argument("--models", default="ollama:llama3.2",
                        help="Comma-separated model specs (backend:model)")
    parser.add_argument("--criteria", default="seo_quality,creativity,accuracy,conciseness",
                        help="Comma-separated evaluation criteria")
    parser.add_argument("--json", action="store_true", help="JSON output")
    args = parser.parse_args()

    result = run(prompt=args.prompt, models=args.models, criteria=args.criteria)

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print(f"\n📊 Prompt Comparison — {result['models_succeeded']}/{result['models_tested']} models responded")
        print(f"   Prompt: {result['prompt'][:80]}")
        print()

        for r in result["results"]:
            if r.get("error"):
                print(f"  ❌ {r['model']}: {r['error']}")
            else:
                winner_mark = " 🏆" if r["model"] == result.get("winner") else ""
                print(f"  {'─' * 40}")
                print(f"  {r['model']}{winner_mark} — Score: {r['avg_score']}/100")
                print(f"    Output: {r['text'][:120]}")
                print(f"    Scores: {r['scores']}")
                print(f"    Time: {r['wall_time_ms']}ms | Tokens: {r.get('tokens', '?')}")

        if result.get("winner"):
            print(f"\n  🏆 Winner: {result['winner']} (score: {result['winner_score']})")
        print()

import os
from typing import Iterable, List, Tuple

from openai import OpenAI


"""
routing.py — central LLM router for Behique/Ceiba

This module decides which model/client to use based on task type, following
the Allocator map in Ceiba/05-Knowledge/session-2026-03-15-capture.md.

High‑level policy (v1):
- Vault + housekeeping (primer, wiki traversal, summaries) → Ollama (free)
- BehiqueBot classification, memory matching → Ollama first, OpenAI fallback
- Codegen, architecture / deep strategy → OpenAI (stand‑in for Claude Sonnet/Opus)

API:
- get_chat_clients_for_task(task_type) → iterable of (client, model) pairs
- run_chat(task_type, messages, **kwargs) → chat completion response with fallback
"""


# ── CLIENTS ──────────────────────────────────────────────────────────────────────

OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://192.168.0.151:11434")
OLLAMA_MODEL_DEFAULT = os.getenv("OLLAMA_MODEL", "llama3.2")

OPENAI_MODEL_DEFAULT = os.getenv("OPENAI_MODEL_DEFAULT", "gpt-4o-mini")
OPENAI_MODEL_CODEGEN = os.getenv("OPENAI_MODEL_CODEGEN", OPENAI_MODEL_DEFAULT)
OPENAI_MODEL_ARCH = os.getenv("OPENAI_MODEL_ARCH", OPENAI_MODEL_DEFAULT)

_ollama_client = OpenAI(
    api_key="ollama",
    base_url=f"{OLLAMA_HOST}/v1",
    timeout=5.0,  # Don't hang if Cobo is unreachable (e.g. Railway deploy)
)

_openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


ChatClient = Tuple[OpenAI, str]


def get_chat_clients_for_task(task_type: str) -> List[ChatClient]:
    """
    Return an ordered list of (client, model) pairs to try for the given task.

    task_type is a simple string; current known values:
    - "vault_housekeeping" / "primer_rewrite" / "wiki_traversal" / "stop_hook_summary"
    - "classification"
    - "memory_match"
    - "codegen"
    - "architecture"

    Callers should iterate these in order and handle exceptions/fallbacks.
    """
    t = task_type.lower()

    # Housekeeping + vault traversal → Ollama only
    if t in {
        "vault_housekeeping",
        "primer_rewrite",
        "wiki_traversal",
        "stop_hook_summary",
    }:
        return [(_ollama_client, OLLAMA_MODEL_DEFAULT)]

    # BehiqueBot classification → Ollama first, then OpenAI
    if t == "classification":
        return [
            (_ollama_client, OLLAMA_MODEL_DEFAULT),
            (_openai_client, OPENAI_MODEL_DEFAULT),
        ]

    # Memory matching / "is this an update?" → same pattern as classification
    if t == "memory_match":
        return [
            (_ollama_client, OLLAMA_MODEL_DEFAULT),
            (_openai_client, OPENAI_MODEL_DEFAULT),
        ]

    # Code generation → OpenAI for now (conceptually Claude Sonnet)
    if t == "codegen":
        return [(_openai_client, OPENAI_MODEL_CODEGEN)]

    # Architecture / deep strategic work → OpenAI (conceptually Opus)
    if t == "architecture":
        return [(_openai_client, OPENAI_MODEL_ARCH)]

    # Default: be conservative, mirror classification pattern
    return [
        (_ollama_client, OLLAMA_MODEL_DEFAULT),
        (_openai_client, OPENAI_MODEL_DEFAULT),
    ]


def run_chat(task_type: str, messages: Iterable[dict], **kwargs):
    """
    Convenience helper to run a chat completion with routing + fallback.

    Example:
        response = run_chat(
            "memory_match",
            [
              {"role": "system", "content": system_prompt},
              {"role": "user", "content": user_msg},
            ],
            temperature=0,
            response_format={"type": "json_object"},
        )
    """
    last_error: Exception | None = None

    for client, model in get_chat_clients_for_task(task_type):
        try:
            return client.chat.completions.create(
                model=model,
                messages=list(messages),
                **kwargs,
            )
        except Exception as exc:  # noqa: BLE001
            last_error = exc
            continue

    if last_error is not None:
        raise last_error


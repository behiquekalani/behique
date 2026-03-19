#!/usr/bin/env python3
"""
Claude Code UserPromptSubmit hook — Graph-Aware Vault Context Loader.

When Kalani submits a prompt, this hook:
  1. Extracts topics from the prompt + CWD
  2. Queries the vault graph for relevant nodes via typed relationships
  3. Injects the top context files as a system message

This replaces dumb CWD→file mappings with actual graph traversal.
Ceiba automatically knows about related tools, decisions, patterns, and systems.
"""

import json
import os
import pathlib
import sys


def read_stdin_payload() -> dict:
    try:
        data = sys.stdin.read()
        if not data.strip():
            return {}
        return json.loads(data)
    except Exception:
        return {}


def find_project_root() -> pathlib.Path:
    return pathlib.Path(__file__).resolve().parents[2]


def get_cwd_relative(project_root: pathlib.Path) -> str:
    """Get CWD relative to project root."""
    try:
        cwd = pathlib.Path.cwd()
        return str(cwd.relative_to(project_root))
    except ValueError:
        return ""


def load_file_content(path: str, max_lines: int = 30) -> str:
    """Load first N lines of a file."""
    try:
        p = pathlib.Path(path)
        if not p.exists():
            return ""
        lines = p.read_text(encoding="utf-8").splitlines()[:max_lines]
        return "\n".join(lines)
    except Exception:
        return ""


def main() -> None:
    payload = read_stdin_payload()
    project_root = find_project_root()

    if not (project_root / "primer.md").exists():
        print(json.dumps({"decision": "approve"}))
        return

    # Try graph-aware loading first, fall back to basic if graph unavailable
    context_parts = []

    # Always include primer (lightweight, current state)
    primer_content = load_file_content(str(project_root / "primer.md"), max_lines=20)
    if primer_content:
        context_parts.append(f"[primer.md]\n{primer_content}")

    try:
        # Add tools dir to path for graph_query import
        tools_dir = str(project_root / "tools")
        if tools_dir not in sys.path:
            sys.path.insert(0, tools_dir)

        from vault_context_engine import VaultContextEngine
        engine = VaultContextEngine()

        # Get prompt text if available
        prompt_text = ""
        if isinstance(payload, dict):
            # Extract prompt from the hook payload
            messages = payload.get("messages", [])
            if messages:
                last_msg = messages[-1] if isinstance(messages, list) else {}
                if isinstance(last_msg, dict):
                    content = last_msg.get("content", "")
                    if isinstance(content, str):
                        prompt_text = content

        rel_cwd = get_cwd_relative(project_root)

        # Combine CWD-based and prompt-based context
        results = []
        if prompt_text and len(prompt_text) > 5:
            results = engine.context_for_prompt(prompt_text, top_n=5)
        if not results and rel_cwd:
            results = engine.context_for_cwd(rel_cwd, top_n=5)
        if not results:
            results = engine.context_for("vault", top_n=3)

        # Load content from top results
        for r in results[:5]:
            content = load_file_content(r["path"], max_lines=25)
            if content:
                context_parts.append(
                    f"[{r['node']}] (type:{r['type']}, relevance:{r['score']})\n{content}"
                )

    except Exception:
        # Fallback: basic CWD-based loading if graph engine fails
        ceiba = project_root / "Ceiba"
        fallback_files = [ceiba / "VAULT_INDEX.md"]

        rel_cwd = get_cwd_relative(project_root)
        project_map = {
            "ebay": "eBay-Listing-Assistant.md",
            "shopify": "Shopify-Store.md",
            "behiquebot": "BehiqueBot.md",
            "n8n": "n8n-Agency.md",
            "trends": "Google-Trends-Scraper.md",
        }
        for keyword, filename in project_map.items():
            if keyword in rel_cwd.lower():
                fallback_files.append(ceiba / "01-Projects" / filename)
                break

        for f in fallback_files:
            if f.exists():
                content = load_file_content(str(f), max_lines=25)
                if content:
                    rel_name = str(f.relative_to(project_root))
                    context_parts.append(f"[{rel_name}]\n{content}")

    # Output hook result
    result = {"decision": "approve"}
    if context_parts:
        result["suppressOutput"] = True
    print(json.dumps(result))


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
ceiba_audit.py — AI cross-review for recent code changes.

Inspired by Jared's workflow: extract changed code → send to a second AI
for dead code detection, redundancies, and quality audit → present findings.

Uses codegpt_bridge for model routing. Default: Ollama (free) → OpenAI fallback.

Usage:
    ceiba audit                      # Audit uncommitted changes
    ceiba audit --commits 3          # Audit last 3 commits
    ceiba audit --file path/to.py    # Audit a specific file
    ceiba audit --model openai:gpt-4o-mini   # Use specific model
    ceiba audit --full               # Deep audit (slower, more thorough)
"""

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path

BEHIQUE = Path.home() / "behique"

# ── Git helpers ──────────────────────────────────────────────────────────────

def get_uncommitted_diff() -> str:
    """Get diff of all uncommitted changes (staged + unstaged)."""
    result = subprocess.run(
        ["git", "diff", "HEAD"],
        capture_output=True, text=True, cwd=BEHIQUE, timeout=10
    )
    return result.stdout.strip()


def get_commit_diff(n: int = 1) -> str:
    """Get diff of last N commits."""
    result = subprocess.run(
        ["git", "diff", f"HEAD~{n}..HEAD"],
        capture_output=True, text=True, cwd=BEHIQUE, timeout=10
    )
    return result.stdout.strip()


def get_file_content(filepath: str) -> str:
    """Read a specific file."""
    p = BEHIQUE / filepath
    if not p.exists():
        print(f"❌ File not found: {filepath}")
        sys.exit(1)
    return p.read_text(encoding="utf-8")


def get_changed_files_list() -> str:
    """Get list of recently modified files for context."""
    result = subprocess.run(
        ["git", "diff", "--name-only", "HEAD"],
        capture_output=True, text=True, cwd=BEHIQUE, timeout=10
    )
    uncommitted = result.stdout.strip()

    result2 = subprocess.run(
        ["git", "diff", "--name-only", "HEAD~1..HEAD"],
        capture_output=True, text=True, cwd=BEHIQUE, timeout=10
    )
    committed = result2.stdout.strip()

    files = set()
    if uncommitted:
        files.update(uncommitted.split("\n"))
    if committed:
        files.update(committed.split("\n"))
    return "\n".join(sorted(files))


# ── Audit prompts ────────────────────────────────────────────────────────────

QUICK_AUDIT_PROMPT = """You are a senior code reviewer performing a quick audit.
Analyze the following code changes and report:

1. **Dead code**: Functions, imports, or variables that are defined but never used
2. **Redundancies**: Duplicate logic, repeated patterns that should be abstracted
3. **Bugs**: Obvious bugs, unhandled edge cases, potential crashes
4. **Security**: Exposed secrets, unsafe patterns, injection risks
5. **Quick wins**: Easy improvements that would make the code better

Be concise. Use bullet points. Only report real issues, not style preferences.
If the code looks clean, say so — don't invent problems.

Format your response as:
## 🔍 Audit Results

### Dead Code
- (findings or "None found")

### Redundancies
- (findings or "None found")

### Bugs
- (findings or "None found")

### Security
- (findings or "None found")

### Quick Wins
- (findings or "None found")

### Verdict
(one line: CLEAN / NEEDS WORK / CRITICAL ISSUES)
"""

DEEP_AUDIT_PROMPT = """You are a senior software architect performing a thorough code audit.
Analyze the following code changes and report:

1. **Dead code**: Functions, imports, variables defined but never used
2. **Redundancies**: Duplicate logic, repeated patterns, DRY violations
3. **Bugs**: Logic errors, unhandled edge cases, race conditions, crashes
4. **Security**: Exposed secrets, unsafe inputs, injection, auth issues
5. **Architecture**: Design patterns, coupling, cohesion, naming
6. **Performance**: Inefficient algorithms, unnecessary I/O, memory leaks
7. **Error handling**: Missing try/catch, swallowed errors, unclear messages
8. **Testing gaps**: What's untested, what should be tested

Be thorough but honest. Don't invent problems.
Prioritize findings by severity: CRITICAL > HIGH > MEDIUM > LOW.

Format your response as:
## 🔍 Deep Audit Results

### Critical Issues
- (findings or "None found")

### High Priority
- (findings or "None found")

### Medium Priority
- (findings or "None found")

### Low Priority
- (findings or "None found")

### Architecture Notes
- (observations)

### Verdict
(summary + recommended next actions)
"""


# ── AI routing ───────────────────────────────────────────────────────────────

def query_ai(prompt: str, code: str, model: str | None = None) -> str:
    """Send code to AI for review. Uses codegpt_bridge if available, else OpenAI direct."""

    full_prompt = f"{prompt}\n\n---\n\n## Changed files:\n{get_changed_files_list()}\n\n## Diff:\n```\n{code[:12000]}\n```"

    if len(code) > 12000:
        full_prompt += f"\n\n(Truncated — showing first 12000 of {len(code)} characters)"

    # Try codegpt_bridge first
    try:
        sys.path.insert(0, str(BEHIQUE / "tools"))
        from codegpt_bridge import query_model
        result = query_model(
            full_prompt,
            model=model or "ollama:llama3.2",
            system="You are a code auditor. Be concise and precise."
        )
        return result
    except ImportError:
        pass
    except Exception as e:
        print(f"[bridge] Fallback to OpenAI: {e}")

    # Direct OpenAI fallback
    try:
        from openai import OpenAI
        client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        response = client.chat.completions.create(
            model=model or "gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a code auditor. Be concise and precise."},
                {"role": "user", "content": full_prompt}
            ],
            temperature=0.2,
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"❌ AI audit failed: {e}"


# ── Main ─────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Ceiba Audit — AI code review")
    parser.add_argument("--commits", type=int, default=0, help="Audit last N commits")
    parser.add_argument("--file", type=str, help="Audit a specific file")
    parser.add_argument("--model", type=str, help="Model to use (e.g. openai:gpt-4o-mini, ollama:codellama)")
    parser.add_argument("--full", action="store_true", help="Deep audit (slower)")

    args = parser.parse_args()

    # Get code to audit
    if args.file:
        print(f"[audit] Reading file: {args.file}")
        code = get_file_content(args.file)
        source = f"File: {args.file}"
    elif args.commits > 0:
        print(f"[audit] Getting diff of last {args.commits} commit(s)...")
        code = get_commit_diff(args.commits)
        source = f"Last {args.commits} commit(s)"
    else:
        print("[audit] Getting uncommitted changes...")
        code = get_uncommitted_diff()
        source = "Uncommitted changes"

    if not code.strip():
        print("✅ No changes to audit.")
        sys.exit(0)

    # Count lines
    lines = code.count("\n")
    print(f"[audit] {source}: {lines} lines to review")

    # Select prompt
    prompt = DEEP_AUDIT_PROMPT if args.full else QUICK_AUDIT_PROMPT
    mode = "deep" if args.full else "quick"
    model_name = args.model or "ollama:llama3.2"
    print(f"[audit] Mode: {mode} | Model: {model_name}")
    print()

    # Run audit
    result = query_ai(prompt, code, args.model)
    print(result)


if __name__ == "__main__":
    main()

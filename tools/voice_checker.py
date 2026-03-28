#!/usr/bin/env python3
# Copyright 2026 Behike. All rights reserved.
"""
Voice Bible Checker. Scans any text file against the Voice Bible banned words
list. Reports violations with line numbers and suggested replacements.

Usage:
    python3 voice_checker.py FILE.md
    python3 voice_checker.py FILE.md --fix          # auto-replace banned words
    python3 voice_checker.py FILE.md --json          # output as JSON
    python3 voice_checker.py --check-text "some text" # check inline text
    python3 voice_checker.py --help

Returns exit code 0 if clean, 1 if violations found.
"""

import argparse
import json
import re
import sys
from pathlib import Path

# --- Paths ---
TOOLS_DIR = Path(__file__).parent
PROJECT_DIR = TOOLS_DIR.parent
VOICE_BIBLE = PROJECT_DIR / "Ceiba" / "VOICE_BIBLE.md"

# --- Banned words and replacements ---
# Hard-coded from Voice Bible so this tool works standalone without parsing markdown.
# Keep in sync with VOICE_BIBLE.md.

BANNED_PHRASES = {
    # Hard banned: phrase -> replacement (empty string means delete the phrase)
    "unlock your potential": "",
    "in today's fast-paced world": "",
    "let's dive in": "",
    "let's dive deep": "",
    "game-changer": "useful",
    "game-changing": "useful",
    "game changer": "useful",
    "leverage": "use",
    "leveraging": "using",
    "leveraged": "used",
    "elevate": "improve",
    "elevating": "improving",
    "streamline": "simplify",
    "streamlining": "simplifying",
    "revolutionize": "change",
    "revolutionizing": "changing",
    "cutting-edge": "new",
    "cutting edge": "new",
    "seamlessly": "smoothly",
    "seamless": "smooth",
    "robust": "solid",
    "harness the power of": "use",
    "take your": "improve your",
    "to the next level": "",
    "whether you're a beginner or expert": "",
    "whether you're a beginner or an expert": "",
    "look no further": "",
    "in this comprehensive guide": "",
    "without further ado": "",
    "it's important to note that": "",
    "it is important to note that": "",
    "at the end of the day": "",
    "moving forward": "",
    "excited to announce": "",
    "thrilled to share": "",
    "i'm passionate about": "",
    "on this journey": "",
    "pain points": "problems",
    "low-hanging fruit": "easy wins",
    "circle back": "revisit",
    "deep dive": "close look",
    "unpack": "explain",
    "landscape": "space",
    "paradigm shift": "change",
    "synergy": "teamwork",
    "empower": "help",
    "empowering": "helping",
    "empowered": "helped",
}

# Soft banned: flag but don't auto-replace
SOFT_BANNED = [
    "here's the thing",
    "the truth is",
    "most people don't realize",
    "what if i told you",
]

# Em dash detection
EM_DASH_CHARS = ["\u2014", "\u2013"]


def load_voice_bible_banned() -> dict:
    """Load banned words from VOICE_BIBLE.md if it exists, for validation."""
    # We use the hardcoded list above as primary. This function can be used
    # to verify the lists stay in sync.
    return BANNED_PHRASES


def check_text(text: str) -> list:
    """
    Check text against banned words and phrases.
    Returns list of violations: [{"line": int, "phrase": str, "replacement": str, "severity": str}]
    """
    violations = []
    lines = text.split("\n")

    for line_num, line in enumerate(lines, 1):
        line_lower = line.lower()

        # Check hard banned phrases
        for phrase, replacement in BANNED_PHRASES.items():
            if phrase in line_lower:
                violations.append({
                    "line": line_num,
                    "phrase": phrase,
                    "replacement": replacement if replacement else "[delete]",
                    "severity": "hard",
                    "context": line.strip()[:100],
                })

        # Check soft banned phrases
        for phrase in SOFT_BANNED:
            if phrase in line_lower:
                violations.append({
                    "line": line_num,
                    "phrase": phrase,
                    "replacement": "[consider removing]",
                    "severity": "soft",
                    "context": line.strip()[:100],
                })

        # Check em dashes
        for dash in EM_DASH_CHARS:
            if dash in line:
                violations.append({
                    "line": line_num,
                    "phrase": "em dash" if dash == "\u2014" else "en dash",
                    "replacement": ". or ,",
                    "severity": "hard",
                    "context": line.strip()[:100],
                })

    return violations


def fix_text(text: str) -> tuple:
    """
    Auto-replace banned words in text.
    Returns (fixed_text, list_of_changes).
    """
    changes = []
    fixed = text

    # Replace em/en dashes first
    for dash in EM_DASH_CHARS:
        if dash in fixed:
            count = fixed.count(dash)
            fixed = fixed.replace(dash, ".")
            changes.append({"phrase": "em/en dash", "replacement": ".", "count": count})

    # Clean up double periods from dash replacement
    while ".." in fixed:
        fixed = fixed.replace("..", ".")

    # Replace banned phrases (case-insensitive)
    for phrase, replacement in BANNED_PHRASES.items():
        # Build a case-insensitive pattern
        pattern = re.compile(re.escape(phrase), re.IGNORECASE)
        matches = pattern.findall(fixed)
        if matches:
            fixed = pattern.sub(replacement, fixed)
            changes.append({
                "phrase": phrase,
                "replacement": replacement if replacement else "[deleted]",
                "count": len(matches),
            })

    # Clean up double spaces from deletions
    fixed = re.sub(r"  +", " ", fixed)
    # Clean up lines that are just whitespace after deletions
    fixed = re.sub(r"\n +\n", "\n\n", fixed)

    return fixed, changes


def check_file(filepath: str) -> list:
    """Check a file for Voice Bible violations. Returns violations list."""
    path = Path(filepath)
    if not path.exists():
        print(f"[ERROR] File not found: {filepath}")
        sys.exit(1)

    text = path.read_text(encoding="utf-8", errors="replace")
    return check_text(text)


def fix_file(filepath: str) -> tuple:
    """Fix a file in place. Returns (violations_before, changes_made)."""
    path = Path(filepath)
    if not path.exists():
        print(f"[ERROR] File not found: {filepath}")
        sys.exit(1)

    text = path.read_text(encoding="utf-8", errors="replace")
    violations_before = check_text(text)

    fixed, changes = fix_text(text)

    if changes:
        path.write_text(fixed, encoding="utf-8")

    return violations_before, changes


def print_report(filepath: str, violations: list):
    """Print a human-readable violation report."""
    if not violations:
        print(f"\n  VOICE CHECK: {filepath}")
        print(f"  Result: CLEAN. No violations found.")
        print()
        return

    hard = [v for v in violations if v["severity"] == "hard"]
    soft = [v for v in violations if v["severity"] == "soft"]

    print(f"\n  VOICE CHECK: {filepath}")
    print(f"  ={'=' * 55}")
    print(f"  Violations: {len(violations)} ({len(hard)} hard, {len(soft)} soft)")
    print()

    if hard:
        print(f"  HARD BANNED (must fix):")
        for v in hard:
            print(f"    Line {v['line']:4d}: \"{v['phrase']}\" -> {v['replacement']}")
            print(f"             {v['context']}")
        print()

    if soft:
        print(f"  SOFT BANNED (review):")
        for v in soft:
            print(f"    Line {v['line']:4d}: \"{v['phrase']}\"")
            print(f"             {v['context']}")
        print()

    print(f"  Fix with: python3 voice_checker.py {filepath} --fix")
    print(f"  ={'=' * 55}")
    print()


def main():
    parser = argparse.ArgumentParser(
        description="Voice Bible Checker. Scan text for banned words and AI-sounding phrases. Copyright 2026 Behike."
    )
    parser.add_argument("file", nargs="?", help="File to check")
    parser.add_argument("--fix", action="store_true", help="Auto-replace banned words in place")
    parser.add_argument("--json", action="store_true", help="Output results as JSON")
    parser.add_argument("--check-text", type=str, help="Check inline text instead of a file")
    parser.add_argument("--quiet", action="store_true", help="Only output if violations found")

    args = parser.parse_args()

    if args.check_text:
        violations = check_text(args.check_text)
        if args.json:
            print(json.dumps({"violations": violations, "count": len(violations)}, indent=2))
        else:
            if violations:
                print(f"  Found {len(violations)} violations:")
                for v in violations:
                    print(f"    [{v['severity']}] \"{v['phrase']}\" -> {v['replacement']}")
            else:
                if not args.quiet:
                    print("  Clean. No violations.")
        sys.exit(1 if violations else 0)

    if not args.file:
        parser.print_help()
        sys.exit(1)

    if args.fix:
        violations_before, changes = fix_file(args.file)
        if args.json:
            print(json.dumps({
                "file": args.file,
                "violations_before": len(violations_before),
                "changes": changes,
            }, indent=2))
        else:
            if changes:
                print(f"\n  VOICE FIX: {args.file}")
                print(f"  Changes made:")
                for c in changes:
                    print(f"    \"{c['phrase']}\" -> \"{c['replacement']}\" ({c['count']}x)")
                print(f"  Total: {sum(c['count'] for c in changes)} replacements")
                print()
            else:
                if not args.quiet:
                    print(f"  No changes needed in {args.file}")
        sys.exit(0)

    # Default: check and report
    violations = check_file(args.file)

    if args.json:
        print(json.dumps({
            "file": args.file,
            "violations": violations,
            "count": len(violations),
            "hard": len([v for v in violations if v["severity"] == "hard"]),
            "soft": len([v for v in violations if v["severity"] == "soft"]),
        }, indent=2))
    else:
        if violations or not args.quiet:
            print_report(args.file, violations)

    sys.exit(1 if violations else 0)


if __name__ == "__main__":
    main()

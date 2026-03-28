"""
idea_splitter.py -- Split a single message into multiple discrete ideas.

Uses heuristic patterns first (numbered lists, separator words, paragraph breaks).
Falls back to treating the whole message as a single idea if nothing splits.
No LLM call needed for Phase 1. Pure heuristics, fast and free.
"""

import re
import logging

logger = logging.getLogger(__name__)


# Words/phrases that signal a new idea within a sentence or paragraph.
SPLIT_PHRASES = [
    r"\balso\b",
    r"\banother thing\b",
    r"\boh and\b",
    r"\bplus\b",
    r"\bbtw\b",
    r"\bby the way\b",
    r"\band also\b",
    r"\bon another note\b",
    r"\bseparately\b",
    r"\bone more thing\b",
    r"\badditionally\b",
]

# Compiled pattern that matches any split phrase (case-insensitive)
_SPLIT_PATTERN = re.compile(
    r"(?:,\s*|\.\s+|\s+)(?:" + "|".join(SPLIT_PHRASES) + r")[\s,:]",
    re.IGNORECASE,
)

# Numbered list pattern: "1. something", "1) something", "- something", "* something"
_NUMBERED_LIST = re.compile(r"^\s*(?:\d+[.)]\s+|[-*]\s+)", re.MULTILINE)


def split_ideas(text: str) -> list[str]:
    """
    Take raw text (typed or transcribed voice) and split into individual ideas.

    Returns a list of cleaned idea strings. Always returns at least one idea.

    Splitting strategy (in priority order):
    1. Numbered/bulleted lists
    2. Double newline paragraph breaks
    3. Separator phrases ("also", "btw", "another thing", etc.)
    4. No split found: return the whole message as one idea
    """
    text = text.strip()
    if not text:
        return []

    # Strategy 1: Numbered or bulleted list
    ideas = _try_numbered_list(text)
    if ideas and len(ideas) > 1:
        logger.info(f"Splitter: numbered list detected, {len(ideas)} ideas")
        return ideas

    # Strategy 2: Double newline paragraph breaks
    ideas = _try_paragraph_split(text)
    if ideas and len(ideas) > 1:
        logger.info(f"Splitter: paragraph split, {len(ideas)} ideas")
        return ideas

    # Strategy 3: Separator phrases
    ideas = _try_phrase_split(text)
    if ideas and len(ideas) > 1:
        logger.info(f"Splitter: phrase split, {len(ideas)} ideas")
        return ideas

    # No split detected. Single idea.
    logger.info("Splitter: single idea (no split detected)")
    return [text]


def _try_numbered_list(text: str) -> list[str]:
    """Split on numbered/bulleted list items."""
    matches = list(_NUMBERED_LIST.finditer(text))
    if len(matches) < 2:
        return []

    ideas = []
    for i, match in enumerate(matches):
        start = match.end()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        idea = text[start:end].strip()
        # Clean trailing punctuation artifacts
        idea = idea.rstrip(",;")
        if idea:
            ideas.append(idea)

    return ideas


def _try_paragraph_split(text: str) -> list[str]:
    """Split on double newlines (paragraph breaks)."""
    paragraphs = re.split(r"\n\s*\n", text)
    ideas = [p.strip() for p in paragraphs if p.strip()]
    return ideas


def _try_phrase_split(text: str) -> list[str]:
    """Split on separator phrases like 'also', 'btw', 'another thing'."""
    matches = list(_SPLIT_PATTERN.finditer(text))
    if not matches:
        return []

    ideas = []

    # First chunk: everything before the first split phrase
    first = text[:matches[0].start()].strip().rstrip(",;")
    if first:
        ideas.append(first)

    # Middle and last chunks: everything after each split phrase, up to the next one
    for i, match in enumerate(matches):
        start = match.end()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        chunk = text[start:end].strip().rstrip(",;")
        # Strip trailing conjunctions left over from splitting
        chunk = re.sub(r"\s+and\s*$", "", chunk, flags=re.IGNORECASE).strip()
        if chunk:
            ideas.append(chunk)

    return ideas


# ---- Self-test ----
if __name__ == "__main__":
    tests = [
        (
            "I want to make a meditation app and also a music studio and btw we should add a habit tracker to the website",
            3,
        ),
        (
            "1. Build the landing page\n2. Set up Stripe\n3. Write the copy",
            3,
        ),
        (
            "Update on the meditation app: added breathing exercises",
            1,
        ),
        (
            "First idea here.\n\nSecond completely different idea.\n\nThird one too.",
            3,
        ),
        (
            "Just one single thought about eBay listings",
            1,
        ),
    ]

    for text, expected in tests:
        result = split_ideas(text)
        status = "PASS" if len(result) == expected else "FAIL"
        print(f"[{status}] Expected {expected}, got {len(result)}: {result}")

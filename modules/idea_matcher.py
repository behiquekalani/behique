"""
idea_matcher.py -- Match a new idea against recent ideas using keyword similarity.

No LLM call. Uses Jaccard similarity on extracted keywords.
Fast, free, and deterministic. Falls back gracefully.
"""

import re
import logging
from modules.memory import load_entries

logger = logging.getLogger(__name__)

# Similarity threshold. Above this, we consider it an update to an existing idea.
MATCH_THRESHOLD = 0.4

# Common stop words to ignore when comparing ideas
STOP_WORDS = {
    "i", "me", "my", "we", "our", "you", "your", "the", "a", "an", "is", "are",
    "was", "were", "be", "been", "being", "have", "has", "had", "do", "does",
    "did", "will", "would", "could", "should", "may", "might", "can", "shall",
    "to", "of", "in", "for", "on", "with", "at", "by", "from", "as", "into",
    "about", "like", "through", "after", "before", "between", "out", "up",
    "down", "off", "over", "under", "again", "further", "then", "once",
    "and", "but", "or", "nor", "not", "so", "yet", "both", "either", "neither",
    "each", "every", "all", "any", "few", "more", "most", "other", "some",
    "such", "no", "only", "own", "same", "than", "too", "very",
    "it", "its", "this", "that", "these", "those", "there", "here",
    "what", "which", "who", "whom", "when", "where", "why", "how",
    "also", "just", "want", "need", "thing", "things", "something",
    "going", "make", "made", "get", "got", "think", "know", "really",
    "still", "even", "much", "many", "well", "back", "way",
}

# Words that signal this is an update, not a new idea
UPDATE_SIGNAL_WORDS = {
    "update", "updated", "updating", "progress", "changed", "change",
    "added", "adding", "fixed", "fixing", "finished", "done", "completed",
    "modified", "built", "building", "working", "worked",
    "correction", "actually", "instead", "nevermind",
}


def extract_keywords(text: str) -> set[str]:
    """Extract meaningful keywords from text, removing stop words."""
    # Lowercase, split on non-alphanumeric
    words = re.findall(r"[a-z0-9]+", text.lower())
    # Remove stop words and very short words
    return {w for w in words if w not in STOP_WORDS and len(w) > 2}


def jaccard_similarity(set_a: set, set_b: set) -> float:
    """Jaccard similarity: intersection / union. Returns 0.0 to 1.0."""
    if not set_a or not set_b:
        return 0.0
    intersection = set_a & set_b
    union = set_a | set_b
    return len(intersection) / len(union)


def has_update_signals(text: str) -> bool:
    """Check if the text contains words that suggest it's an update to something."""
    words = set(re.findall(r"[a-z]+", text.lower()))
    return bool(words & UPDATE_SIGNAL_WORDS)


def match_idea(user_id: str, idea_text: str, max_recent: int = 50) -> dict:
    """
    Compare a new idea against recent entries for the user.

    Returns:
        {
            "is_update": bool,
            "matched_id": str or None,
            "matched_seed": str or None,
            "similarity": float
        }
    """
    entries = load_entries()
    user_entries = [e for e in entries if e.get("user_id") == user_id]

    if not user_entries:
        return {"is_update": False, "matched_id": None, "matched_seed": None, "similarity": 0.0}

    # Only check the most recent entries
    recent = user_entries[-max_recent:]

    idea_keywords = extract_keywords(idea_text)
    if not idea_keywords:
        return {"is_update": False, "matched_id": None, "matched_seed": None, "similarity": 0.0}

    # Check if the text has update signal words. If so, lower the threshold.
    is_update_signal = has_update_signals(idea_text)
    threshold = MATCH_THRESHOLD * 0.7 if is_update_signal else MATCH_THRESHOLD

    best_match = None
    best_similarity = 0.0

    for entry in recent:
        # Compare against the seed text and all update texts
        entry_text = entry.get("seed", "")
        for update in entry.get("updates", []):
            entry_text += " " + update.get("text", "")

        # Also include tags and summary from classification
        classification = entry.get("classification", {})
        entry_text += " " + classification.get("summary", "")
        entry_text += " " + " ".join(entry.get("tags", []))

        entry_keywords = extract_keywords(entry_text)
        similarity = jaccard_similarity(idea_keywords, entry_keywords)

        if similarity > best_similarity:
            best_similarity = similarity
            best_match = entry

    if best_similarity >= threshold and best_match:
        logger.info(
            f"Matcher: matched idea to entry {best_match['id'][:8]} "
            f"(similarity={best_similarity:.2f}, threshold={threshold:.2f})"
        )
        return {
            "is_update": True,
            "matched_id": best_match["id"],
            "matched_seed": best_match.get("seed", "")[:80],
            "similarity": best_similarity,
        }

    logger.info(f"Matcher: no match found (best similarity={best_similarity:.2f}, threshold={threshold:.2f})")
    return {"is_update": False, "matched_id": None, "matched_seed": None, "similarity": best_similarity}


# ---- Self-test ----
if __name__ == "__main__":
    # Quick keyword extraction test
    text1 = "I want to build a meditation app with breathing exercises"
    text2 = "Update on the meditation app: added breathing exercises"

    kw1 = extract_keywords(text1)
    kw2 = extract_keywords(text2)
    sim = jaccard_similarity(kw1, kw2)

    print(f"Keywords 1: {kw1}")
    print(f"Keywords 2: {kw2}")
    print(f"Jaccard similarity: {sim:.2f}")
    print(f"Has update signals: {has_update_signals(text2)}")
    print(f"Would match (threshold {MATCH_THRESHOLD}): {sim >= MATCH_THRESHOLD}")

"""
Cross-store product matching.
Normalizes product names for deduplication and fuzzy matching.

Steps:
1. Lowercase
2. Remove brand names (configurable stoplist)
3. Remove filler words
4. Sort remaining tokens alphabetically -> fingerprint
5. Use rapidfuzz for fuzzy matching (threshold from config)
"""

import re
import logging
from rapidfuzz import fuzz

logger = logging.getLogger(__name__)


class ProductNormalizer:

    def __init__(self, config):
        self.brands = set(config["normalizer"]["brand_stoplist"])
        self.fillers = set(config["normalizer"]["filler_words"])
        self.threshold = config["normalizer"]["fuzzy_threshold"]

    def normalize(self, name: str) -> str:
        text = name.lower()
        # Extract only alphanumeric tokens
        tokens = re.findall(r"[a-z0-9]+", text)
        # Remove brands and fillers
        tokens = [t for t in tokens if t not in self.brands and t not in self.fillers]
        # Sort for fingerprint consistency
        tokens.sort()
        return " ".join(tokens)

    def is_match(self, name_a: str, name_b: str) -> bool:
        score = fuzz.token_sort_ratio(name_a, name_b)
        return score >= self.threshold

    def match_score(self, name_a: str, name_b: str) -> float:
        return fuzz.token_sort_ratio(name_a, name_b)

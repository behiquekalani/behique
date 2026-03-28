#!/usr/bin/env python3
"""
trends_scorer.py — Google Trends Product Scorer v3
Post-processor for Apify Google Trends scraper output.

Replaces trends_scraper.py (790 lines) with Apify data fetching + this scoring logic.
The scraping is handled by Apify actor `apify/google-trends-scraper`.
This file only does: trend classification, product viability scoring, and ranking.

Usage:
    # Score results from an Apify run (JSON file)
    python trends_scorer.py --input apify_output.json

    # Score results from stdin (pipe from Apify CLI)
    cat apify_output.json | python trends_scorer.py

    # Generate Apify input configs for seed keywords
    python trends_scorer.py --generate-input
    python trends_scorer.py --generate-input --category electronics
    python trends_scorer.py --generate-input --seed "air fryer"

Output:
    ~/behique/output/scored_trends_YYYY-MM-DD.json
    ~/behique/output/top_picks_YYYY-MM-DD.txt
"""

import json
import sys
import argparse
from datetime import datetime
from pathlib import Path

OUTPUT_DIR = Path.home() / "behique" / "output"

# ── SEED CATEGORIES (from v2) ────────────────────────────────────────────────

CATEGORIES = {
    "electronics": [
        "wireless earbuds", "phone stand", "LED strip lights", "portable charger",
        "ring light", "smart watch", "phone case", "laptop stand", "webcam",
        "bluetooth speaker", "USB hub", "wireless mouse", "screen protector",
        "power bank", "cable organizer",
    ],
    "home": [
        "air purifier", "humidifier", "storage organizer", "desk lamp",
        "shower curtain", "candle holder", "wall art", "throw pillow",
        "bookshelf decor", "plant pots", "cable management", "drawer organizer",
        "aromatherapy diffuser", "LED mirror", "floating shelf",
    ],
    "kitchen": [
        "air fryer accessories", "coffee accessories", "reusable bags",
        "food container", "water bottle", "lunch box", "kitchen gadgets",
        "ice maker", "spice rack", "cutting board", "blender accessories",
        "coffee mug", "tumbler cup", "meal prep containers", "kitchen timer",
    ],
    "beauty_health": [
        "facial roller", "hair clips", "makeup organizer", "skincare fridge",
        "LED face mask", "massage gun", "teeth whitening", "nail art",
        "hair growth", "essential oils", "beard grooming kit", "lip balm",
    ],
    "fitness": [
        "resistance bands", "yoga mat", "jump rope", "foam roller",
        "gym bag", "protein shaker", "wrist wraps", "pull up bar",
        "ankle weights", "ab roller",
    ],
    "kids_pets": [
        "dog toy", "cat tree", "baby monitor", "kids tablet",
        "pet camera", "dog harness", "baby carrier", "toddler toys",
        "pet bed", "fish tank accessories",
    ],
    "fashion": [
        "crossbody bag", "baseball cap", "sunglasses", "tote bag",
        "minimalist wallet", "watch band", "beanie", "socks",
        "fanny pack", "jewelry organizer",
    ],
    "seasonal_viral": [
        "stanley cup", "emotional support water bottle", "cloud couch",
        "sunset lamp", "mushroom decor", "sensory toys", "mini projector",
        "portable fan", "ice bath tub", "under desk treadmill",
    ],
}

SEED_PATTERNS = [
    "fix {}", "replacement {}", "best {} for",
    "how to clean {}", "{} accessories", "{} parts",
]

# ── SCORING LOGIC (preserved from v2) ────────────────────────────────────────

VIABILITY_KEYWORDS = [
    "replacement", "parts", "cleaner", "kit", "filter",
    "accessories", "case", "cover", "charger", "organizer",
    "set", "bundle", "premium", "pro", "upgraded", "custom",
    "holder", "mount", "stand", "bracket", "adapter",
]

LOW_VALUE_SIGNALS = [
    "free", "cheap", "diy", "how to", "tutorial", "review", "vs",
    "meaning", "definition", "reddit", "wiki",
]


def classify_trend(timeline_data):
    """
    Classify trend from Apify timeline values.
    Input: list of {'value': int, ...} from Apify interest_over_time.
    Returns: spike, emerging, seasonal, or stable.
    """
    if not timeline_data or len(timeline_data) < 4:
        return "stable"

    values = [p.get("value", 0) for p in timeline_data if isinstance(p, dict)]
    if not values or len(values) < 4:
        return "stable"

    mean_val = sum(values) / len(values) if values else 0
    mid = len(values) // 2
    first_half = values[:mid]
    second_half = values[mid:]

    first_avg = sum(first_half) / len(first_half) if first_half else 1
    second_avg = sum(second_half) / len(second_half) if second_half else 0

    # Spike: recent half is 2x+ the first half
    if first_avg > 0 and second_avg > 2 * first_avg:
        return "spike"

    # Emerging: positive slope
    if first_avg > 0 and second_avg > first_avg * 1.2:
        return "emerging"

    # Seasonal: high variance
    if mean_val > 0:
        variance = sum((v - mean_val) ** 2 for v in values) / len(values)
        std = variance ** 0.5
        if std / mean_val > 0.5:
            return "seasonal"

    return "stable"


def compute_velocity(timeline_data):
    """Ratio of recent vs older trend values. >1 = accelerating."""
    if not timeline_data:
        return 0.5
    values = [p.get("value", 0) for p in timeline_data if isinstance(p, dict)]
    if len(values) < 4:
        return 0.5
    mid = len(values) // 2
    prev_avg = sum(values[:mid]) / len(values[:mid])
    recent_avg = sum(values[mid:]) / len(values[mid:])
    return recent_avg / prev_avg if prev_avg > 0 else 0.5


def compute_volume(timeline_data):
    """Mean interest value as volume proxy."""
    if not timeline_data:
        return 0
    values = [p.get("value", 0) for p in timeline_data if isinstance(p, dict)]
    return sum(values) / len(values) if values else 0


def compute_specificity(query):
    """More words = more niche = higher specificity."""
    words = len(query.split())
    if words >= 4:
        return 1.0
    elif words == 3:
        return 0.8
    elif words == 2:
        return 0.5
    return 0.2


def compute_product_viability(query):
    """Heuristic: does the query look like a buyable product?"""
    q = query.lower()
    score = 0.3

    for signal in VIABILITY_KEYWORDS:
        if signal in q:
            score += 0.15

    for signal in LOW_VALUE_SIGNALS:
        if signal in q:
            score -= 0.2

    if any(c.isdigit() for c in q):
        score += 0.1
    if any(color in q for color in ["black", "white", "pink", "blue", "red", "green"]):
        score += 0.05

    return max(0.0, min(1.0, score))


def normalize(value, min_val, max_val):
    if max_val == min_val:
        return 0.5
    return max(0.0, min(1.0, (value - min_val) / (max_val - min_val)))


def score_results(results):
    """
    Score = velocity * 0.35 + volume * 0.25 + viability * 0.25 + specificity * 0.15
    """
    if not results:
        return results

    velocities = [r["velocity"] for r in results]
    volumes = [r["volume"] for r in results]

    vel_min, vel_max = min(velocities), max(velocities)
    vol_min, vol_max = min(volumes), max(volumes)

    for r in results:
        vel_norm = normalize(r["velocity"], vel_min, vel_max)
        vol_norm = normalize(r["volume"], vol_min, vol_max)

        r["score"] = round(
            vel_norm * 0.35 +
            vol_norm * 0.25 +
            r["viability"] * 0.25 +
            r["specificity"] * 0.15,
            4,
        )

    return sorted(results, key=lambda x: x["score"], reverse=True)


# ── APIFY OUTPUT PARSER ──────────────────────────────────────────────────────

def parse_apify_output(data):
    """
    Parse Apify google-trends-scraper output into scorable results.
    Each item has: searchTerm, interestOverTime, relatedQueries, relatedTopics.
    """
    results = []

    for item in data:
        keyword = item.get("searchTerm", item.get("term", "unknown"))
        timeline = item.get("interestOverTime", [])

        result = {
            "keyword": keyword,
            "trend_type": classify_trend(timeline),
            "velocity": compute_velocity(timeline),
            "volume": compute_volume(timeline),
            "specificity": compute_specificity(keyword),
            "viability": compute_product_viability(keyword),
        }

        # Extract related queries (rising ones are gold for product ideas)
        rising = item.get("relatedQueries", {}).get("rising", [])
        if isinstance(rising, list):
            result["rising_queries"] = [
                q.get("query", q) if isinstance(q, dict) else q
                for q in rising[:8]
            ]

        results.append(result)

    return results


# ── APIFY INPUT GENERATOR ────────────────────────────────────────────────────

def generate_apify_input(category=None, seed=None, geo="US"):
    """
    Generate input config for apify/google-trends-scraper.
    Use this to create the Apify run input from Ceiba.
    """
    if seed:
        keywords = [seed] + [p.format(seed) for p in SEED_PATTERNS]
    elif category and category in CATEGORIES:
        keywords = CATEGORIES[category]
    else:
        keywords = []
        for cat_keywords in CATEGORIES.values():
            keywords.extend(cat_keywords)

    return {
        "searchTerms": keywords,
        "timeRange": "past12Months",
        "geo": geo,
        "isMultiple": False,
        "maxItems": len(keywords),
        "extendOutputFunction": "",
    }


# ── OUTPUT ────────────────────────────────────────────────────────────────────

def write_output(scored, prefix="scored_trends"):
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    date_str = datetime.now().strftime("%Y-%m-%d")

    json_path = OUTPUT_DIR / f"{prefix}_{date_str}.json"
    json_path.write_text(json.dumps(scored, indent=2))

    txt_path = OUTPUT_DIR / f"top_picks_{date_str}.txt"
    lines = [f"Top Product Trends — {date_str}\n{'=' * 50}\n"]
    for i, r in enumerate(scored[:25], 1):
        lines.append(
            f"{i:2d}. [{r['trend_type']:9s}] {r['keyword']:<40s} "
            f"score={r['score']:.3f}  vel={r['velocity']:.2f}  "
            f"vol={r['volume']:.1f}  viab={r['viability']:.2f}"
        )
        if r.get("rising_queries"):
            lines.append(f"     Rising: {', '.join(r['rising_queries'][:4])}")
    txt_path.write_text("\n".join(lines))

    print(f"Saved: {json_path}")
    print(f"Saved: {txt_path}")
    return json_path, txt_path


# ── CLI ───────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Score Google Trends data from Apify")
    parser.add_argument("--input", "-i", help="Apify output JSON file")
    parser.add_argument("--generate-input", action="store_true",
                        help="Generate Apify actor input config instead of scoring")
    parser.add_argument("--category", "-c", help="Category for input generation")
    parser.add_argument("--seed", "-s", help="Seed keyword for expansion")
    parser.add_argument("--geo", default="US", help="Geo target (default: US)")
    args = parser.parse_args()

    if args.generate_input:
        config = generate_apify_input(args.category, args.seed, args.geo)
        print(json.dumps(config, indent=2))
        print(f"\n# {len(config['searchTerms'])} keywords ready for Apify")
        print(f"# Estimated cost: ${len(config['searchTerms']) * 0.003:.2f} (free tier)")
        return

    # Score mode: read from file or stdin
    if args.input:
        data = json.loads(Path(args.input).read_text())
    else:
        data = json.loads(sys.stdin.read())

    results = parse_apify_output(data)
    scored = score_results(results)
    write_output(scored)

    print(f"\nScored {len(scored)} keywords. Top 5:")
    for i, r in enumerate(scored[:5], 1):
        print(f"  {i}. {r['keyword']} — {r['trend_type']} (score: {r['score']:.3f})")


if __name__ == "__main__":
    main()

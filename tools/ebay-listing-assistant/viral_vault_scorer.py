#!/usr/bin/env python3
"""
Viral Vault Product Scoring Tool
15-point scoring methodology adapted for eBay/dropshipping product evaluation.

This scoring system is available as part of The Ecommerce Playbook ($14.99)

Usage:
    python3 viral_vault_scorer.py              # Interactive scoring
    python3 viral_vault_scorer.py --list        # Show all scored products
    python3 viral_vault_scorer.py --compare     # Side-by-side top 5 comparison
"""

import argparse
import json
import os
import sys
from datetime import datetime
from pathlib import Path

SCORES_FILE = Path(__file__).parent / "product_scores.json"

CRITERIA = [
    {
        "name": "Wow Factor",
        "question": "Does it make people stop scrolling?",
        "tip": "Think: would someone share this in a group chat? If yes, that's a 4-5.",
    },
    {
        "name": "Problem Solving",
        "question": "Does it solve a real problem?",
        "tip": "Pain points sell. 'Nice to have' = 2-3. 'Need this now' = 5.",
    },
    {
        "name": "Broad Appeal",
        "question": "Would most adults want this?",
        "tip": "Niche = 1-2. Gender-specific = 3. Universal = 5.",
    },
    {
        "name": "Impulse Buy Price",
        "question": "Is it under $30 retail?",
        "tip": "$10-20 sweet spot = 5. $20-30 = 4. $30-50 = 2. Over $50 = 1.",
    },
    {
        "name": "Hard to Find Locally",
        "question": "Can't buy at Walmart or Target?",
        "tip": "Available everywhere = 1. Specialty only = 4. Online-only = 5.",
    },
    {
        "name": "Profit Margin",
        "question": "Is a 3x markup possible?",
        "tip": "Cost $5, sell $15+ = 5. Cost $10, sell $20 = 3. Thin margins = 1.",
    },
    {
        "name": "Lightweight / Shippable",
        "question": "Under 2 lbs and easy to pack?",
        "tip": "Fits in a padded envelope = 5. Needs a box = 3. Oversized = 1.",
    },
    {
        "name": "Not Seasonal",
        "question": "Does it sell year-round?",
        "tip": "Christmas-only = 1. Summer-heavy = 3. Evergreen = 5.",
    },
    {
        "name": "Not Fragile",
        "question": "Will it survive shipping without breaking?",
        "tip": "Glass/ceramic = 1. Electronics = 3. Silicone/plastic/fabric = 5.",
    },
    {
        "name": "No Brand Dominance",
        "question": "Do Nike/Apple/etc own this category?",
        "tip": "Brand-dominated = 1. Some brands = 3. Generic/unbranded = 5.",
    },
    {
        "name": "Visual / Demonstrable",
        "question": "Easy to show in a video or photo?",
        "tip": "Before/after works = 5. Looks cool in use = 4. Boring to show = 1.",
    },
    {
        "name": "Low Competition",
        "question": "Under 500 eBay listings for this product?",
        "tip": "Under 100 = 5. 100-500 = 4. 500-2000 = 2. Over 2000 = 1.",
    },
    {
        "name": "Trending Up",
        "question": "Is Google Trends showing growth?",
        "tip": "Sharp uptrend = 5. Steady = 3. Declining = 1. Check trends.google.com.",
    },
    {
        "name": "Repeat Purchase",
        "question": "Will they buy again or buy refills?",
        "tip": "Consumable/refillable = 5. Might buy another color = 3. One and done = 1.",
    },
    {
        "name": "Cross-sell Potential",
        "question": "Can you bundle related products?",
        "tip": "Natural accessories exist = 5. Kinda related = 3. Standalone = 1.",
    },
]


def color(text: str, code: str) -> str:
    """Apply ANSI color if terminal supports it."""
    if not sys.stdout.isatty():
        return text
    colors = {
        "green": "\033[92m",
        "yellow": "\033[93m",
        "red": "\033[91m",
        "bold": "\033[1m",
        "dim": "\033[2m",
        "reset": "\033[0m",
        "cyan": "\033[96m",
    }
    return f"{colors.get(code, '')}{text}{colors.get('reset', '')}"


def get_rating_color(score: int) -> str:
    """Return color code based on individual criterion score."""
    if score >= 4:
        return "green"
    if score >= 3:
        return "yellow"
    return "red"


def get_verdict(total: int) -> tuple[str, str, str]:
    """Return (verdict, color, emoji-free label) based on total score."""
    if total >= 60:
        return "STRONG BUY. List this product.", "green", "GO"
    if total >= 40:
        return "Worth testing. Run a small batch first.", "yellow", "TEST"
    return "Skip. Too many red flags.", "red", "PASS"


def load_scores() -> list[dict]:
    """Load saved product scores from JSON."""
    if not SCORES_FILE.exists():
        return []
    try:
        with open(SCORES_FILE, "r") as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return []


def save_score(entry: dict) -> None:
    """Append a scored product to the JSON file."""
    scores = load_scores()
    scores.append(entry)
    with open(SCORES_FILE, "w") as f:
        json.dump(scores, f, indent=2)


def interactive_score() -> None:
    """Run the interactive scoring session."""
    print()
    print(color("=" * 60, "bold"))
    print(color("  Viral Vault Product Scorer", "bold"))
    print(color("  15-Point Methodology for Dropshipping", "dim"))
    print(color("=" * 60, "bold"))
    print()

    product_name = input("  Product name: ").strip()
    if not product_name:
        print("  No product name entered. Exiting.")
        return

    source_url = input("  Source URL (optional): ").strip()
    cost_price = input("  Cost price $ (optional): ").strip()
    print()

    print(color("  Rate each criterion from 1 (worst) to 5 (best).", "dim"))
    print(color("  Press Enter to skip (defaults to 3).", "dim"))
    print()

    scores = {}
    running_total = 0

    for i, criterion in enumerate(CRITERIA, 1):
        print(f"  {color(f'[{i}/15]', 'cyan')} {color(criterion['name'], 'bold')}")
        print(f"         {criterion['question']}")
        print(f"         {color(criterion['tip'], 'dim')}")

        while True:
            raw = input(f"         Score (1-5): ").strip()
            if raw == "":
                score = 3
                break
            try:
                score = int(raw)
                if 1 <= score <= 5:
                    break
                print("         Enter a number between 1 and 5.")
            except ValueError:
                print("         Enter a number between 1 and 5.")

        scores[criterion["name"]] = score
        running_total += score

        score_color = get_rating_color(score)
        bar = color("*" * score + "." * (5 - score), score_color)
        print(f"         [{bar}] Running total: {running_total}/75")
        print()

    # Results
    max_score = 75
    percentage = int(running_total / max_score * 100)
    verdict_text, verdict_color, verdict_label = get_verdict(running_total)

    print(color("=" * 60, "bold"))
    print(color(f"  RESULTS: {product_name}", "bold"))
    print(color("=" * 60, "bold"))
    print()
    print(f"  Total Score:  {color(f'{running_total}/{max_score}', verdict_color)} ({percentage}%)")
    print(f"  Verdict:      {color(f'[{verdict_label}]', verdict_color)} {verdict_text}")
    print()

    # Breakdown
    print(color("  BREAKDOWN:", "bold"))
    print(f"  {'Criterion':<25} {'Score':>5}")
    print(f"  {'-' * 25} {'-' * 5}")
    for criterion in CRITERIA:
        name = criterion["name"]
        s = scores[name]
        sc = get_rating_color(s)
        print(f"  {name:<25} {color(str(s), sc):>5}")
    print(f"  {'-' * 25} {'-' * 5}")
    print(f"  {'TOTAL':<25} {color(str(running_total), verdict_color):>5}")
    print()

    # Strengths and weaknesses
    strengths = [c["name"] for c in CRITERIA if scores[c["name"]] >= 4]
    weaknesses = [c["name"] for c in CRITERIA if scores[c["name"]] <= 2]

    if strengths:
        print(f"  {color('Strengths:', 'green')} {', '.join(strengths)}")
    if weaknesses:
        print(f"  {color('Weaknesses:', 'red')} {', '.join(weaknesses)}")
    print()

    # Save
    entry = {
        "product": product_name,
        "source_url": source_url if source_url else None,
        "cost_price": float(cost_price) if cost_price else None,
        "scores": scores,
        "total": running_total,
        "max": max_score,
        "percentage": percentage,
        "verdict": verdict_label,
        "strengths": strengths,
        "weaknesses": weaknesses,
        "scored_at": datetime.now().isoformat(),
    }
    save_score(entry)
    print(f"  Saved to {SCORES_FILE.name}")
    print()


def list_products() -> None:
    """Show all scored products."""
    scores = load_scores()
    if not scores:
        print("\n  No products scored yet. Run without flags to score one.\n")
        return

    print()
    print(color("=" * 70, "bold"))
    print(color("  All Scored Products", "bold"))
    print(color("=" * 70, "bold"))
    print()
    print(f"  {'#':<4} {'Product':<30} {'Score':>7} {'%':>5}  {'Verdict':<6}  {'Date':<10}")
    print(f"  {'-' * 4} {'-' * 30} {'-' * 7} {'-' * 5}  {'-' * 6}  {'-' * 10}")

    # Sort by score descending
    sorted_scores = sorted(scores, key=lambda x: x["total"], reverse=True)

    for i, entry in enumerate(sorted_scores, 1):
        name = entry["product"][:28]
        total = entry["total"]
        pct = entry["percentage"]
        verdict = entry.get("verdict", "?")
        scored_at = entry.get("scored_at", "")[:10]

        _, vc, _ = get_verdict(total)
        print(f"  {i:<4} {name:<30} {color(f'{total}/75', vc):>7} {pct:>4}%  {color(verdict, vc):<6}  {scored_at}")

    print()
    print(f"  {len(scores)} product(s) scored total.")
    print()


def compare_products() -> None:
    """Side-by-side comparison of top 5 products."""
    scores = load_scores()
    if not scores:
        print("\n  No products scored yet. Run without flags to score one.\n")
        return

    sorted_scores = sorted(scores, key=lambda x: x["total"], reverse=True)
    top = sorted_scores[:5]

    print()
    print(color("=" * 80, "bold"))
    print(color("  Top Products Comparison", "bold"))
    print(color("=" * 80, "bold"))
    print()

    # Header
    names = [e["product"][:15] for e in top]
    header = f"  {'Criterion':<22}"
    for name in names:
        header += f" {name:>15}"
    print(color(header, "bold"))
    print(f"  {'-' * 22}" + (" " + "-" * 15) * len(top))

    # Each criterion
    for criterion in CRITERIA:
        row = f"  {criterion['name']:<22}"
        for entry in top:
            s = entry["scores"].get(criterion["name"], 0)
            sc = get_rating_color(s)
            row += f" {color(str(s), sc):>15}"
        print(row)

    # Totals
    print(f"  {'-' * 22}" + (" " + "-" * 15) * len(top))
    total_row = f"  {'TOTAL':<22}"
    for entry in top:
        t = entry["total"]
        _, vc, _ = get_verdict(t)
        total_row += f" {color(str(t), vc):>15}"
    print(color(total_row, "bold"))

    # Verdicts
    verdict_row = f"  {'VERDICT':<22}"
    for entry in top:
        t = entry["total"]
        _, vc, vl = get_verdict(t)
        verdict_row += f" {color(vl, vc):>15}"
    print(verdict_row)
    print()


def main():
    parser = argparse.ArgumentParser(
        description="Viral Vault Product Scorer. 15-point methodology for dropshipping.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "This scoring system is available as part of The Ecommerce Playbook ($14.99)\n\n"
            "Examples:\n"
            "  python3 viral_vault_scorer.py            # Score a new product\n"
            "  python3 viral_vault_scorer.py --list      # View all scored products\n"
            "  python3 viral_vault_scorer.py --compare   # Compare top 5 side-by-side\n"
        ),
    )
    parser.add_argument("--list", "-l", action="store_true", help="Show all scored products")
    parser.add_argument("--compare", "-c", action="store_true", help="Side-by-side comparison of top 5")

    args = parser.parse_args()

    if args.list:
        list_products()
    elif args.compare:
        compare_products()
    else:
        interactive_score()


if __name__ == "__main__":
    main()

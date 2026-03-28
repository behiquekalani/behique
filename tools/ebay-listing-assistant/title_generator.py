#!/usr/bin/env python3
"""
AI eBay Title Generator
Generates optimized eBay listing titles using Ollama (local AI, $0 cost).

Usage:
    python3 title_generator.py "Nike Air Max 90" --brand Nike --condition "New with Box"
    python3 title_generator.py "Wireless Earbuds" --brand JBL --features "Noise Cancelling, Bluetooth 5.3" --condition "New"
    python3 title_generator.py "Vintage Polaroid Camera" --condition "Used, Good"

Falls back to template-based generation if Ollama is offline.
"""

import argparse
import json
import sys
import urllib.request
import urllib.error
from typing import Optional

OLLAMA_URL = "http://localhost:11434/api/generate"
OLLAMA_MODEL = "qwen2.5:7b"
EBAY_TITLE_MAX = 80

# eBay title best practices baked into the prompt
SYSTEM_PROMPT = """You are an eBay listing title optimization expert.

Rules for eBay titles:
- MAXIMUM 80 characters. This is a hard limit. Never exceed it.
- Front-load the most important keywords (brand, product type)
- Include: brand, model, key features, size/color if relevant, condition
- Use common search terms buyers actually type
- No special characters, emojis, or excessive punctuation
- No filler words like "wow", "amazing", "look", "L@@K"
- Capitalize important words for readability
- Separate distinct attributes naturally, no em dashes

Return EXACTLY 5 title variations, one per line, numbered 1-5.
Each title must be under 80 characters. Count carefully.
Do not include any other text, explanations, or formatting."""


def generate_with_ollama(
    product: str,
    brand: Optional[str] = None,
    features: Optional[str] = None,
    condition: Optional[str] = None,
) -> list[str]:
    """Generate titles using Ollama local AI."""

    parts = []
    if brand:
        parts.append(f"Brand: {brand}")
    parts.append(f"Product: {product}")
    if features:
        parts.append(f"Key features: {features}")
    if condition:
        parts.append(f"Condition: {condition}")

    user_prompt = (
        "Generate 5 optimized eBay listing titles (each under 80 characters) for:\n"
        + "\n".join(parts)
    )

    payload = json.dumps({
        "model": OLLAMA_MODEL,
        "prompt": f"{SYSTEM_PROMPT}\n\n{user_prompt}",
        "stream": False,
        "options": {
            "temperature": 0.8,
            "num_predict": 512,
        },
    }).encode("utf-8")

    req = urllib.request.Request(
        OLLAMA_URL,
        data=payload,
        headers={"Content-Type": "application/json"},
    )

    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            data = json.loads(resp.read().decode("utf-8"))
    except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError):
        return []

    raw = data.get("response", "")
    return _parse_titles(raw)


def _parse_titles(raw: str) -> list[str]:
    """Extract numbered titles from model output."""
    titles = []
    for line in raw.strip().splitlines():
        line = line.strip()
        if not line:
            continue
        # Strip leading number/bullet: "1. ", "1) ", "- "
        for prefix_len in range(1, 5):
            if line[prefix_len:prefix_len + 2] in (". ", ") "):
                line = line[prefix_len + 2:]
                break
            if line[prefix_len:prefix_len + 1] == " " and line[:prefix_len].isdigit():
                line = line[prefix_len + 1:]
                break
        # Strip surrounding quotes
        if len(line) >= 2 and line[0] == '"' and line[-1] == '"':
            line = line[1:-1]
        line = line.strip()
        if line and len(line) <= EBAY_TITLE_MAX:
            titles.append(line)
    return titles[:5]


def generate_with_template(
    product: str,
    brand: Optional[str] = None,
    features: Optional[str] = None,
    condition: Optional[str] = None,
) -> list[str]:
    """Fallback: generate titles using templates when Ollama is offline."""

    brand_str = brand or ""
    condition_str = condition or ""
    feature_list = [f.strip() for f in features.split(",")] if features else []

    templates = []

    # Template 1: Brand Product Feature Condition
    t1_parts = [brand_str, product]
    if feature_list:
        t1_parts.append(feature_list[0])
    if condition_str:
        t1_parts.append(condition_str)
    templates.append(" ".join(p for p in t1_parts if p))

    # Template 2: Brand Product, All Features, Condition
    t2_parts = [brand_str, product]
    if feature_list:
        t2_parts.extend(feature_list[:2])
    if condition_str:
        t2_parts.append(condition_str)
    templates.append(" ".join(p for p in t2_parts if p))

    # Template 3: Product by Brand, Feature, Condition
    t3 = product
    if brand_str:
        t3 += f" by {brand_str}"
    if feature_list:
        t3 += f" {feature_list[0]}"
    if condition_str:
        t3 += f" {condition_str}"
    templates.append(t3)

    # Template 4: NEW/USED prefix style
    prefix = ""
    if condition_str:
        cond_upper = condition_str.upper()
        if "NEW" in cond_upper:
            prefix = "NEW"
        elif "USED" in cond_upper:
            prefix = "USED"
    t4_parts = []
    if prefix:
        t4_parts.append(prefix)
    t4_parts.extend([brand_str, product])
    if feature_list:
        t4_parts.append(feature_list[0])
    if condition_str and not prefix:
        t4_parts.append(condition_str)
    templates.append(" ".join(p for p in t4_parts if p))

    # Template 5: Compact, keyword-dense
    t5_parts = [brand_str, product]
    t5_parts.extend(feature_list[:3])
    templates.append(" ".join(p for p in t5_parts if p))

    # Enforce 80 char limit
    result = []
    for t in templates:
        t = t.strip()
        if len(t) > EBAY_TITLE_MAX:
            t = t[:EBAY_TITLE_MAX].rsplit(" ", 1)[0]
        result.append(t)

    return result


def generate_titles(
    product: str,
    brand: Optional[str] = None,
    features: Optional[str] = None,
    condition: Optional[str] = None,
) -> list[str]:
    """Generate eBay titles. Tries Ollama first, falls back to templates."""

    print(f"Connecting to Ollama ({OLLAMA_MODEL})...")
    titles = generate_with_ollama(product, brand, features, condition)

    if titles:
        print(f"Generated {len(titles)} titles with AI.\n")
        return titles

    print("Ollama offline or unavailable. Using template fallback.\n")
    return generate_with_template(product, brand, features, condition)


def main():
    parser = argparse.ArgumentParser(
        description="Generate optimized eBay listing titles using local AI.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Examples:\n"
            '  python3 title_generator.py "Nike Air Max 90" --brand Nike --condition "New with Box"\n'
            '  python3 title_generator.py "Wireless Earbuds" --brand JBL --features "Noise Cancelling, BT 5.3"\n'
        ),
    )
    parser.add_argument("product", help="Product name or description")
    parser.add_argument("--brand", "-b", help="Brand name")
    parser.add_argument("--features", "-f", help="Key features, comma-separated")
    parser.add_argument("--condition", "-c", help='Condition (e.g. "New with Box", "Used, Good")')

    args = parser.parse_args()

    print("=" * 60)
    print("  eBay Title Generator")
    print("=" * 60)
    print(f"\n  Product:   {args.product}")
    if args.brand:
        print(f"  Brand:     {args.brand}")
    if args.features:
        print(f"  Features:  {args.features}")
    if args.condition:
        print(f"  Condition: {args.condition}")
    print()

    titles = generate_titles(args.product, args.brand, args.features, args.condition)

    print("  OPTIMIZED TITLES (max 80 chars each):")
    print("  " + "-" * 56)
    for i, title in enumerate(titles, 1):
        char_count = len(title)
        bar = "#" * int(char_count / EBAY_TITLE_MAX * 30)
        print(f"  {i}. {title}")
        print(f"     [{char_count}/{EBAY_TITLE_MAX} chars] {bar}")
    print()

    # Copy hint
    if titles:
        print(f"  Tip: Copy your favorite and paste it into your eBay listing.")
    print()


if __name__ == "__main__":
    main()

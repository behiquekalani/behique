#!/usr/bin/env python3
"""
Oni-Puni Social Batch Generator
Generates a full week of social media content from a CSV product list.

Usage:
    python3 social_batch.py
    python3 social_batch.py my_products.csv

Reads products from sample_products.csv (or a file you specify).
Outputs to output/weekly-content/ as individual text files.

Falls back to template-based generation if Ollama is not running.
"""

import csv
import os
import sys
import json
import random
from datetime import datetime, timedelta

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL = "llama3.1:8b"
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DEFAULT_CSV = os.path.join(SCRIPT_DIR, "sample_products.csv")
OUTPUT_DIR = os.path.join(SCRIPT_DIR, "output", "weekly-content")

DAYS_OF_WEEK = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

# Hashtag pools for template mode
HASHTAG_POOLS = {
    "general": [
        "#kawaii", "#kawaiistore", "#onipuni", "#milwaukeeshop", "#shopsmall",
        "#smallbusiness", "#kawaiicollector", "#cuteaesthetic", "#kawaiilife",
        "#supportsmall", "#milwaukeelocal", "#kawaiistyle"
    ],
    "plush": [
        "#plushie", "#plushlife", "#plushcollector", "#plushiesofinstagram",
        "#stuffedanimals", "#softplush", "#kawaiiplush", "#plushielife"
    ],
    "stickers": [
        "#stickershop", "#stickeraddict", "#stickerlove", "#vinylstickers",
        "#stickerart", "#stickercollector", "#pokemonstickers"
    ],
    "pokemon": [
        "#pokemontcg", "#pokemoncollector", "#pokemonmerch", "#pokemoncards",
        "#pokemonfan", "#gottacatchemall"
    ],
    "figures": [
        "#blindbox", "#figurecollector", "#animefigures", "#collectibles",
        "#mysterybox", "#unboxing", "#figurine"
    ],
    "brand_sanx": [
        "#sanx", "#rilakkuma", "#korilakkuma", "#chairoikoguma",
        "#sumikkogurashi", "#japanesecharacters"
    ],
}

# ---------------------------------------------------------------------------
# Ollama API
# ---------------------------------------------------------------------------

def ask_ollama(prompt):
    """Send a prompt to Ollama. Returns None if Ollama is not available."""
    try:
        import requests
        response = requests.post(
            OLLAMA_URL,
            json={
                "model": MODEL,
                "prompt": prompt,
                "stream": False,
                "options": {"temperature": 0.8, "num_predict": 512}
            },
            timeout=120
        )
        if response.status_code == 200:
            return response.json().get("response", "").strip()
        return None
    except Exception:
        return None


def check_ollama():
    """Check if Ollama is running and the model is available."""
    result = ask_ollama("Say OK")
    return result is not None

# ---------------------------------------------------------------------------
# Product loading
# ---------------------------------------------------------------------------

def load_products(csv_path):
    """Load products from a CSV file. Returns a list of dicts."""
    products = []
    with open(csv_path, "r", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            products.append({
                "name": row["name"].strip(),
                "brand": row["brand"].strip(),
                "price": row["price"].strip(),
                "description": row["description"].strip()
            })
    return products

# ---------------------------------------------------------------------------
# Hashtag helper
# ---------------------------------------------------------------------------

def get_hashtags(product, count=25):
    """Pick relevant hashtags based on product attributes."""
    tags = list(HASHTAG_POOLS["general"])

    desc_lower = product["description"].lower() + " " + product["name"].lower()
    brand_lower = product["brand"].lower()

    if "plush" in desc_lower:
        tags.extend(HASHTAG_POOLS["plush"])
    if "sticker" in desc_lower:
        tags.extend(HASHTAG_POOLS["stickers"])
    if "pokemon" in desc_lower or "pokmon" in desc_lower:
        tags.extend(HASHTAG_POOLS["pokemon"])
    if "blind box" in desc_lower or "figure" in desc_lower or "figurine" in desc_lower:
        tags.extend(HASHTAG_POOLS["figures"])
    if brand_lower == "san-x" or "rilakkuma" in desc_lower:
        tags.extend(HASHTAG_POOLS["brand_sanx"])

    # Deduplicate and shuffle
    tags = list(set(tags))
    random.shuffle(tags)
    return tags[:count]

# ---------------------------------------------------------------------------
# AI generation
# ---------------------------------------------------------------------------

def generate_instagram_ai(product, day, theme):
    """Generate an Instagram post using Ollama."""
    prompt = f"""Write an Instagram post for Oni-Puni, a kawaii store in Milwaukee.

Product: {product['name']}
Brand: {product['brand']}
Price: ${product['price']}
Details: {product['description']}
Day: {day}
Theme: {theme}

Requirements:
- Engaging opening line
- 2-3 sentences about the product
- Call to action
- Then 25 relevant hashtags on a new line
- Do not use emojis
- Do not use em dashes

Write only the post, nothing else."""
    return ask_ollama(prompt)


def generate_tiktok_ai(product, theme):
    """Generate a TikTok concept using Ollama."""
    prompt = f"""Write a TikTok video concept for Oni-Puni, a kawaii store in Milwaukee.

Product: {product['name']}
Brand: {product['brand']}
Price: ${product['price']}
Details: {product['description']}
Video theme: {theme}

Requirements:
- Title for the video
- 30-60 second concept
- Camera directions in brackets
- Suggest a sound or music style
- Hashtags for TikTok
- Do not use emojis
- Do not use em dashes

Write only the concept, nothing else."""
    return ask_ollama(prompt)


def generate_pinterest_ai(product):
    """Generate a Pinterest pin description using Ollama."""
    prompt = f"""Write a Pinterest pin for Oni-Puni, a kawaii store.

Product: {product['name']}
Brand: {product['brand']}
Price: ${product['price']}
Details: {product['description']}

Requirements:
- Pin title (under 100 characters)
- Pin description (2-3 sentences, SEO friendly, include keywords people search for)
- Board suggestion
- 10 keywords for Pinterest SEO
- Do not use emojis
- Do not use em dashes

Write only the pin content, nothing else."""
    return ask_ollama(prompt)

# ---------------------------------------------------------------------------
# Template generation
# ---------------------------------------------------------------------------

INSTAGRAM_THEMES = [
    "New Arrival Monday",
    "Fan Favorite Tuesday",
    "Wishlist Wednesday",
    "Throwback Thursday (restocked item)",
    "Feel Good Friday",
    "Small Business Saturday",
    "Self Care Sunday"
]

TIKTOK_THEMES = [
    "Unboxing",
    "Collection showcase",
    "Day in the life of a kawaii shop owner",
    "Packing an order",
    "What sold this week",
    "Rating my inventory",
    "POV: you visit our booth"
]

INSTAGRAM_HOOKS = [
    "This one has been on everyone's wishlist.",
    "Just restocked and we already know it is going to fly.",
    "If you know, you know.",
    "Stop scrolling. You need this.",
    "New drop just landed at Oni-Puni.",
    "One of our all-time favorites.",
    "This is the one your collection is missing.",
]


def generate_instagram_template(product, day, theme):
    """Template-based Instagram post."""
    hook = random.choice(INSTAGRAM_HOOKS)
    hashtags = " ".join(get_hashtags(product, 25))

    lines = []
    lines.append(f"{hook}")
    lines.append("")
    lines.append(f"{product['name']} by {product['brand']}. "
                 f"{product['description'].capitalize()}. "
                 f"Priced at ${product['price']}.")
    lines.append("")
    lines.append("Shop link in bio. DM us with questions.")
    lines.append("")
    lines.append(hashtags)
    return "\n".join(lines)


def generate_tiktok_template(product, theme):
    """Template-based TikTok concept."""
    lines = []
    lines.append(f"TIKTOK CONCEPT: {theme.upper()}")
    lines.append(f"Product: {product['name']} by {product['brand']}")
    lines.append(f"Duration: 30-45 seconds")
    lines.append(f"Music: Lo-fi beats or cute J-pop")
    lines.append("")

    if theme == "Unboxing":
        lines.append(f'[Close-up of sealed package] "New arrival..."')
        lines.append(f'[Slowly open] "It is the {product["name"]} by {product["brand"]}."')
        lines.append(f'[Show details] "{product["description"].capitalize()}."')
        lines.append(f'[Price reveal] "Only ${product["price"]}. Link in bio."')
    elif theme == "Packing an order":
        lines.append('[Workspace setup, tissue paper, stickers ready]')
        lines.append(f'[Pick up {product["name"]}] "Someone has great taste."')
        lines.append('[Wrap carefully, add stickers, seal box]')
        lines.append('"Another happy customer. Want one? Link in bio."')
    else:
        lines.append(f'[Hold up product] "Let me tell you about this {product["name"]}."')
        lines.append(f'[Show details] "{product["description"].capitalize()}."')
        lines.append(f'[Price card] "${product["price"]} at Oni-Puni."')
        lines.append('"Follow for more kawaii finds."')

    lines.append("")
    lines.append("#kawaii #onipuni #unboxing #plushie #kawaiihaul #smallbusiness #tiktokshop")
    return "\n".join(lines)


def generate_pinterest_template(product):
    """Template-based Pinterest pin."""
    lines = []
    lines.append(f"PIN TITLE: {product['name']} by {product['brand']} | Kawaii Collectible")
    lines.append("")
    lines.append(f"PIN DESCRIPTION:")
    lines.append(f"Add the {product['name']} to your kawaii collection. "
                 f"{product['description'].capitalize()}. "
                 f"Available now at Oni-Puni for ${product['price']}. "
                 f"Perfect gift for anime fans and kawaii lovers.")
    lines.append("")
    lines.append(f"BOARD: Kawaii Collectibles")
    lines.append("")
    lines.append(f"KEYWORDS: kawaii, {product['brand'].lower()}, "
                 f"{product['name'].lower().split()[0]}, cute gifts, "
                 f"anime merch, japanese characters, plush toys, "
                 f"kawaii aesthetic, gift ideas, collectibles")
    return "\n".join(lines)

# ---------------------------------------------------------------------------
# Main batch generation
# ---------------------------------------------------------------------------

def main():
    # Determine CSV file
    csv_path = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_CSV

    if not os.path.exists(csv_path):
        print(f"Error: Cannot find {csv_path}")
        print(f"Make sure sample_products.csv is in the same folder as this script.")
        sys.exit(1)

    # Load products
    products = load_products(csv_path)
    if not products:
        print("Error: No products found in CSV file.")
        sys.exit(1)

    print(f"Loaded {len(products)} products from {os.path.basename(csv_path)}")

    # Check Ollama
    using_ai = check_ollama()
    if using_ai:
        print("Ollama is running. Using AI generation.")
    else:
        print("Ollama is not running. Using template mode.")
        print("(Start Ollama for AI-powered content.)")

    # Create output directory with date
    week_start = datetime.now().strftime("%Y-%m-%d")
    week_dir = os.path.join(OUTPUT_DIR, f"week-of-{week_start}")
    os.makedirs(os.path.join(week_dir, "instagram"), exist_ok=True)
    os.makedirs(os.path.join(week_dir, "tiktok"), exist_ok=True)
    os.makedirs(os.path.join(week_dir, "pinterest"), exist_ok=True)

    print(f"\nOutput folder: {week_dir}")
    print("=" * 60)

    # ---------------------------------------------------------------------------
    # Generate 7 Instagram posts (one per day)
    # ---------------------------------------------------------------------------
    print("\nGenerating Instagram posts...")
    for i in range(7):
        day = DAYS_OF_WEEK[i]
        theme = INSTAGRAM_THEMES[i]
        product = products[i % len(products)]  # Cycle through products

        print(f"  {day}: {product['name']}")

        if using_ai:
            content = generate_instagram_ai(product, day, theme)
            if not content:
                content = generate_instagram_template(product, day, theme)
        else:
            content = generate_instagram_template(product, day, theme)

        # Add header
        header = f"DAY: {day}\nTHEME: {theme}\nPRODUCT: {product['name']}\n{'=' * 40}\n\n"
        filepath = os.path.join(week_dir, "instagram", f"{i+1}-{day.lower()}.txt")
        with open(filepath, "w") as f:
            f.write(header + content)

    # ---------------------------------------------------------------------------
    # Generate 7 TikTok concepts (one per day)
    # ---------------------------------------------------------------------------
    print("\nGenerating TikTok concepts...")
    random.shuffle(products)  # Different order than Instagram
    tiktok_themes_shuffled = list(TIKTOK_THEMES)
    random.shuffle(tiktok_themes_shuffled)

    for i in range(7):
        day = DAYS_OF_WEEK[i]
        theme = tiktok_themes_shuffled[i % len(tiktok_themes_shuffled)]
        product = products[i % len(products)]

        print(f"  {day}: {product['name']} ({theme})")

        if using_ai:
            content = generate_tiktok_ai(product, theme)
            if not content:
                content = generate_tiktok_template(product, theme)
        else:
            content = generate_tiktok_template(product, theme)

        header = f"DAY: {day}\nTHEME: {theme}\nPRODUCT: {product['name']}\n{'=' * 40}\n\n"
        filepath = os.path.join(week_dir, "tiktok", f"{i+1}-{day.lower()}.txt")
        with open(filepath, "w") as f:
            f.write(header + content)

    # ---------------------------------------------------------------------------
    # Generate 3 Pinterest pins
    # ---------------------------------------------------------------------------
    print("\nGenerating Pinterest pins...")
    # Pick 3 different products, prefer higher-priced items for Pinterest
    sorted_products = sorted(products, key=lambda p: float(p["price"]), reverse=True)
    pin_products = sorted_products[:3]

    for i, product in enumerate(pin_products):
        print(f"  Pin {i+1}: {product['name']}")

        if using_ai:
            content = generate_pinterest_ai(product)
            if not content:
                content = generate_pinterest_template(product)
        else:
            content = generate_pinterest_template(product)

        header = f"PRODUCT: {product['name']}\nBRAND: {product['brand']}\nPRICE: ${product['price']}\n{'=' * 40}\n\n"
        filepath = os.path.join(week_dir, "pinterest", f"pin-{i+1}.txt")
        with open(filepath, "w") as f:
            f.write(header + content)

    # ---------------------------------------------------------------------------
    # Summary
    # ---------------------------------------------------------------------------
    print("\n" + "=" * 60)
    print("DONE. Weekly content generated:")
    print(f"  7 Instagram posts  -> {week_dir}/instagram/")
    print(f"  7 TikTok concepts  -> {week_dir}/tiktok/")
    print(f"  3 Pinterest pins   -> {week_dir}/pinterest/")
    print(f"\nMode: {'AI (Ollama)' if using_ai else 'Template'}")
    print(f"Products used: {len(products)}")
    print("\nOpen the files in the output folder to copy and paste into your apps.")


if __name__ == "__main__":
    main()

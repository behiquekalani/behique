#!/usr/bin/env python3
"""
Oni-Puni Product Writer
Generates product descriptions, Instagram captions, and TikTok scripts
for kawaii store products using a local AI (Ollama).

Usage:
    python3 product_writer.py "Product Name" "Brand" "$Price" "description of the product"

Examples:
    python3 product_writer.py "Rilakkuma Plush" "San-X" "$25.99" "soft brown bear plush, 12 inches, new with tags"
    python3 product_writer.py "Ghost Type Stickers" "Oni-Puni" "$3.00" "original ghost Pokemon type sticker sheet, vinyl, waterproof"
    python3 product_writer.py "Chairoikoguma Dino Plush" "San-X" "$30.00" "soft plush bear in dinosaur costume, mochi series"
    python3 product_writer.py "Highland Cow Plush" "Birduyen" "$25.99" "cute highland cow plush toy, soft, 10 inches"
    python3 product_writer.py "Pokemon Deck Box" "Ultra Pro" "$24.94" "Iono and Bellibolt design, holds 80+ sleeved cards"

Falls back to template-based generation if Ollama is not running.
Output is saved to the output/ folder automatically.
"""

import sys
import os
import json
import re
from datetime import datetime

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL = "llama3.1:8b"
OUTPUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "output")

# ---------------------------------------------------------------------------
# Ollama API call
# ---------------------------------------------------------------------------

def ask_ollama(prompt):
    """Send a prompt to Ollama and return the response text.
    Returns None if Ollama is not running or errors out."""
    try:
        import requests
        response = requests.post(
            OLLAMA_URL,
            json={
                "model": MODEL,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": 0.7,
                    "num_predict": 1024
                }
            },
            timeout=120
        )
        if response.status_code == 200:
            return response.json().get("response", "").strip()
        else:
            return None
    except Exception:
        return None

# ---------------------------------------------------------------------------
# AI-powered generation
# ---------------------------------------------------------------------------

def generate_shopify_ai(name, brand, price, description):
    """Use Ollama to write a Shopify product description."""
    prompt = f"""Write a Shopify product description for a kawaii store called Oni-Puni.

Product: {name}
Brand: {brand}
Price: ${price}
Details: {description}

Requirements:
- Warm, friendly tone that appeals to kawaii collectors
- 2-3 short paragraphs
- Mention the brand name
- Include care instructions if it is a plush
- End with a line about limited availability
- Do not use emojis
- Do not use em dashes

Write only the description, nothing else."""
    return ask_ollama(prompt)


def generate_instagram_ai(name, brand, price, description):
    """Use Ollama to write an Instagram caption with hashtags."""
    prompt = f"""Write an Instagram caption for a kawaii store called Oni-Puni based in Milwaukee.

Product: {name}
Brand: {brand}
Price: ${price}
Details: {description}

Requirements:
- Engaging first line that hooks the reader
- 2-3 sentences about the product
- Call to action (shop link in bio, DM to order, etc.)
- Then on a new line, write exactly 30 relevant hashtags
- Hashtags should mix popular ones (like #kawaii #plushie) with niche ones
- Do not use emojis
- Do not use em dashes

Write only the caption and hashtags, nothing else."""
    return ask_ollama(prompt)


def generate_tiktok_ai(name, brand, price, description):
    """Use Ollama to write a TikTok unboxing script."""
    prompt = f"""Write a TikTok unboxing video script for a kawaii store called Oni-Puni.

Product: {name}
Brand: {brand}
Price: ${price}
Details: {description}

Requirements:
- 30-60 second video script
- Start with a hook (first 3 seconds to grab attention)
- Include camera directions in brackets like [close-up of product]
- End with a call to action
- Suggest a trending sound or music style
- Do not use emojis
- Do not use em dashes

Write only the script, nothing else."""
    return ask_ollama(prompt)

# ---------------------------------------------------------------------------
# Template fallback (works without Ollama)
# ---------------------------------------------------------------------------

KAWAII_HASHTAGS = [
    "#kawaii", "#kawaiistore", "#plushie", "#plushlife", "#sanx", "#rilakkuma",
    "#cuteplush", "#kawaiicollector", "#animefigures", "#blindbox",
    "#kawaiimerch", "#pokemontcg", "#pokemoncollector", "#stickershop",
    "#stickeraddict", "#plushcollector", "#toycollector", "#milwaukeeshop",
    "#smallbusiness", "#shopsmall", "#kawaiiaesthetic", "#cuteaesthetic",
    "#japanesecharacters", "#animecollector", "#figurecollector",
    "#plushiesofinstagram", "#kawaiiplush", "#collectibles", "#onipuni",
    "#kawaiilife"
]


def generate_shopify_template(name, brand, price, description):
    """Template-based Shopify description."""
    lines = []
    lines.append(f"Meet the {name} by {brand}.")
    lines.append("")
    lines.append(f"This {description} is a must-have for any kawaii collector. "
                 f"Made with attention to detail and that signature {brand} charm "
                 f"that fans know and love.")
    lines.append("")
    if "plush" in description.lower():
        lines.append("Care: Surface wash only. Keep away from direct sunlight to preserve colors.")
        lines.append("")
    lines.append(f"Priced at ${price}. Limited stock available, grab yours before it is gone.")
    return "\n".join(lines)


def generate_instagram_template(name, brand, price, description):
    """Template-based Instagram caption."""
    lines = []
    lines.append(f"New arrival alert: {name} by {brand}.")
    lines.append("")
    lines.append(f"This {description} just landed at Oni-Puni and we are obsessed. "
                 f"Perfect for collectors or as a gift for the kawaii lover in your life.")
    lines.append("")
    lines.append(f"${price} | Link in bio to shop | DM us for questions")
    lines.append("")
    lines.append(" ".join(KAWAII_HASHTAGS))
    return "\n".join(lines)


def generate_tiktok_template(name, brand, price, description):
    """Template-based TikTok script."""
    lines = []
    lines.append("TIKTOK UNBOXING SCRIPT")
    lines.append("Duration: 30-45 seconds")
    lines.append("Music: Lo-fi or cute J-pop instrumental")
    lines.append("")
    lines.append(f'[Close-up of package] "Look what just came in..."')
    lines.append("")
    lines.append(f'[Slowly open packaging] "This is the {name} by {brand}..."')
    lines.append("")
    lines.append(f'[Hold up product, rotate slowly] "The details on this are incredible. '
                 f'{description.capitalize()}."')
    lines.append("")
    lines.append(f'[Show price tag or overlay] "And it is only ${price}."')
    lines.append("")
    lines.append('[Point to camera] "Link in bio. These go fast."')
    lines.append("")
    lines.append("Hashtags: #kawaii #unboxing #onipuni #plushie #kawaiihaul #smallbusiness")
    return "\n".join(lines)

# ---------------------------------------------------------------------------
# Output handling
# ---------------------------------------------------------------------------

def save_output(name, content):
    """Save generated content to a text file in the output folder."""
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # Clean the product name for use as a filename
    clean_name = re.sub(r'[^a-zA-Z0-9]+', '-', name.lower()).strip('-')
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    filename = f"{clean_name}-{timestamp}.txt"
    filepath = os.path.join(OUTPUT_DIR, filename)

    with open(filepath, "w") as f:
        f.write(content)

    return filepath

# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    # Check command line arguments
    if len(sys.argv) < 5:
        print("Usage: python3 product_writer.py \"Product Name\" \"Brand\" \"$Price\" \"description\"")
        print("")
        print("Example:")
        print('  python3 product_writer.py "Rilakkuma Plush" "San-X" "$25.99" "soft brown bear plush, 12 inches"')
        sys.exit(1)

    name = sys.argv[1]
    brand = sys.argv[2]
    price = sys.argv[3].replace("$", "")
    description = sys.argv[4]

    print(f"Generating content for: {name} by {brand} (${price})")
    print("=" * 60)

    # Try Ollama first, fall back to templates
    print("\nChecking if Ollama is running...")
    test = ask_ollama("Say OK")
    using_ai = test is not None

    if using_ai:
        print("Ollama is running. Using AI generation.\n")
    else:
        print("Ollama is not running. Using template mode.\n")
        print("(Start Ollama for AI-powered descriptions.)\n")

    # Generate Shopify description
    print("-" * 40)
    print("SHOPIFY PRODUCT DESCRIPTION")
    print("-" * 40)
    if using_ai:
        shopify = generate_shopify_ai(name, brand, price, description)
        if not shopify:
            shopify = generate_shopify_template(name, brand, price, description)
    else:
        shopify = generate_shopify_template(name, brand, price, description)
    print(shopify)

    # Generate Instagram caption
    print("\n" + "-" * 40)
    print("INSTAGRAM CAPTION")
    print("-" * 40)
    if using_ai:
        instagram = generate_instagram_ai(name, brand, price, description)
        if not instagram:
            instagram = generate_instagram_template(name, brand, price, description)
    else:
        instagram = generate_instagram_template(name, brand, price, description)
    print(instagram)

    # Generate TikTok script
    print("\n" + "-" * 40)
    print("TIKTOK UNBOXING SCRIPT")
    print("-" * 40)
    if using_ai:
        tiktok = generate_tiktok_ai(name, brand, price, description)
        if not tiktok:
            tiktok = generate_tiktok_template(name, brand, price, description)
    else:
        tiktok = generate_tiktok_template(name, brand, price, description)
    print(tiktok)

    # Combine and save
    full_output = []
    full_output.append(f"Product: {name}")
    full_output.append(f"Brand: {brand}")
    full_output.append(f"Price: ${price}")
    full_output.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    full_output.append(f"Mode: {'AI (Ollama)' if using_ai else 'Template'}")
    full_output.append("=" * 60)
    full_output.append("")
    full_output.append("SHOPIFY PRODUCT DESCRIPTION")
    full_output.append("-" * 40)
    full_output.append(shopify)
    full_output.append("")
    full_output.append("INSTAGRAM CAPTION")
    full_output.append("-" * 40)
    full_output.append(instagram)
    full_output.append("")
    full_output.append("TIKTOK UNBOXING SCRIPT")
    full_output.append("-" * 40)
    full_output.append(tiktok)

    filepath = save_output(name, "\n".join(full_output))
    print(f"\n{'=' * 60}")
    print(f"Saved to: {filepath}")


if __name__ == "__main__":
    main()

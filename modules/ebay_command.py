"""
eBay Command Handler for BehiqueBot

Telegram commands:
  /ebay "Product Name" 29.99              — quick list (name + price)
  /ebay "Product Name" 29.99 Used         — with condition
  /ebay "Product Name" 29.99 New 12 5.00  — with weight(oz) and cost
  /ebay help                              — usage guide
  /ebay last                              — show last generated listing

Calls quick_list() from the eBay listing pipeline, returns formatted
listing ready for copy-paste into eBay's form.
"""

import os
import sys
import json
import logging
import re
from datetime import datetime

# Add listing pipeline to path
LISTING_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                           "tools", "ebay-listing-assistant")
if LISTING_DIR not in sys.path:
    sys.path.insert(0, LISTING_DIR)

from quick_list import quick_list, save_listing

logger = logging.getLogger(__name__)

# Store last listing per user for /ebay last
_last_listings = {}

HELP_TEXT = """⚔️ *eBay Quick Lister*

*Usage:*
`/ebay "Product Name" price`
`/ebay "Product Name" price condition`
`/ebay "Product Name" price condition weight cost`

*Examples:*
`/ebay "Funko Pop Vegeta" 27.99`
`/ebay "Hello Kitty Mug" 14.99 Used`
`/ebay "PS5 Controller" 45.00 Used 16 20`

*Parameters:*
• `price` — listing price in USD
• `condition` — New (default), Used, Refurbished
• `weight` — weight in ounces (default: 12)
• `cost` — what you paid (default: 0)

*Other commands:*
`/ebay last` — re-send last listing
`/ebay help` — this message
"""


def parse_ebay_args(text: str) -> dict:
    """
    Parse /ebay command arguments.

    Supports:
      /ebay "Product Name" 29.99
      /ebay "Product Name" 29.99 Used
      /ebay "Product Name" 29.99 Used 16 5.00
      /ebay Product Name 29.99
    """
    text = text.strip()

    # Extract quoted product name
    quoted = re.match(r'"([^"]+)"\s*(.*)', text)
    if quoted:
        name = quoted.group(1)
        rest = quoted.group(2).strip()
    else:
        # No quotes — split on last number-like tokens
        # Try to find where numbers start
        words = text.split()
        name_parts = []
        rest_parts = []
        found_number = False
        for w in words:
            if not found_number and re.match(r'^\d+\.?\d*$', w):
                found_number = True
            if found_number:
                rest_parts.append(w)
            else:
                name_parts.append(w)
        name = " ".join(name_parts)
        rest = " ".join(rest_parts)

    if not name:
        return {"error": "No product name provided"}

    # Parse remaining: price [condition] [weight] [cost]
    tokens = rest.split() if rest else []

    price = None
    condition = "New"
    weight = 12.0
    cost = 0.0

    # First token should be price
    if tokens:
        try:
            price = float(tokens[0].replace("$", ""))
        except ValueError:
            return {"error": f"Invalid price: {tokens[0]}"}
        tokens = tokens[1:]

    if price is None:
        return {"error": "No price provided. Usage: /ebay \"Product\" 29.99"}

    # Second token: condition or weight
    valid_conditions = {"new", "used", "refurbished", "for parts"}
    if tokens and tokens[0].lower() in valid_conditions:
        condition = tokens[0].capitalize()
        if condition == "For":
            condition = "For Parts"
            tokens = tokens[1:]  # skip "parts"
        tokens = tokens[1:]

    # Third token: weight
    if tokens:
        try:
            weight = float(tokens[0])
            tokens = tokens[1:]
        except ValueError:
            pass

    # Fourth token: cost
    if tokens:
        try:
            cost = float(tokens[0].replace("$", ""))
            tokens = tokens[1:]
        except ValueError:
            pass

    return {
        "name": name,
        "price": price,
        "condition": condition,
        "weight_oz": weight,
        "cost": cost,
    }


async def handle_ebay_command(update, context):
    """Handle /ebay Telegram command."""
    from telegram.constants import ParseMode

    user_id = str(update.message.from_user.id)
    raw_args = " ".join(context.args) if context.args else ""

    # /ebay help
    if not raw_args or raw_args.lower() in ("help", "h", "?"):
        await update.message.reply_text(HELP_TEXT, parse_mode=ParseMode.MARKDOWN)
        return

    # /ebay last
    if raw_args.lower() == "last":
        last = _last_listings.get(user_id)
        if last:
            await _send_listing(update, last["output"], last["pricing"], last["name"])
        else:
            await update.message.reply_text("No listing generated yet this session.")
        return

    # Parse arguments
    parsed = parse_ebay_args(raw_args)
    if "error" in parsed:
        await update.message.reply_text(
            f"❌ {parsed['error']}\n\nType `/ebay help` for usage.",
            parse_mode=ParseMode.MARKDOWN,
        )
        return

    # Generate listing
    try:
        await update.message.reply_text(
            f"⚙️ Generating listing for *{parsed['name']}* at ${parsed['price']:.2f}...",
            parse_mode=ParseMode.MARKDOWN,
        )

        output, pricing = quick_list(
            name=parsed["name"],
            price=parsed["price"],
            condition=parsed["condition"],
            weight_oz=parsed["weight_oz"],
            cost=parsed["cost"],
        )

        # Save to file
        txt_path, json_path = save_listing(
            name=parsed["name"],
            output=output,
            pricing=pricing,
            args_dict=parsed,
        )

        # Cache for /ebay last
        _last_listings[user_id] = {
            "name": parsed["name"],
            "output": output,
            "pricing": pricing,
            "txt_path": txt_path,
        }

        await _send_listing(update, output, pricing, parsed["name"])

        logger.info(f"eBay listing generated: {parsed['name']} @ ${parsed['price']:.2f} → {txt_path}")

    except Exception as e:
        logger.error(f"eBay listing error: {e}")
        await update.message.reply_text(f"❌ Error generating listing: {str(e)[:200]}")


async def _send_listing(update, output: str, pricing: dict, name: str):
    """Send listing to Telegram, split into digestible messages."""
    from telegram.constants import ParseMode

    # Summary message (human-readable, not the full dump)
    title_line = ""
    for line in output.split("\n"):
        stripped = line.strip()
        if stripped and not stripped.startswith("=") and not stripped.startswith("─") and "TITLE" not in stripped and "/80" not in stripped:
            if len(stripped) > 10 and not stripped.startswith("["):
                title_line = stripped
                break

    summary = (
        f"✅ *Listing Ready: {name}*\n\n"
        f"📋 *Title:* `{title_line}`\n"
        f"💰 *Price:* ${pricing['list_price']:.2f}\n"
        f"📦 *Ship:* {pricing['shipping_service']} (${pricing['shipping_cost']:.2f})\n"
        f"🏷️ *Fees:* ${pricing['ebay_fees']:.2f}\n"
        f"💵 *Profit:* ${pricing['profit']:.2f} ({pricing['margin']})\n"
        f"📍 *Breakeven:* ${pricing['breakeven']:.2f}\n\n"
        f"_Full listing below — copy each section into eBay._"
    )

    await update.message.reply_text(summary, parse_mode=ParseMode.MARKDOWN)

    # Full listing as code block (split if > 4096 chars)
    MAX_MSG = 4000  # Telegram limit is 4096, leave buffer
    chunks = []
    current = ""
    for line in output.split("\n"):
        if len(current) + len(line) + 2 > MAX_MSG:
            chunks.append(current)
            current = line + "\n"
        else:
            current += line + "\n"
    if current:
        chunks.append(current)

    for chunk in chunks:
        await update.message.reply_text(f"```\n{chunk}\n```", parse_mode=ParseMode.MARKDOWN)

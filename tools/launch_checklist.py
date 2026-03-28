#!/usr/bin/env python3
"""Product launch checklist generator for the Behike store."""

import argparse
import json
import os
import re
from datetime import datetime, timedelta

CHECKLIST_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "launch-checklists")
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID", "")

VALID_TYPES = ["blueprint", "guide", "kit", "course"]

CHECKLIST_TEMPLATE = {
    "pre_launch": [
        "Product audit: content reviewed, no errors, links work",
        "Description written: benefit-driven, SEO keywords included",
        "Pricing set: competitor check done, tier chosen",
        "Cover image: designed, sized for Gumroad + socials",
        "Tags: 5+ relevant tags added",
        "Category: assigned in store taxonomy",
        "Test download: file opens correctly, no corruption",
    ],
    "launch_day": [
        "Publish on Gumroad: live, thumbnail visible, price correct",
        "Add to products.json in storefront/",
        "Update sitemap with new product URL",
        "Post on IG/TikTok/Twitter: launch announcement",
        "Send newsletter to email list",
    ],
    "post_launch": [
        "Monitor first 24h sales and traffic",
        "Respond to buyer questions within 2h",
        "Collect feedback: DMs, reviews, comments",
        "Add to relevant bundle if one exists",
        "Schedule follow-up content: tutorial, breakdown, or testimonial",
    ],
}


def slugify(name: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")


def checklist_path(name: str) -> str:
    return os.path.join(CHECKLIST_DIR, f"{slugify(name)}.json")


def create_checklist(name: str, product_type: str) -> dict:
    if product_type not in VALID_TYPES:
        print(f"Invalid type '{product_type}'. Must be one of: {', '.join(VALID_TYPES)}")
        return {}
    path = checklist_path(name)
    if os.path.exists(path):
        print(f"Checklist already exists: {path}")
        return json.load(open(path))
    data = {
        "product_name": name,
        "product_type": product_type,
        "created": datetime.now().isoformat(),
        "phases": {},
    }
    for phase, items in CHECKLIST_TEMPLATE.items():
        data["phases"][phase] = [
            {"item": item, "done": False, "completed_at": None} for item in items
        ]
    os.makedirs(CHECKLIST_DIR, exist_ok=True)
    with open(path, "w") as f:
        json.dump(data, f, indent=2)
    total = sum(len(v) for v in CHECKLIST_TEMPLATE.values())
    print(f"Created checklist for '{name}' ({product_type}) - {total} items")
    print(f"Saved to: {path}")
    return data


def show_check(name: str):
    path = checklist_path(name)
    if not os.path.exists(path):
        print(f"No checklist found for '{name}'. Use --new to create one.")
        return
    data = json.load(open(path))
    print(f"\n  {data['product_name']} ({data['product_type']})")
    print(f"  Created: {data['created'][:10]}\n")
    total, done = 0, 0
    for phase, items in data["phases"].items():
        label = phase.replace("_", " ").upper()
        phase_done = sum(1 for i in items if i["done"])
        print(f"  [{phase_done}/{len(items)}] {label}")
        for idx, item in enumerate(items, 1):
            marker = "x" if item["done"] else " "
            global_idx = total + idx
            print(f"    {global_idx:2d}. [{marker}] {item['item']}")
            if item["done"] and item["completed_at"]:
                print(f"              done {item['completed_at'][:10]}")
        total += len(items)
        done += phase_done
    pct = int(done / total * 100) if total else 0
    print(f"\n  Progress: {done}/{total} ({pct}%)\n")


def complete_item(name: str, item_number: int):
    path = checklist_path(name)
    if not os.path.exists(path):
        print(f"No checklist found for '{name}'.")
        return
    data = json.load(open(path))
    idx = 0
    for phase, items in data["phases"].items():
        for item in items:
            idx += 1
            if idx == item_number:
                if item["done"]:
                    print(f"Already done: {item['item']}")
                    return
                item["done"] = True
                item["completed_at"] = datetime.now().isoformat()
                with open(path, "w") as f:
                    json.dump(data, f, indent=2)
                print(f"Completed #{item_number}: {item['item']}")
                return
    print(f"Item #{item_number} not found. Max is {idx}.")


def show_active():
    os.makedirs(CHECKLIST_DIR, exist_ok=True)
    files = [f for f in os.listdir(CHECKLIST_DIR) if f.endswith(".json")]
    if not files:
        print("No active checklists.")
        return
    print("\n  ACTIVE LAUNCHES\n")
    for fname in sorted(files):
        data = json.load(open(os.path.join(CHECKLIST_DIR, fname)))
        total = sum(len(items) for items in data["phases"].values())
        done = sum(1 for items in data["phases"].values() for i in items if i["done"])
        if done < total:
            pct = int(done / total * 100) if total else 0
            age = (datetime.now() - datetime.fromisoformat(data["created"])).days
            flag = " !! OVERDUE" if age > 2 and pct < 100 else ""
            print(f"  [{done:2d}/{total}] {data['product_name']} ({data['product_type']}) - {pct}% - {age}d old{flag}")
    print()


def send_telegram_reminders():
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        print("Set TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID env vars for reminders.")
        return
    os.makedirs(CHECKLIST_DIR, exist_ok=True)
    files = [f for f in os.listdir(CHECKLIST_DIR) if f.endswith(".json")]
    overdue = []
    for fname in files:
        data = json.load(open(os.path.join(CHECKLIST_DIR, fname)))
        created = datetime.fromisoformat(data["created"])
        if datetime.now() - created < timedelta(hours=48):
            continue
        pending = []
        for items in data["phases"].values():
            for item in items:
                if not item["done"]:
                    pending.append(item["item"])
        if pending:
            overdue.append((data["product_name"], pending))
    if not overdue:
        print("No overdue items.")
        return
    lines = ["Launch checklist reminders:\n"]
    for name, items in overdue:
        lines.append(f"{name}:")
        for item in items[:5]:
            lines.append(f"  - {item}")
        if len(items) > 5:
            lines.append(f"  ...and {len(items) - 5} more")
    msg = "\n".join(lines)
    try:
        import urllib.request
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        payload = json.dumps({"chat_id": TELEGRAM_CHAT_ID, "text": msg}).encode()
        req = urllib.request.Request(url, data=payload, headers={"Content-Type": "application/json"})
        urllib.request.urlopen(req)
        print(f"Sent reminders for {len(overdue)} product(s).")
    except Exception as e:
        print(f"Telegram send failed: {e}")


def main():
    parser = argparse.ArgumentParser(description="Behike product launch checklist")
    parser.add_argument("--new", metavar="NAME", help="Create checklist for a new product")
    parser.add_argument("--type", metavar="TYPE", default="blueprint", help="Product type: blueprint/guide/kit/course")
    parser.add_argument("--check", metavar="NAME", help="Show checklist progress for a product")
    parser.add_argument("--complete", nargs=2, metavar=("NAME", "ITEM"), help="Mark item as done")
    parser.add_argument("--active", action="store_true", help="Show all incomplete launches")
    parser.add_argument("--remind", action="store_true", help="Send Telegram reminders for 48h+ overdue items")
    args = parser.parse_args()

    if args.new:
        create_checklist(args.new, args.type)
    elif args.check:
        show_check(args.check)
    elif args.complete:
        complete_item(args.complete[0], int(args.complete[1]))
    elif args.active:
        show_active()
    elif args.remind:
        send_telegram_reminders()
    else:
        parser.print_help()


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
Beta Reader Program Manager
Manages beta readers who receive free products in exchange for honest reviews.
Copyright 2026 Behike.
"""

import argparse
import json
import os
import sys
import smtplib
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from pathlib import Path

# Paths
SCRIPT_DIR = Path(__file__).parent.resolve()
PROJECT_ROOT = SCRIPT_DIR.parent
READERS_FILE = PROJECT_ROOT / "Ceiba" / "beta-readers" / "readers.json"
TESTIMONIALS_FILE = PROJECT_ROOT / "themes" / "behike-store" / "landing-pages" / "testimonials.json"

# Google Form template for collecting reviews
REVIEW_FORM_TEMPLATE = (
    "https://docs.google.com/forms/d/e/YOUR_FORM_ID/viewform"
    "?usp=pp_url"
    "&entry.NAME_FIELD={name}"
    "&entry.PRODUCT_FIELD={product}"
)

# SMTP config (reads from environment or .env)
SMTP_HOST = os.environ.get("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT = int(os.environ.get("SMTP_PORT", "587"))
SMTP_USER = os.environ.get("SMTP_USER", "")
SMTP_PASS = os.environ.get("SMTP_PASS", "")
FROM_EMAIL = os.environ.get("FROM_EMAIL", SMTP_USER)


def load_readers() -> list:
    """Load beta readers from JSON file."""
    if not READERS_FILE.exists():
        READERS_FILE.parent.mkdir(parents=True, exist_ok=True)
        READERS_FILE.write_text("[]")
        return []
    with open(READERS_FILE, "r") as f:
        return json.load(f)


def save_readers(readers: list):
    """Save beta readers to JSON file."""
    READERS_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(READERS_FILE, "w") as f:
        json.dump(readers, f, indent=2)


def find_reader(readers: list, name: str) -> dict | None:
    """Find a reader by name (case-insensitive)."""
    for r in readers:
        if r["name"].lower() == name.lower():
            return r
    return None


def add_reader(name: str, email: str, product: str):
    """Add a new beta reader."""
    readers = load_readers()

    if find_reader(readers, name):
        print(f"Reader '{name}' already exists. Use a different name or update manually.")
        return

    reader = {
        "name": name,
        "email": email,
        "product": product,
        "date_added": datetime.now().isoformat(),
        "date_sent": None,
        "product_sent": False,
        "review_received": False,
        "review_text": None,
        "rating": None,
        "reminders_sent": 0,
        "last_reminder": None,
    }

    readers.append(reader)
    save_readers(readers)
    print(f"Added beta reader: {name} ({email}) for '{product}'")
    print(f"Total readers: {len(readers)}")


def send_product(name: str):
    """Send the product PDF to a beta reader via email."""
    readers = load_readers()
    reader = find_reader(readers, name)

    if not reader:
        print(f"No reader found with name '{name}'")
        return

    if not SMTP_USER or not SMTP_PASS:
        print("SMTP credentials not configured.")
        print("Set SMTP_USER and SMTP_PASS environment variables.")
        print("Or create a .env file in the project root.")
        return

    product = reader["product"]

    # Look for the product PDF in common locations
    pdf_paths = [
        PROJECT_ROOT / "Ceiba" / "projects" / "content-empire" / "products" / f"{product}.pdf",
        PROJECT_ROOT / "products" / f"{product}.pdf",
        PROJECT_ROOT / f"{product}.pdf",
    ]

    pdf_path = None
    for p in pdf_paths:
        if p.exists():
            pdf_path = p
            break

    if not pdf_path:
        print(f"Product PDF not found for '{product}'.")
        print("Searched:")
        for p in pdf_paths:
            print(f"  {p}")
        print("\nPlace the PDF in one of these locations and try again.")
        return

    # Build email
    msg = MIMEMultipart()
    msg["From"] = FROM_EMAIL
    msg["To"] = reader["email"]
    msg["Subject"] = f"Your free copy of '{product}' from Behike"

    body = f"""Hey {reader['name'].split()[0]},

Thanks for joining the Behike beta reader program. Here's your free copy of "{product}".

All I ask in return is an honest review. No pressure to be positive. Just tell me what you actually thought.

When you're ready (take your time, but ideally within 2 weeks), reply to this email with:
1. A rating from 1-5
2. A sentence or two about what you found most useful
3. Whether I can use your first name and review on the landing page

That's it. Simple.

Thanks for helping build something real.

Kalani
Behike"""

    msg.attach(MIMEText(body, "plain"))

    # Attach PDF
    with open(pdf_path, "rb") as f:
        attachment = MIMEBase("application", "octet-stream")
        attachment.set_payload(f.read())
    encoders.encode_base64(attachment)
    attachment.add_header(
        "Content-Disposition",
        f"attachment; filename={pdf_path.name}",
    )
    msg.attach(attachment)

    try:
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_USER, SMTP_PASS)
            server.send_message(msg)

        reader["product_sent"] = True
        reader["date_sent"] = datetime.now().isoformat()
        save_readers(readers)
        print(f"Product sent to {reader['name']} ({reader['email']})")
    except Exception as e:
        print(f"Failed to send email: {e}")


def remind_reader(name: str):
    """Send a reminder to submit their review."""
    readers = load_readers()
    reader = find_reader(readers, name)

    if not reader:
        print(f"No reader found with name '{name}'")
        return

    if reader["review_received"]:
        print(f"{reader['name']} already submitted their review.")
        return

    if not reader["product_sent"]:
        print(f"Product hasn't been sent to {reader['name']} yet. Send it first.")
        return

    if not SMTP_USER or not SMTP_PASS:
        print("SMTP credentials not configured.")
        print("Set SMTP_USER and SMTP_PASS environment variables.")
        return

    msg = MIMEMultipart()
    msg["From"] = FROM_EMAIL
    msg["To"] = reader["email"]
    msg["Subject"] = f"Quick check-in: how was '{reader['product']}'?"

    body = f"""Hey {reader['name'].split()[0]},

Just checking in. Did you get a chance to look at "{reader['product']}"?

No rush, but if you've had time to read through it, I'd love your honest take. Even just a sentence or two helps a lot.

Reply with:
1. Rating (1-5)
2. What you found most useful (or least useful, be honest)
3. Whether I can use your first name + review publicly

Thanks again.

Kalani
Behike"""

    msg.attach(MIMEText(body, "plain"))

    try:
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_USER, SMTP_PASS)
            server.send_message(msg)

        reader["reminders_sent"] += 1
        reader["last_reminder"] = datetime.now().isoformat()
        save_readers(readers)
        print(f"Reminder sent to {reader['name']} (reminder #{reader['reminders_sent']})")
    except Exception as e:
        print(f"Failed to send reminder: {e}")


def list_readers():
    """Show all beta readers and their status."""
    readers = load_readers()

    if not readers:
        print("No beta readers yet.")
        print("Add one: python beta_reader.py --add 'Name' 'email@example.com' 'Product Name'")
        return

    print(f"\nBeta Reader Program - {len(readers)} readers")
    print("=" * 70)

    # Stats
    sent = sum(1 for r in readers if r["product_sent"])
    reviewed = sum(1 for r in readers if r["review_received"])
    print(f"Products sent: {sent}/{len(readers)}")
    print(f"Reviews received: {reviewed}/{len(readers)}")
    if sent > 0:
        print(f"Response rate: {reviewed/sent*100:.0f}%")
    print("-" * 70)

    for r in readers:
        status = "REVIEWED" if r["review_received"] else ("SENT" if r["product_sent"] else "PENDING")
        rating = f"{'*' * r['rating']}" if r.get("rating") else ""
        print(f"  [{status:8}] {r['name']:20} {r['email']:30} {r['product']}")
        if rating:
            print(f"            Rating: {rating} ({r['rating']}/5)")
        if r.get("review_text"):
            preview = r["review_text"][:80] + "..." if len(r["review_text"]) > 80 else r["review_text"]
            print(f"            Review: \"{preview}\"")
        if r.get("reminders_sent", 0) > 0:
            print(f"            Reminders sent: {r['reminders_sent']}")

    print()


def record_review(name: str, rating: int, review_text: str):
    """Record a review from a beta reader."""
    readers = load_readers()
    reader = find_reader(readers, name)

    if not reader:
        print(f"No reader found with name '{name}'")
        return

    if rating < 1 or rating > 5:
        print("Rating must be between 1 and 5.")
        return

    reader["review_received"] = True
    reader["rating"] = rating
    reader["review_text"] = review_text

    save_readers(readers)
    print(f"Review recorded for {reader['name']}: {rating}/5")
    print(f"Review: \"{review_text}\"")

    # Auto-update testimonials.json if it exists
    update_testimonials(readers)


def update_testimonials(readers: list):
    """Update testimonials.json with reviews that have been received."""
    testimonials = []

    for r in readers:
        if r["review_received"] and r.get("review_text"):
            # Use first name + last initial for privacy
            name_parts = r["name"].split()
            display_name = name_parts[0]
            if len(name_parts) > 1:
                display_name += f" {name_parts[1][0]}."

            testimonials.append({
                "name": display_name,
                "rating": r["rating"],
                "quote": r["review_text"],
                "product": r["product"],
                "date": r.get("date_sent", datetime.now().isoformat())[:10],
                "verified": True,
            })

    if testimonials:
        TESTIMONIALS_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(TESTIMONIALS_FILE, "w") as f:
            json.dump(testimonials, f, indent=2)
        print(f"Updated testimonials.json with {len(testimonials)} reviews.")


def generate_form_link():
    """Generate a Google Form link for collecting reviews."""
    print("\nGoogle Form Review Collection")
    print("=" * 50)
    print()
    print("Create a Google Form with these fields:")
    print("  1. Full Name (short answer)")
    print("  2. Email (short answer)")
    print("  3. Product Reviewed (dropdown with your product names)")
    print("  4. Rating 1-5 (linear scale)")
    print("  5. What did you find most useful? (paragraph)")
    print("  6. What could be improved? (paragraph)")
    print("  7. Can we use your first name and review publicly? (yes/no)")
    print()
    print("Template URL (replace YOUR_FORM_ID after creating):")
    print(f"  {REVIEW_FORM_TEMPLATE}")
    print()
    print("After creating the form:")
    print("  1. Update REVIEW_FORM_TEMPLATE in this script with your real form ID")
    print("  2. Set up email notifications so you know when reviews come in")
    print("  3. Use --record to manually add reviews to the system")


def main():
    parser = argparse.ArgumentParser(
        description="Beta Reader Program Manager - Behike",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python beta_reader.py --add "Maria Lopez" "maria@email.com" "AI Automation Blueprint"
  python beta_reader.py --send "Maria Lopez"
  python beta_reader.py --remind "Maria Lopez"
  python beta_reader.py --record "Maria Lopez" 5 "Clear, actionable steps. Best guide I've read on automation."
  python beta_reader.py --list
  python beta_reader.py --collect
        """,
    )

    parser.add_argument("--add", nargs=3, metavar=("NAME", "EMAIL", "PRODUCT"),
                        help="Add a beta reader")
    parser.add_argument("--send", metavar="NAME",
                        help="Send the product PDF to a reader")
    parser.add_argument("--remind", metavar="NAME",
                        help="Send a review reminder to a reader")
    parser.add_argument("--record", nargs=3, metavar=("NAME", "RATING", "REVIEW"),
                        help="Record a review (name, 1-5 rating, review text)")
    parser.add_argument("--list", action="store_true",
                        help="List all beta readers and status")
    parser.add_argument("--collect", action="store_true",
                        help="Generate Google Form link for review collection")
    parser.add_argument("--export-testimonials", action="store_true",
                        help="Export reviews to testimonials.json")

    args = parser.parse_args()

    if args.add:
        add_reader(args.add[0], args.add[1], args.add[2])
    elif args.send:
        send_product(args.send)
    elif args.remind:
        remind_reader(args.remind)
    elif args.record:
        record_review(args.record[0], int(args.record[1]), args.record[2])
    elif args.list:
        list_readers()
    elif args.collect:
        generate_form_link()
    elif args.export_testimonials:
        readers = load_readers()
        update_testimonials(readers)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()

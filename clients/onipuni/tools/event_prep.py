#!/usr/bin/env python3
"""
Oni-Puni Event Prep Generator
Generates all materials needed for an upcoming event: social media posts,
email blast, packing checklist, QR code info, and follow-up email.

Usage:
    python3 event_prep.py "Event Name" "Date" "Booth/Table Number"

Examples:
    python3 event_prep.py "Milwaukee Comic Con" "March 29" "Booth 42"
    python3 event_prep.py "Anime Milwaukee" "April 12-13" "Table A7"
    python3 event_prep.py "Milwaukee Night Market" "May 3" "Vendor Spot 15"
    python3 event_prep.py "Kawaii Pop-Up at Third Ward" "June 1" "Main Floor"
    python3 event_prep.py "Holiday Market MKE" "December 7" "Booth 22"

Falls back to template-based generation if Ollama is not running.
Output saved to output/events/[event-name]/
"""

import sys
import os
import re
from datetime import datetime

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL = "llama3.1:8b"
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_BASE = os.path.join(SCRIPT_DIR, "output", "events")

STORE_NAME = "Oni-Puni"
STORE_EMAIL = "onipuni@email.com"  # Randy should update this
STORE_WEBSITE = "onipuni.com"       # Randy should update this
STORE_INSTAGRAM = "@onipuni"        # Randy should update this

# ---------------------------------------------------------------------------
# Ollama API
# ---------------------------------------------------------------------------

def ask_ollama(prompt):
    """Send a prompt to Ollama. Returns None if not available."""
    try:
        import requests
        response = requests.post(
            OLLAMA_URL,
            json={
                "model": MODEL,
                "prompt": prompt,
                "stream": False,
                "options": {"temperature": 0.7, "num_predict": 1024}
            },
            timeout=120
        )
        if response.status_code == 200:
            return response.json().get("response", "").strip()
        return None
    except Exception:
        return None


def check_ollama():
    """Check if Ollama is running."""
    return ask_ollama("Say OK") is not None

# ---------------------------------------------------------------------------
# AI generation functions
# ---------------------------------------------------------------------------

def generate_announcements_ai(event, date, booth):
    """Generate 3 social media announcement posts using AI."""
    prompt = f"""Write 3 social media announcement posts for Oni-Puni, a kawaii store in Milwaukee.

Event: {event}
Date: {date}
Location: {booth}
Store: Oni-Puni (kawaii collectibles, plushies, stickers, blind boxes)

Write 3 different posts:
1. First announcement (excitement, save the date)
2. Countdown post (what to expect at the booth)
3. Day-of post (we are here, come find us)

Each post should:
- Be ready to copy-paste into Instagram
- Include 15-20 relevant hashtags
- Have a clear call to action
- Do not use emojis
- Do not use em dashes

Label each post clearly as POST 1, POST 2, POST 3."""
    return ask_ollama(prompt)


def generate_email_blast_ai(event, date, booth):
    """Generate email blast copy using AI."""
    prompt = f"""Write an email blast for Oni-Puni, a kawaii store, announcing they will be at an event.

Event: {event}
Date: {date}
Location: {booth}
Store: Oni-Puni (kawaii collectibles, plushies, stickers, blind boxes, Pokemon TCG)

Requirements:
- Subject line
- Preview text (the snippet shown in inbox)
- Email body (friendly, warm, builds excitement)
- Mention exclusive items or deals for event attendees
- Include store hours at the event
- Call to action to visit the booth
- Do not use emojis
- Do not use em dashes

Write the complete email."""
    return ask_ollama(prompt)


def generate_followup_ai(event, date):
    """Generate post-event follow-up email using AI."""
    prompt = f"""Write a follow-up email for Oni-Puni to send after attending an event.

Event: {event}
Date: {date}
Store: Oni-Puni (kawaii collectibles, plushies, stickers)

Requirements:
- Thank people for visiting the booth
- Mention that items from the event are available online
- Include a discount code for first online order (suggest a code name)
- Ask them to follow on social media
- Warm, personal tone
- Do not use emojis
- Do not use em dashes

Write the complete follow-up email with subject line."""
    return ask_ollama(prompt)

# ---------------------------------------------------------------------------
# Template generation functions
# ---------------------------------------------------------------------------

def generate_announcements_template(event, date, booth):
    """Template-based announcement posts."""
    posts = []

    # Post 1: Save the date
    posts.append(f"""POST 1 - SAVE THE DATE
{'=' * 40}

Mark your calendars. {STORE_NAME} is coming to {event} on {date}.

We are bringing our full kawaii lineup: plushies, stickers, blind boxes,
Pokemon TCG accessories, and exclusive items you will not find online.

Come say hi at {booth}. We would love to meet you.

More details coming soon. Stay tuned.

#kawaii #{event.lower().replace(' ', '')} #onipuni #milwaukeeshop #kawaiistore
#plushie #blindbox #pokemontcg #smallbusiness #shopsmall #milwaukeeevents
#kawaiicollector #animecollector #vendorlife #kawaiilife""")

    # Post 2: Countdown
    posts.append(f"""POST 2 - COUNTDOWN
{'=' * 40}

We are almost there. {event} is right around the corner.

Here is what we are packing for {date}:
- Rilakkuma and San-X plushies
- Original Oni-Puni sticker sets
- Mystery blind boxes
- Pokemon TCG storage and accessories
- Limited items you can only get in person

Find us at {booth}. First customers get a free sticker with purchase.

Drop a comment if you are going.

#kawaii #{event.lower().replace(' ', '')} #onipuni #milwaukeeshop #kawaiistore
#plushie #blindbox #pokemontcg #smallbusiness #shopsmall #kawaiicollector
#animecommunity #vendorbooth #kawaiiaesthetic #cutemerch""")

    # Post 3: Day of
    posts.append(f"""POST 3 - DAY OF
{'=' * 40}

We are here. {STORE_NAME} is set up at {event}, {booth}.

The booth is stocked and ready. Come through and check out everything
we brought. Plushies, stickers, blind boxes, and some surprises.

Show this post at the booth for a free sticker with any purchase.

See you today.

#kawaii #{event.lower().replace(' ', '')} #onipuni #milwaukeeshop #kawaiistore
#plushie #blindbox #pokemontcg #smallbusiness #shopsmall #liveevent
#vendorbooth #kawaiicollector #milwaukeelocal #kawaiimerch""")

    return "\n\n\n".join(posts)


def generate_email_blast_template(event, date, booth):
    """Template-based email blast."""
    return f"""SUBJECT: {STORE_NAME} is coming to {event} on {date}

PREVIEW TEXT: Come visit us at {booth}. Exclusive kawaii items, plushies, and more.

---

Hi there,

We are excited to let you know that {STORE_NAME} will be at {event} on {date}.

You can find us at {booth}. We are bringing a full selection of kawaii
collectibles, plushies, stickers, blind boxes, and Pokemon TCG accessories.

WHAT TO EXPECT:
- San-X plushies (Rilakkuma, Korilakkuma, Chairoikoguma)
- Original Oni-Puni sticker sets
- Mystery blind boxes and figurines
- Pokemon TCG deck boxes and accessories
- Event-exclusive bundle deals

EXCLUSIVE FOR EVENT VISITORS:
Mention this email at the booth and get a free sticker with any purchase
of $15 or more.

EVENT DETAILS:
- What: {event}
- When: {date}
- Where to find us: {booth}

We would love to see you there. Bring a friend, bring the whole crew.

See you soon,
Randy
{STORE_NAME}

---
Follow us: {STORE_INSTAGRAM}
Shop online: {STORE_WEBSITE}
Reply to this email with any questions."""


def generate_followup_template(event, date):
    """Template-based follow-up email."""
    return f"""SUBJECT: Thank you for visiting {STORE_NAME} at {event}

PREVIEW TEXT: Missed something at the booth? Shop online with a special discount.

---

Hey there,

Thank you for stopping by the {STORE_NAME} booth at {event} on {date}.
It was great meeting everyone and sharing our kawaii collection with you.

If you saw something you liked but did not grab it, good news:
most of our event inventory is also available in our online store.

SPECIAL OFFER:
Use code EVENT10 at checkout for 10% off your first online order.
This code is valid for 2 weeks.

Shop now: {STORE_WEBSITE}

STAY CONNECTED:
Follow us on Instagram {STORE_INSTAGRAM} for new arrivals, restocks,
and info about our next event.

If you took any photos at the booth, we would love to see them.
Tag us {STORE_INSTAGRAM} and we will share our favorites.

Thanks again for the support. See you at the next one.

Randy
{STORE_NAME}

---
Shop: {STORE_WEBSITE}
Instagram: {STORE_INSTAGRAM}
Questions? Reply to this email."""


def generate_packing_checklist(event, date, booth):
    """Generate a packing checklist for the event. Always template-based."""
    return f"""PACKING CHECKLIST: {event}
Date: {date}
Location: {booth}
{'=' * 50}

BOOTH SETUP
[ ] Table cover / tablecloth
[ ] Banner or sign with Oni-Puni branding
[ ] Business cards
[ ] Price tags or price list
[ ] Product display stands or risers
[ ] Lighting (clip-on LED if indoor)
[ ] Extension cord and power strip
[ ] Tape, zip ties, scissors, markers

PAYMENT
[ ] Phone with Square / card reader
[ ] Cash box with change ($50 in ones, $20 in fives)
[ ] Venmo/Zelle QR code printed
[ ] Receipt paper (if using printer)

INVENTORY
[ ] San-X plushies
[ ] Oni-Puni sticker sets
[ ] Blind boxes
[ ] Pokemon TCG accessories
[ ] Any event-exclusive items
[ ] Extra stock in bins under table
[ ] Inventory count sheet (track what sells)

MARKETING
[ ] QR code for email signup (printed, visible)
[ ] QR code for Instagram
[ ] Flyers for next event (if known)
[ ] Free stickers for "follow us" incentive
[ ] "Mention this post" sign for social media deal

PERSONAL
[ ] Water bottle
[ ] Snacks
[ ] Phone charger / battery pack
[ ] Comfortable shoes
[ ] Jacket or layers (convention centers can be cold)
[ ] Hand sanitizer

DAY-OF REMINDERS
[ ] Post "we are here" on Instagram and TikTok
[ ] Take photos of booth setup
[ ] Take photos/video of customers (with permission)
[ ] Track sales throughout the day
[ ] Collect email signups
[ ] Post a thank-you story at end of event

POST-EVENT
[ ] Count remaining inventory
[ ] Calculate total sales
[ ] Send follow-up email within 48 hours
[ ] Post recap content on social media
[ ] Note what sold best for next event
[ ] Restock popular items"""


def generate_qr_info(event):
    """Generate QR code setup instructions."""
    clean_event = re.sub(r'[^a-zA-Z0-9]+', '-', event.lower()).strip('-')
    return f"""QR CODE SETUP FOR EMAIL SIGNUP
{'=' * 50}

You need a QR code that links to an email signup form.
Here are 3 free options (pick whichever is easiest):

OPTION 1: GOOGLE FORMS (easiest)
1. Go to forms.google.com
2. Create a new form titled "{STORE_NAME} - Stay Connected"
3. Add fields: Name, Email, Instagram handle (optional)
4. Click Send, copy the link
5. Go to qr-code-generator.com and paste the link
6. Download and print the QR code

OPTION 2: MAILCHIMP (best for email marketing later)
1. Go to mailchimp.com and create a free account
2. Create an Audience (your email list)
3. Go to Audience > Signup forms > Form builder
4. Copy the signup form URL
5. Generate a QR code from that URL at qr-code-generator.com

OPTION 3: LINKTREE
1. Go to linktr.ee and create a free account
2. Add links to your shop, Instagram, and email signup
3. Your Linktree URL is your QR code target
4. Generate QR at qr-code-generator.com

PRINTING TIPS:
- Print at least 2 copies (one for the table, one as backup)
- Size: at least 3x3 inches so phones can scan easily
- Put it on a small stand or tape it where customers can see it
- Add text above it: "Scan for exclusive deals and new arrivals"

SUGGESTED SIGN TEXT:
    Scan to join the Oni-Puni family.
    Get first access to new drops,
    event schedules, and exclusive deals.

FREE QR CODE GENERATORS:
- qr-code-generator.com (simple, free)
- qrcode-monkey.com (free, lets you add colors)
- canva.com (free tier, can design a nice card around it)"""

# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    if len(sys.argv) < 4:
        print('Usage: python3 event_prep.py "Event Name" "Date" "Booth/Table"')
        print("")
        print("Example:")
        print('  python3 event_prep.py "Milwaukee Comic Con" "March 29" "Booth 42"')
        sys.exit(1)

    event = sys.argv[1]
    date = sys.argv[2]
    booth = sys.argv[3]

    print(f"Generating event materials for: {event}")
    print(f"Date: {date}")
    print(f"Location: {booth}")
    print("=" * 60)

    # Create output directory
    clean_event = re.sub(r'[^a-zA-Z0-9]+', '-', event.lower()).strip('-')
    event_dir = os.path.join(OUTPUT_BASE, clean_event)
    os.makedirs(event_dir, exist_ok=True)

    # Check Ollama
    using_ai = check_ollama()
    if using_ai:
        print("Ollama is running. Using AI generation.\n")
    else:
        print("Ollama is not running. Using template mode.\n")

    # ---------------------------------------------------------------------------
    # 1. Social media announcement posts (3)
    # ---------------------------------------------------------------------------
    print("Generating social media announcements...")
    if using_ai:
        announcements = generate_announcements_ai(event, date, booth)
        if not announcements:
            announcements = generate_announcements_template(event, date, booth)
    else:
        announcements = generate_announcements_template(event, date, booth)

    filepath = os.path.join(event_dir, "social-announcements.txt")
    with open(filepath, "w") as f:
        f.write(f"EVENT: {event}\nDATE: {date}\nBOOTH: {booth}\n")
        f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n")
        f.write("=" * 60 + "\n\n")
        f.write(announcements)
    print(f"  Saved: {filepath}")

    # ---------------------------------------------------------------------------
    # 2. Email blast
    # ---------------------------------------------------------------------------
    print("Generating email blast...")
    if using_ai:
        email = generate_email_blast_ai(event, date, booth)
        if not email:
            email = generate_email_blast_template(event, date, booth)
    else:
        email = generate_email_blast_template(event, date, booth)

    filepath = os.path.join(event_dir, "email-blast.txt")
    with open(filepath, "w") as f:
        f.write(email)
    print(f"  Saved: {filepath}")

    # ---------------------------------------------------------------------------
    # 3. Packing checklist
    # ---------------------------------------------------------------------------
    print("Generating packing checklist...")
    checklist = generate_packing_checklist(event, date, booth)

    filepath = os.path.join(event_dir, "packing-checklist.txt")
    with open(filepath, "w") as f:
        f.write(checklist)
    print(f"  Saved: {filepath}")

    # ---------------------------------------------------------------------------
    # 4. QR code setup guide
    # ---------------------------------------------------------------------------
    print("Generating QR code setup guide...")
    qr_info = generate_qr_info(event)

    filepath = os.path.join(event_dir, "qr-code-setup.txt")
    with open(filepath, "w") as f:
        f.write(qr_info)
    print(f"  Saved: {filepath}")

    # ---------------------------------------------------------------------------
    # 5. Post-event follow-up email
    # ---------------------------------------------------------------------------
    print("Generating follow-up email...")
    if using_ai:
        followup = generate_followup_ai(event, date)
        if not followup:
            followup = generate_followup_template(event, date)
    else:
        followup = generate_followup_template(event, date)

    filepath = os.path.join(event_dir, "followup-email.txt")
    with open(filepath, "w") as f:
        f.write(followup)
    print(f"  Saved: {filepath}")

    # ---------------------------------------------------------------------------
    # Summary
    # ---------------------------------------------------------------------------
    print("\n" + "=" * 60)
    print(f"DONE. All materials saved to: {event_dir}/")
    print("")
    print("Files created:")
    print("  social-announcements.txt  - 3 social media posts (pre-event, countdown, day-of)")
    print("  email-blast.txt           - Email to send to your list before the event")
    print("  packing-checklist.txt     - Everything to bring (check items off as you pack)")
    print("  qr-code-setup.txt        - How to create a QR code for email signups")
    print("  followup-email.txt        - Email to send within 48 hours after the event")
    print(f"\nMode: {'AI (Ollama)' if using_ai else 'Template'}")
    print("")
    print("NEXT STEPS:")
    print("1. Review and customize the social posts, then schedule them")
    print("2. Set up your QR code using the guide")
    print("3. Print the packing checklist and start packing")
    print("4. Send the email blast 5-7 days before the event")
    print("5. After the event, send the follow-up email within 48 hours")


if __name__ == "__main__":
    main()

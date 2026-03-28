# Telegram Bot for Business

**Build an automated client communication system with Python and n8n in a weekend**

**Price: $29.99**
**By Behike**

---

## Who This Guide Is For

You run a service business, a coaching practice, an e-commerce store, or any operation where you spend more than an hour a day answering the same questions, sending the same updates, and chasing down the same clients.

You are not a developer. Or maybe you are, but you want something fast.

Either way, by the end of this guide, you will have a working Telegram bot that handles client communication automatically, so you can stop being the person who responds to "what's my order status?" at 11pm.

This is not theory. Every section ends with something you can deploy.

---

## What Your Bot Can Do

Before we get into the how, here is what you are actually building:

- Auto-reply to common questions without you touching a phone
- Capture leads and store them in Google Sheets or Notion
- Send order confirmations, shipping updates, and payment receipts
- Remind clients about appointments 24 hours and 1 hour before
- Qualify new leads before they ever book a call with you
- Broadcast updates to your entire client base at once
- Gate premium content behind a subscription paywall
- Accept payments directly inside the chat

You build it once. It runs every day without you.

---

# Section 1: Why Telegram Over WhatsApp and Email

The short answer: Telegram gives you an API that actually works, open rates that make email look pathetic, and zero per-message fees.

The longer answer follows.

## Open Rates

Email open rates for business newsletters hover around 20-25% on a good day. SMS is better, around 95%, but costs money per message and has no threading or media support.

Telegram message open rates typically land between 80-90% for broadcast channels. For direct messages from a bot, it is closer to 100% because the notification hits the phone like a text message.

When you send an order confirmation via Telegram, your client sees it. When you send it via email, there is a real chance it lands in Promotions and never gets read.

## API Access

WhatsApp does have a business API. It is expensive, requires Facebook Business Manager approval, requires a verified business account, and has per-message fees after a certain volume. For a small operation it is not worth the overhead.

Telegram's Bot API is free, requires no approval, and you can set one up in under 5 minutes. There are no per-message fees at any volume. You can send photos, files, buttons, payment receipts, and inline keyboards without paying Telegram anything.

For a solo operator or small team, this is the obvious choice.

## No Fees

Telegram does not charge you to send messages. Telegram does not charge your customers to receive messages. The only costs you encounter are the server you run your bot on (Railway free tier works fine for most bots), and whatever third-party services you connect it to.

## Cross-Platform Without the Fragmentation

Telegram works on every device. Your clients can switch from phone to desktop to tablet and the conversation is there. No "I only use iMessage" problem. No "I don't have WhatsApp" problem. Telegram has 900+ million monthly active users as of 2024.

## Why Not Build on Instagram DMs or Facebook Messenger?

Platform dependency. If Facebook decides to change its API or shut down your account, your entire communication system disappears overnight. Telegram has a track record of stability and a business model that does not depend on selling your clients' data.

---

# Section 2: What Your Bot Can Do

This section maps capabilities to business problems. Find your situation and go directly to the template section that solves it.

## Auto-Replies and FAQ Handling

**Business problem:** You answer the same 10 questions every week. "Do you ship internationally?" "What's your refund policy?" "How long does delivery take?"

**What the bot does:** Detects keywords or button presses and fires the pre-written answer instantly. No delay, no copy-paste, no you.

**Who needs this:** Any e-commerce store, service provider, coach, or freelancer.

## Lead Capture

**Business problem:** Someone clicks your Instagram bio link, messages you, and you either miss it or respond 8 hours later. They have moved on.

**What the bot does:** Greets new users instantly, asks qualifying questions, stores their answers in a Google Sheet, and either qualifies them for a call or sends them to a sales page.

**Who needs this:** Coaches, consultants, service businesses, anyone running paid traffic.

## Order and Appointment Notifications

**Business problem:** Clients don't read emails. They call or message you asking for updates that you already sent.

**What the bot does:** Pushes notifications when an order ships, when an appointment is confirmed, when a payment is received. The client gets a Telegram message they will actually see.

**Who needs this:** E-commerce stores, service providers, anyone who books appointments.

## Appointment Reminders

**Business problem:** 20-30% of no-shows could have been avoided with a reminder.

**What the bot does:** Sends a reminder 24 hours before and again 1 hour before. Includes a confirmation button. If the client cancels, you are notified immediately.

**Who needs this:** Coaches, consultants, personal trainers, hair stylists, anyone who books 1:1 time.

## Broadcast Updates

**Business problem:** You need to tell 200 clients about a sale, a new product, or a schedule change.

**What the bot does:** Sends one message that goes to every subscriber immediately. No email list, no Mailchimp, no warm-up required.

**Who needs this:** Anyone with a customer base they need to communicate with regularly.

---

# Section 3: The No-Code Path (n8n + Telegram in 30 Minutes)

If you want a bot running today without writing code, this is your section. n8n is an open-source workflow automation tool that connects apps together with a visual canvas. You connect triggers to actions by drawing lines between nodes.

## What You Need

- An n8n account (cloud at n8n.io or self-hosted, free tier works)
- A Telegram bot token (from BotFather)
- 30 minutes

## Step 1: Create Your Bot Token

Open Telegram and search for `@BotFather`. Send it `/newbot`. Follow the prompts to name your bot and get a username ending in `bot`. BotFather will give you a token that looks like this:

```
7123456789:AAHdqTcvCHKSGrHzTxMXZ8ORi_yMsQ4lxRo
```

Copy this. It is your bot's API key. Do not share it publicly.

## Step 2: Set Up n8n

If you do not have n8n running, go to n8n.io and sign up for the cloud version. The free tier allows up to 5 active workflows and 2,500 executions per month, which is enough to test and run a basic bot.

For production use or more volume, you can self-host n8n on Railway or a VPS for around $5-7 per month.

## Step 3: Build the Telegram Trigger Workflow

In n8n, create a new workflow. Add a `Telegram Trigger` node. Paste your bot token. Set the update type to `message`. This node will fire every time someone sends your bot a message.

Add a `Switch` node after the trigger. Set it to check `message.text` and create cases:

- Contains `pricing` or `price` -> output 1
- Contains `booking` or `book` or `appointment` -> output 2
- Contains `help` or `start` -> output 3
- Default -> output 4

Connect each output to a `Telegram` node configured to `Send Message`. Each Telegram node sends a different reply to the chat ID that triggered the workflow.

That is a functional FAQ bot. 15 minutes of work.

## Step 4: Add a Google Sheets Lead Capture

Extend the workflow. After the `start` case, instead of just sending a reply, add a series of nodes that:

1. Send a welcome message asking for the user's name
2. Wait for their reply (use the `Telegram Trigger` node again with a filter on the chat ID)
3. Ask for their email
4. Wait for their email reply
5. Append a row to a Google Sheet with timestamp, name, email, and Telegram username

n8n has a built-in `Google Sheets` node that handles OAuth. Connect it, authorize your Google account, point it at a sheet, and map the fields.

## Step 5: Test and Activate

Click `Execute Workflow` with the workflow active. Open Telegram, find your bot, and send it `/start`. Watch the n8n execution log to see each step fire.

When it works, toggle the workflow to `Active`. It now runs 24/7 without you.

## n8n Workflow Descriptions for Key Automations

**Order Notification Workflow:**
Trigger: Webhook from Shopify or WooCommerce (order.paid event). Action: Telegram node sends a formatted message to the customer's Telegram chat ID (you need to have stored this when they first contacted your bot). Message includes order number, items, expected delivery date.

**Appointment Reminder Workflow:**
Trigger: Schedule node set to run every hour. Action: Query your Google Sheet or Airtable for appointments in the next 24 hours. For each one found, Telegram node sends reminder message. Run again for 1-hour window.

**Broadcast Workflow:**
Trigger: Manual (or schedule for weekly newsletter). Action: Google Sheets node reads all subscriber chat IDs. Loop node iterates through each one. Telegram node sends your message to each chat ID. Add a 1-second delay between messages to avoid Telegram rate limits.

---

# Section 4: The Code Path (Python telegram-bot Library)

If you want more control, or if you want to understand what is actually happening under the hood, this section walks through building a bot in Python.

## Why Python

The `python-telegram-bot` library is the most complete Telegram bot library available. It handles webhooks, polling, conversation state, inline keyboards, file uploads, and payments. The documentation is thorough. The community is large.

## Install the Library

```bash
pip install python-telegram-bot
```

## Basic Bot Structure

```python
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

BOT_TOKEN = "your-bot-token-here"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("Pricing", callback_data="pricing")],
        [InlineKeyboardButton("Book a Call", callback_data="book")],
        [InlineKeyboardButton("FAQ", callback_data="faq")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "Welcome. What do you need?",
        reply_markup=reply_markup
    )

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    responses = {
        "pricing": "Our pricing starts at $97/month. Full details at behike.com/pricing",
        "book": "Schedule a call here: calendly.com/yourlink",
        "faq": "Top questions answered at behike.com/faq",
    }

    await query.edit_message_text(responses.get(query.data, "Send /start to begin."))

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.lower()

    if any(word in text for word in ["price", "cost", "how much"]):
        await update.message.reply_text("Pricing starts at $97/month. Type /start for the full menu.")
    elif any(word in text for word in ["book", "schedule", "call", "appointment"]):
        await update.message.reply_text("Book at: calendly.com/yourlink")
    else:
        await update.message.reply_text("I can help with pricing, booking, and FAQs. Type /start.")

def main():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.run_polling()

if __name__ == "__main__":
    main()
```

Run this with `python bot.py`. Your bot is now running locally.

## Conversation State: Lead Capture Flow

The library has a `ConversationHandler` that manages multi-step conversations. This is how you build a lead qualification flow.

```python
from telegram.ext import ConversationHandler

# States
NAME, EMAIL, BUDGET = range(3)

async def start_lead(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("What's your name?")
    return NAME

async def get_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["name"] = update.message.text
    await update.message.reply_text(f"Got it, {update.message.text}. What's your email?")
    return EMAIL

async def get_email(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["email"] = update.message.text
    await update.message.reply_text("What's your monthly budget for this service? (Under $500 / $500-$2000 / Over $2000)")
    return BUDGET

async def get_budget(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["budget"] = update.message.text

    # Save to your storage here
    lead_data = {
        "name": context.user_data["name"],
        "email": context.user_data["email"],
        "budget": context.user_data["budget"],
        "telegram_id": update.effective_user.id,
        "username": update.effective_user.username,
    }
    save_lead(lead_data)  # your function

    await update.message.reply_text(
        f"Got it. We'll reach out to {context.user_data['email']} within 24 hours."
    )
    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("No problem. Type /start whenever you're ready.")
    return ConversationHandler.END

conv_handler = ConversationHandler(
    entry_points=[CommandHandler("qualify", start_lead)],
    states={
        NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_name)],
        EMAIL: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_email)],
        BUDGET: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_budget)],
    },
    fallbacks=[CommandHandler("cancel", cancel)],
)
```

## Sending Messages to Users from Outside the Bot

This is how you push order notifications. You store the user's `chat_id` when they first message your bot, then use it to send them a message whenever you want.

```python
import asyncio
from telegram import Bot

BOT_TOKEN = "your-bot-token-here"

async def send_notification(chat_id: int, message: str):
    bot = Bot(token=BOT_TOKEN)
    await bot.send_message(chat_id=chat_id, text=message)

# Call this from anywhere in your system
asyncio.run(send_notification(123456789, "Your order #1234 has shipped."))
```

Your Stripe webhook handler, your order management system, your appointment system, all of them can call this function.

## Webhooks vs Polling

Polling (`run_polling()`) is easier to set up but your bot has to constantly ask Telegram "any new messages?" Webhooks are the opposite: Telegram pushes messages to your server the moment they arrive.

For development, use polling. For production, use webhooks.

```python
# Webhook setup
async def webhook_handler(request):
    data = await request.json()
    update = Update.de_json(data, app.bot)
    await app.process_update(update)

# Configure Telegram to send updates to your URL
await app.bot.set_webhook("https://yourdomain.com/webhook")
```

---

# Section 5: Five Business Templates

## Template 1: E-Commerce Order Notifications

**Use case:** Automatically notify customers when their order is placed, when it ships, and when it is delivered.

**Setup:**
1. Create a bot and store the customer's `chat_id` during checkout (add a Telegram opt-in to your checkout flow).
2. Connect your Shopify or WooCommerce webhook to a Python script or n8n workflow.
3. When the webhook fires, look up the customer's `chat_id` from your database and send the appropriate message.

**Messages to send:**
- Order confirmed: "Order #[number] confirmed. Total: $[amount]. We'll notify you when it ships."
- Shipped: "Your order is on the way. Tracking: [link]. Expected delivery: [date]."
- Delivered: "Your order was delivered. Questions? Reply here or visit [support link]."

**n8n workflow:** Shopify Trigger -> Switch (order status) -> Google Sheets (lookup chat_id) -> Telegram (send message)

## Template 2: Coaching Bot

**Use case:** Qualify leads before they book a discovery call. Only serious people get your calendar link.

**Qualification questions:**
1. What is your biggest challenge right now?
2. How long have you been dealing with this?
3. What have you already tried?
4. What is your timeline for solving this?
5. What is your budget range for coaching?

**Bot logic:**

```python
CHALLENGE, TIMELINE, BUDGET, TRIED = range(4)

# Budget qualifier
async def get_budget(update: Update, context: ContextTypes.DEFAULT_TYPE):
    budget = update.message.text
    context.user_data["budget"] = budget

    # Qualify or disqualify based on budget
    if "500" in budget or "1000" in budget or "over" in budget.lower():
        await update.message.reply_text(
            "You're a good fit. Here's the calendar link: calendly.com/yourlink"
        )
        # Notify yourself
        await send_notification(YOUR_CHAT_ID, f"Qualified lead: {context.user_data}")
    else:
        await update.message.reply_text(
            "The program starts at $500/month. If that changes, type /start to reapply."
        )

    return ConversationHandler.END
```

**Where leads go:** Google Sheets row with all answers, timestamp, and Telegram username. Your CRM if you have one via a webhook.

## Template 3: Service Booking Bot

**Use case:** Let clients browse services, see availability, and book without needing to talk to you.

**Flow:**
1. Client types /start
2. Bot shows service menu (Inline Keyboard: Consultation / Website Audit / Monthly Retainer)
3. Client selects a service
4. Bot shows available time slots for the next 7 days
5. Client selects a slot
6. Bot confirms the booking and sends a calendar invite link
7. You get a notification with the booking details

**Availability check:** Store your available slots in a Google Sheet. The bot reads the sheet to show what is open. When a slot is booked, it marks it as taken.

**Reminder flow:** Store the booking with the client's `chat_id`. A scheduled script runs hourly and sends reminders when appointments are within 24 hours or 1 hour.

```python
# Reminder script (run with cron or Railway cron job)
import gspread
from datetime import datetime, timedelta

def check_and_send_reminders():
    gc = gspread.service_account(filename="service-account.json")
    sheet = gc.open("Bookings").sheet1
    bookings = sheet.get_all_records()

    now = datetime.now()

    for booking in bookings:
        apt_time = datetime.fromisoformat(booking["datetime"])
        time_until = apt_time - now
        chat_id = int(booking["chat_id"])

        if timedelta(hours=23) < time_until <= timedelta(hours=25):
            asyncio.run(send_notification(
                chat_id,
                f"Reminder: Your appointment is tomorrow at {apt_time.strftime('%I:%M %p')}."
            ))

        if timedelta(minutes=55) < time_until <= timedelta(hours=1, minutes=5):
            asyncio.run(send_notification(
                chat_id,
                f"Your appointment is in 1 hour. Join at: [your video link]"
            ))
```

## Template 4: FAQ Bot

**Use case:** Handle the 10 questions you answer every week without human intervention.

**Build your FAQ map:**

```python
FAQ = {
    "refund": "We offer full refunds within 14 days of purchase. Email refunds@yourcompany.com.",
    "shipping": "We ship to the US and Canada. Delivery takes 5-7 business days.",
    "international": "We currently only ship within the US and Canada.",
    "payment": "We accept all major credit cards, PayPal, and bank transfer.",
    "support": "Support is available Monday-Friday, 9am-5pm EST. Reply here or email support@yourcompany.com.",
    "affiliate": "Our affiliate program pays 30% recurring. Apply at yourcompany.com/affiliate.",
    "discount": "Sign up for our newsletter at yourcompany.com for early access to promotions.",
    "custom": "Custom orders are available for quantities over 50. Email custom@yourcompany.com.",
    "return": "Return process is at yourcompany.com/returns. Items must be unused and in original packaging.",
    "tracking": "Your tracking number was emailed to you. Check spam or reply with your order number.",
}

async def handle_faq(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.lower()

    for keyword, answer in FAQ.items():
        if keyword in text:
            await update.message.reply_text(answer)
            return

    # No match: escalate to human
    await update.message.reply_text(
        "I don't have an answer for that. A human will respond within 4 hours. "
        "For urgent issues: support@yourcompany.com"
    )
    # Notify you
    await send_notification(
        YOUR_CHAT_ID,
        f"Unhandled question from @{update.effective_user.username}: {update.message.text}"
    )
```

## Template 5: Lead Qualifier

**Use case:** You run ads or have a high-traffic website. You need to filter serious buyers from tire-kickers before they hit your calendar.

**Qualification criteria (customize for your business):**
- Revenue or budget threshold
- Timeline (are they buying now or "just looking")
- Decision-making authority (can they say yes without approval)
- Fit with your service

**Scoring system:**

```python
def calculate_score(user_data: dict) -> int:
    score = 0

    # Budget
    if "2000" in user_data.get("budget", "") or "over" in user_data.get("budget", "").lower():
        score += 40
    elif "500" in user_data.get("budget", ""):
        score += 20

    # Timeline
    if "immediately" in user_data.get("timeline", "").lower() or "now" in user_data.get("timeline", "").lower():
        score += 30
    elif "month" in user_data.get("timeline", "").lower():
        score += 15

    # Decision maker
    if "yes" in user_data.get("decision_maker", "").lower():
        score += 30

    return score

async def qualify_result(update: Update, context: ContextTypes.DEFAULT_TYPE):
    score = calculate_score(context.user_data)

    if score >= 70:
        await update.message.reply_text(
            "You're a strong fit. Here's the link to book a strategy call: calendly.com/yourlink"
        )
        await send_notification(YOUR_CHAT_ID, f"HOT LEAD (score: {score}): {context.user_data}")
    elif score >= 40:
        await update.message.reply_text(
            "You might be a fit. We'll review your answers and reach out within 48 hours."
        )
        await send_notification(YOUR_CHAT_ID, f"Warm lead (score: {score}): {context.user_data}")
    else:
        await update.message.reply_text(
            "We may not be the right fit right now. Check out our free resources at behike.com/free."
        )

    return ConversationHandler.END
```

---

# Section 6: Connecting to Your Stack

## Stripe Webhooks

When a payment succeeds on Stripe, you can send an immediate Telegram confirmation to the buyer.

```python
from flask import Flask, request
import stripe
import asyncio

app = Flask(__name__)
stripe.api_key = "sk_live_..."
STRIPE_WEBHOOK_SECRET = "whsec_..."

@app.route("/stripe-webhook", methods=["POST"])
def stripe_webhook():
    payload = request.data
    sig_header = request.headers.get("Stripe-Signature")

    try:
        event = stripe.Webhook.construct_event(payload, sig_header, STRIPE_WEBHOOK_SECRET)
    except Exception:
        return "Invalid signature", 400

    if event["type"] == "payment_intent.succeeded":
        payment = event["data"]["object"]
        customer_telegram_id = payment.get("metadata", {}).get("telegram_id")
        amount = payment["amount"] / 100

        if customer_telegram_id:
            asyncio.run(send_notification(
                int(customer_telegram_id),
                f"Payment confirmed: ${amount:.2f}. Thank you. Your access link: [link]"
            ))

    return "ok", 200
```

**How to get the Telegram ID into Stripe metadata:** When your customer starts the checkout process through your Telegram bot, your bot already has their `chat_id`. Pass that ID as metadata when you create the Stripe payment link or session.

## Google Sheets

Google Sheets works as a simple database for leads, bookings, and subscriber lists. The `gspread` library handles the connection.

```bash
pip install gspread google-auth
```

```python
import gspread
from google.oauth2.service_account import Credentials

SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]
creds = Credentials.from_service_account_file("service-account.json", scopes=SCOPES)
gc = gspread.authorize(creds)

def save_lead(lead_data: dict):
    sheet = gc.open("Leads").sheet1
    sheet.append_row([
        lead_data.get("name"),
        lead_data.get("email"),
        lead_data.get("telegram_id"),
        lead_data.get("username"),
        lead_data.get("budget"),
        str(datetime.now()),
    ])

def get_subscribers() -> list:
    sheet = gc.open("Subscribers").sheet1
    records = sheet.get_all_records()
    return [r["chat_id"] for r in records if r.get("active") == "yes"]
```

**Get your service account JSON:** Go to Google Cloud Console, create a project, enable the Sheets API, create a service account, download the JSON key, and share your Google Sheet with the service account email.

## Notion

If you prefer Notion as your database:

```bash
pip install notion-client
```

```python
from notion_client import Client

notion = Client(auth="your-notion-integration-token")
DATABASE_ID = "your-database-id"

def save_lead_to_notion(lead_data: dict):
    notion.pages.create(
        parent={"database_id": DATABASE_ID},
        properties={
            "Name": {"title": [{"text": {"content": lead_data["name"]}}]},
            "Email": {"email": lead_data["email"]},
            "Budget": {"rich_text": [{"text": {"content": lead_data["budget"]}}]},
            "Telegram ID": {"number": lead_data["telegram_id"]},
            "Status": {"select": {"name": "New"}},
        }
    )
```

**Setup:** In Notion, create an integration at notion.so/my-integrations. Copy the token. Share your database with the integration (Add connections from the database settings).

## Airtable

```bash
pip install pyairtable
```

```python
from pyairtable import Api

api = Api("your-airtable-api-key")
table = api.table("your-base-id", "Leads")

def save_to_airtable(lead_data: dict):
    table.create({
        "Name": lead_data["name"],
        "Email": lead_data["email"],
        "Budget": lead_data["budget"],
        "Telegram ID": str(lead_data["telegram_id"]),
        "Source": "Telegram Bot",
    })
```

---

# Section 7: Deployment and Hosting

Your bot needs to run 24/7. Here are the options from free to paid.

## Railway (Recommended for Most People)

Railway is the fastest path from working code to a live bot. It handles the server setup, environment variables, and auto-restarts if your bot crashes.

**Steps:**
1. Push your bot code to a GitHub repository
2. Go to railway.app and create a new project
3. Connect your GitHub repo
4. Add your bot token as an environment variable: `BOT_TOKEN=your-token-here`
5. Railway detects Python and builds automatically
6. Your bot is live

**Cost:** Railway's free tier gives you $5 of credit per month. A simple polling bot uses about $1-2/month. Paid plans start at $5/month for more resources.

**Procfile (tells Railway how to start your bot):**

```
worker: python bot.py
```

**requirements.txt:**

```
python-telegram-bot==20.7
gspread==6.0.0
google-auth==2.28.0
flask==3.0.0
stripe==8.5.0
```

## Environment Variables

Never put your bot token or API keys directly in your code. Use environment variables.

```python
import os
from dotenv import load_dotenv

load_dotenv()  # loads .env file locally
BOT_TOKEN = os.getenv("BOT_TOKEN")
STRIPE_KEY = os.getenv("STRIPE_API_KEY")
NOTION_TOKEN = os.getenv("NOTION_TOKEN")
```

Create a `.env` file locally (add it to `.gitignore` so it never gets pushed to GitHub):

```
BOT_TOKEN=7123456789:AAHdqTcvCHKSGrHzTxMXZ8ORi_yMsQ4lxRo
STRIPE_API_KEY=sk_live_...
NOTION_TOKEN=secret_...
```

In Railway, set these in the Variables tab of your project settings.

## VPS (More Control, More Work)

A $6/month VPS on DigitalOcean or Hetzner (Hetzner is cheaper, roughly 4 EUR/month for a basic instance) gives you a server you fully control.

**Basic VPS deployment:**

```bash
# On your VPS
sudo apt update && sudo apt install python3-pip python3-venv -y

# Clone your repo
git clone https://github.com/youruser/your-bot.git
cd your-bot

# Set up virtual environment
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Create .env file
nano .env
# paste your variables

# Run with PM2 or systemd to keep it alive
pip install pm2
pm2 start bot.py --interpreter python3
pm2 startup
pm2 save
```

## Free Options

**Replit:** Has a free tier with Always On for bots. Works for testing, unreliable for production.

**PythonAnywhere:** Free tier allows always-on tasks for simple bots. Limited CPU.

**Fly.io:** Free tier with 3 shared-CPU VMs. More setup than Railway but free.

For anything you care about, Railway is the right default. The cost at low volume is near zero.

---

# Section 8: Growing Your Telegram Audience

Having a bot is one thing. Having 1,000 people in your Telegram ecosystem is another. This section covers how to build the audience.

## Channel vs Group vs Bot: What to Use

**Bot:** Individual automated conversations. The lead qualifier, the FAQ responder, the order notification system. One-on-one, private.

**Channel:** Broadcast tool. You post, subscribers receive. They cannot reply (unless you enable comments). Best for announcements, content, offers.

**Group:** Community space. Everyone can talk to each other. Best for paid communities, support groups, high-engagement niches.

Most businesses need all three. The bot handles automation. The channel handles broadcasts. The group handles community.

## Strategy: Funnel Into Telegram

The goal is to move people off platforms you do not own (Instagram, TikTok) onto Telegram, which you control.

**Tactics:**

- Put your bot link in every Instagram bio, LinkedIn profile, and Twitter/X profile
- End every piece of content with "Get [specific valuable thing] by messaging me on Telegram: [link]"
- Offer a lead magnet exclusively on Telegram. Not your website, not your email list. Telegram only.
- Every Gumroad purchase triggers a Telegram notification asking them to join your channel for updates
- Add a Telegram opt-in step to your checkout flow

**Link format:** `t.me/yourbotusername` for bots. `t.me/yourchannelname` for channels.

## Content Strategy for Your Channel

Post on a schedule. Telegram channels with consistent posting retain subscribers. Sporadic posting leads to exits.

A simple schedule that works:
- Monday: Tip or tutorial related to your niche
- Wednesday: Behind-the-scenes or case study
- Friday: Offer, promotion, or round-up

Keep posts short. Telegram is not a blog. A 3-sentence tip with a link performs better than a 500-word essay.

## Broadcast Without Spam

Telegram users can silence channels with one tap. If you send too much or post irrelevant content, they mute you permanently.

Rules:
- Send no more than once per day on a channel
- Every post must give value or be clearly labeled as a promotion
- Treat your Telegram audience like your best customers, not a marketing list

---

# Section 9: Monetization

Your Telegram ecosystem can generate revenue directly, separate from whatever product you are already selling.

## Paid Channels

Telegram does not natively support paid subscriptions (in most regions), but you can gate access manually or with a bot.

**Manual method:** Charge via Stripe or Gumroad. When payment is confirmed, manually add the person to a private channel or group. This does not scale past 100 members.

**Bot-gated method:** Use a bot that validates payment before generating a one-time invite link.

```python
async def check_payment(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    # Check your database for this user's payment status
    is_paid = check_paid_status(user_id)  # your function

    if is_paid:
        # Generate invite link (expires after 1 use)
        invite_link = await context.bot.create_chat_invite_link(
            chat_id=PRIVATE_CHANNEL_ID,
            member_limit=1,
            expire_date=datetime.now() + timedelta(hours=1),
        )
        await update.message.reply_text(f"Access link (expires in 1 hour): {invite_link.invite_link}")
    else:
        await update.message.reply_text("Subscribe here: [your payment link]")
```

## Telegram Payments (Native)

Telegram has a native payments system that works in 30+ countries via Stripe. Users pay directly inside the chat without leaving Telegram.

```python
from telegram import LabeledPrice

async def send_invoice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_invoice(
        chat_id=update.effective_chat.id,
        title="Telegram Bot Business Guide",
        description="Build an automated client communication system in a weekend.",
        payload="tgbot-guide-purchase",
        provider_token="your-stripe-payment-provider-token",
        currency="USD",
        prices=[LabeledPrice("Telegram Bot Business Guide", 2999)],  # 2999 cents = $29.99
        protect_content=True,
    )

async def pre_checkout(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.pre_checkout_query
    await query.answer(ok=True)

async def successful_payment(update: Update, context: ContextTypes.DEFAULT_TYPE):
    payment = update.message.successful_payment
    await update.message.reply_text(
        "Payment confirmed. Your download link: [link]"
    )
    # Save purchase to your database here
```

Get your payment provider token from BotFather: `/mybots` -> Your Bot -> Payments -> Connect provider.

## Subscriber Gating for Content

Build a model where free content is available to anyone who follows your channel, but deep-dive tutorials, templates, or tools require a paid subscription.

The flow:
1. Post valuable free content on your public channel
2. End each post with "Full tutorial (with code templates) is in the Pro channel: [join link]"
3. The join link leads to the bot
4. Bot checks payment status or sends a payment link
5. Paid users get the invite link to the private channel

This is a recurring revenue model built entirely on Telegram.

---

## Next Steps

You have the full picture. Here is what to do in order:

1. Create your bot token with BotFather (5 minutes)
2. Choose your path: n8n for no-code, Python for code
3. Pick the one template that matches your most painful communication problem right now
4. Build that template first. Get it working. Deploy it.
5. Connect it to your actual data source (Google Sheets is the fastest starting point)
6. Deploy to Railway
7. Start sending your existing clients and leads the bot link

The goal is not to build all nine automations this weekend. The goal is to have one thing running by Sunday that handles a task you currently do manually every day.

Once one workflow is live and you feel how it runs, the next five take half the time.

Build the thing.

---

*Telegram Bot for Business is a Behike product. For questions, support, or community access, find us on Telegram: t.me/behikeai*

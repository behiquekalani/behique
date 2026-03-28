# Behike n8n Automation Pack

15 ready-to-import n8n workflows for solopreneurs, digital product sellers, and one-person businesses. Built for the Behike ecosystem but works for any creator running a lean operation.

Import any workflow in n8n via Settings > Import Workflow. Replace all `YOUR_X_HERE` placeholders with your actual credentials before activating.

---

## The 15 Workflows

### Original 5

**1. lead-capture.json**
Captures leads from a landing page form, logs them to Google Sheets, tags them in ConvertKit, and sends a Telegram ping.
Credentials needed: Google Sheets OAuth2, ConvertKit API, Telegram Bot
Estimated setup time: 15 minutes

**2. new-sale-notification.json**
Fires on every Gumroad purchase via webhook. Sends Telegram alert, logs to Airtable, and tags buyer in ConvertKit.
Credentials needed: Gumroad webhook, Airtable Token, ConvertKit API, Telegram Bot
Estimated setup time: 10 minutes

**3. weekly-revenue-report.json**
Runs every Monday morning. Pulls 7-day sales data from Gumroad, calculates week-over-week growth, sends formatted report to Telegram.
Credentials needed: Gumroad API, Telegram Bot
Estimated setup time: 10 minutes

**4. content-scheduler.json**
Takes a spreadsheet of content ideas and auto-schedules posts via Buffer API across Twitter, Instagram, and LinkedIn.
Credentials needed: Google Sheets OAuth2, Buffer API Token
Estimated setup time: 20 minutes

**5. abandoned-cart-followup.json**
Detects Gumroad checkout attempts that did not complete. Triggers a 2-email follow-up sequence 1 hour and 24 hours later.
Credentials needed: Gumroad webhook, Gmail OAuth2
Estimated setup time: 20 minutes

---

### New 10

**6. client-onboarding.json**
Fires when a new client submits an intake form via webhook. Logs client to Google Sheets, sends a welcome email, creates a Notion page with client details, and notifies you on Telegram.
Credentials needed: Google Sheets OAuth2, Gmail OAuth2, Notion API, Telegram Bot
Estimated setup time: 25 minutes

**7. invoice-generator.json**
Runs automatically on the 1st of every month. Pulls active clients from Google Sheets, calculates invoices including optional tax, sends HTML invoices via Gmail, logs everything to Airtable.
Credentials needed: Google Sheets OAuth2, Gmail OAuth2, Airtable Token
Estimated setup time: 30 minutes

**8. content-repurpose.json**
Monitors your RSS feed for new posts. When one drops, uses GPT-4o-mini to generate a Twitter thread, LinkedIn post, and Instagram caption. Schedules all three via Buffer API automatically.
Credentials needed: OpenAI API, Buffer API Token
Estimated setup time: 20 minutes

**9. ebay-listing-monitor.json**
Runs every 6 hours. Hits the eBay Finding API to scan for your target products, filters for price drops below your threshold, logs results to Google Sheets, and sends a Telegram alert when something hits.
Credentials needed: eBay App ID, Google Sheets OAuth2, Telegram Bot
Estimated setup time: 25 minutes

**10. email-list-cleanup.json**
Runs every Sunday. Fetches ConvertKit subscribers inactive for 60+ days, sends a re-engagement email, waits 3 days, then removes non-openers. Logs all removed subscribers to Google Sheets for your records.
Credentials needed: ConvertKit API Secret, Gmail OAuth2, Google Sheets OAuth2
Estimated setup time: 20 minutes

**11. social-proof-collector.json**
Triggered by Gumroad's ping webhook on purchase. Waits 3 days, then sends a personal testimonial request email. Logs outreach to Airtable. When replies come in, saves testimonials to a Notion database.
Credentials needed: Gumroad webhook, Gmail OAuth2, Airtable Token, Notion API
Estimated setup time: 25 minutes

**12. product-launch-sequence.json**
Manual trigger you fire yourself when launching a product. Tags your list in ConvertKit, sends 3 emails over 72 hours (announcement, story, close), then logs the completed launch to Airtable. Email content is passed via the webhook body so you can customize per launch.
Credentials needed: ConvertKit API Secret, Gmail OAuth2, Airtable Token
Estimated setup time: 30 minutes

**13. reddit-monitor.json**
Runs every 2 hours. Searches Reddit for keywords: "digital products", "solopreneur", "AI tools", "passive income", "n8n automation". Scores posts by engagement, filters to top 5, sends a digest to Telegram. Good for finding content angles and communities to engage.
Credentials needed: Reddit OAuth2 App, Telegram Bot
Estimated setup time: 30 minutes

**14. gumroad-analytics.json**
Runs every morning at 8am. Fetches yesterday's Gumroad sales, calculates total revenue, average order value, and top product, sends a morning report to Telegram, and logs daily metrics to Google Sheets for trend tracking.
Credentials needed: Gumroad API Access Token, Telegram Bot, Google Sheets OAuth2
Estimated setup time: 15 minutes

**15. support-triage.json**
Monitors your support inbox via Gmail trigger. When a new email arrives, GPT-4o-mini classifies it as REFUND, QUESTION, BUG, or FEEDBACK. Routes to category-specific auto-reply drafts, logs every ticket to a Notion database, and sends you a Telegram alert for refunds and bug reports.
Credentials needed: Gmail OAuth2, OpenAI API, Notion API, Telegram Bot
Estimated setup time: 35 minutes

---

## Credential Setup Order

If you are setting this up from scratch, connect credentials in this order to avoid repeated work:

1. Gmail OAuth2 (used in 8 workflows)
2. Telegram Bot (used in 7 workflows)
3. Google Sheets OAuth2 (used in 6 workflows)
4. OpenAI API (used in 3 workflows)
5. Gumroad API Token (used in 3 workflows)
6. Notion API (used in 3 workflows)
7. ConvertKit API Secret (used in 3 workflows)
8. Airtable Token (used in 3 workflows)
9. eBay App ID (used in 1 workflow)
10. Reddit OAuth2 App (used in 1 workflow)
11. Buffer API Token (used in 2 workflows)

---

## Quick Tips

Every placeholder follows the pattern `YOUR_X_HERE`. Run a search for that string after import to find everything that needs filling in before you activate.

The workflows with Wait nodes (email-list-cleanup, social-proof-collector, product-launch-sequence) will hold execution state between runs. Make sure your n8n instance stays online or use n8n Cloud.

The Reddit and eBay monitors use public/semi-public APIs. Check rate limits if you run multiple instances.

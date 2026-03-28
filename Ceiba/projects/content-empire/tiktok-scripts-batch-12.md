# TikTok Scripts — Batch 12
# Topic: n8n Automation Tutorial Clips
# Brand: Behike
# 5 Scripts | 60-90 seconds each

---

### Script 1 — What n8n Is and Why Nobody Is Talking About It

**Hook (0-3s):** This free tool automates things that would cost you $500 a month in software.

**Setup (3-10s):** It's called n8n. It's open source. And it's the most powerful automation tool most people have never heard of.

**Content (10-55s):**
n8n is like Zapier but you self-host it. Which means no per-task pricing. Which means unlimited automations for free.

Here's what it can do:
When someone fills out a form, it automatically creates a row in your spreadsheet, sends them a welcome email, adds them to your CRM, and pings you on Telegram. All at once. Zero manual work.

You connect apps using visual blocks called nodes. Each node does one thing. You chain them together.

The three things beginners use it for:
1. Lead capture to email list automation
2. Social media post scheduling from Notion
3. Daily digest alerts from RSS feeds

You don't need to code. You drag, drop, connect. If you get stuck, there's a community of 50k people who will help you.

The learning curve is one weekend. The time saved is forever.

**CTA (55-60s):** Follow. Next video shows you how to build your first workflow in under 10 minutes.

**On-screen text:** "n8n = free Zapier you own" / "No per-task pricing" / "Visual automation builder"

**Trending sound direction:** Tech-forward background music, slightly upbeat, clean and focused feel

---

### Script 2 — Build This n8n Workflow in 10 Minutes (Lead to Email)

**Hook (0-3s):** Every time someone downloads your free thing, this workflow handles everything automatically.

**Setup (3-10s):** Lead capture to welcome email, no code, ten minutes to build.

**Content (10-55s):**
Here's exactly what we're building.
Someone fills out your Tally form. n8n picks it up. It adds them to your Brevo email list. It sends them the download link. It logs their info in a Google Sheet. Done.

Step 1 — Open n8n. Create a new workflow.
Step 2 — Add a Webhook node. Copy the URL into your Tally form settings.
Step 3 — Add a Google Sheets node. Connect your account. Map the fields from the form to the sheet columns.
Step 4 — Add a Brevo node. Map the email field. Select your list.
Step 5 — Add a Send Email node. Write your welcome message. Include the download link as a variable.
Step 6 — Hit activate. Test it with your own email.

Total nodes: 4. Total time: under 10 minutes.
Every new subscriber triggers the whole chain automatically.

**CTA (55-60s):** Comment "workflow" and I'll drop the template link.

**On-screen text:** "Tally form to email list in 10 min" / "n8n free automation" / "No code"

**Trending sound direction:** Clean tutorial energy, mid-tempo, focus-friendly, no lyrics

---

### Script 3 — How to Get Daily AI News Summaries Without Lifting a Finger

**Hook (0-3s):** Every morning I get a summary of the top AI news. I never read a single article. n8n does it for me.

**Setup (3-10s):** This is the RSS to Telegram digest workflow. You can build it in 15 minutes.

**Content (10-55s):**
What it does:
Every morning at 8am, n8n pulls the latest posts from five AI news RSS feeds. It sends each headline and summary to a private Telegram channel you control. You read it in 2 minutes instead of 45.

How to build it:
Step 1 — Cron node. Set it to trigger every day at 8am.
Step 2 — RSS Feed node. Add the feed URLs for your sources. I use TechCrunch AI, The Verge AI, and Hugging Face blog.
Step 3 — Code node. Write a short loop that formats each item as a clean message.
Step 4 — Telegram node. Connect your bot. Point it to your channel. Send the formatted message.

That's four nodes. The Code node is the only one that needs one line of JavaScript, which ChatGPT will write for you in ten seconds.

Now you are always informed. And you never wasted time doomscrolling to get there.

**CTA (55-60s):** Want the exact code block. Drop a comment and I'll share it.

**On-screen text:** "AI news to Telegram every morning" / "4 nodes only" / "Wake up informed"

**Trending sound direction:** Morning energy, slightly warm and calm, no lyrics, lo-fi feel

---

### Script 4 — Automate Your Content Pipeline With n8n and Notion

**Hook (0-3s):** I plan my content in Notion. It publishes everywhere automatically. Here's how.

**Setup (3-10s):** This is for creators who batch their content but hate the manual copy-paste work afterward.

**Content (10-55s):**
The workflow:
You write your post in a Notion database. You add a "Status" property and set it to "Ready to Post." n8n detects the change. It pulls the content. It formats it for each platform. It queues it in Buffer or posts directly.

How to set it up:
Step 1 — Notion trigger node. Watch for rows where Status = "Ready to Post."
Step 2 — Set node. Pull the Title, Body, Image URL from the Notion properties.
Step 3 — HTTP Request node pointing to Buffer API. Pass the content as the post body.
Step 4 — Update the Notion row status to "Posted." No double posting.

Optional add-on: add an AI node in between that rewrites the post for each platform's tone. Twitter version is shorter. LinkedIn version adds context.

One place to write. Every platform covered. Zero manual work.

**CTA (55-60s):** Follow for the Notion template that pairs with this workflow.

**On-screen text:** "Write once, post everywhere" / "Notion + n8n" / "No manual copy-paste"

**Trending sound direction:** Focused and productive, slightly faster pace, background instrumental

---

### Script 5 — The n8n Workflow That Makes Me Money While I Sleep

**Hook (0-3s):** This workflow processes orders, sends products, and emails receipts while I am asleep.

**Setup (3-10s):** If you sell digital products, this is the most important workflow you can build.

**Content (10-55s):**
What happens when someone buys your Gumroad product:
Gumroad fires a webhook.
n8n catches it.
It logs the sale in Google Sheets.
It sends a custom onboarding email with the product link.
It adds the buyer to your email list in Brevo.
It sends you a Telegram notification so you know a sale happened.

This entire sequence runs in under 30 seconds.

How to build it:
Step 1 — Webhook node. Get the URL, paste it in Gumroad's webhook settings.
Step 2 — Google Sheets node. Log buyer name, email, product, date.
Step 3 — Brevo node. Add to your buyers-only email list.
Step 4 — Gmail or SMTP node. Send your custom onboarding email.
Step 5 — Telegram node. Send yourself "New sale: [product] from [email]."

Six nodes. One workflow. Your whole fulfillment pipeline runs itself.

**CTA (55-60s):** Save this. When you make your first sale, you'll want this already built.

**On-screen text:** "Gumroad + n8n = automated fulfillment" / "6 nodes" / "Runs while you sleep"

**Trending sound direction:** Calm nighttime energy, soft electronic background, "set it and forget it" vibe

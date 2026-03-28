---
title: "X/Twitter Threads Batch 3"
type: content
tags: [twitter, x, threads, content]
created: 2026-03-22
---

# X/Twitter Thread Templates Batch 3
# Accounts: @kalaniandrez and @behikeai
# Voice: Behike Voice Bible. Short. Direct. Thesis-first. No em dashes.

---

## THREAD 1: The eBay Arbitrage Math Nobody Shows You
**Account:** @kalaniandrez
**Hook:** "eBay arbitrage sounds simple. The math that makes it work is not. Here it is."

---

eBay arbitrage sounds simple. The math that makes it work is not.

Here it is.

---

Most people hear "buy low, sell high" and think that's the whole strategy.

It isn't. The margin you see before fees is not the margin you keep.

Here's what the numbers actually look like.

---

The cost breakdown on a $40 sale:

Sale price: $40.00
eBay final value fee (12.9%): $5.16
Payment processing (2.9% + $0.30): $1.46
Shipping (padded envelope, tracked): $5.50
Packaging materials: $0.75
Cost of item: $18.00

Net profit: $9.13
Net margin: 22.8%

That's a losing product. The cutoff is 25% net.

---

The same math on a better product:

Sale price: $35.00
eBay fee (12.9%): $4.52
Payment processing: $1.32
Shipping (small, lightweight): $3.80
Packaging: $0.50
Cost of item: $10.00

Net profit: $14.86
Net margin: 42.5%

Same platform. Better product selection. Nearly double the margin.

The variable that matters most is item weight and size. Light products ship cheap. That's where the margin lives.

---

Three product categories with consistently strong margins:

1. Small electronics accessories. Phone cases, cables, adapters. Source at $3-6. Sell at $18-28. Light. No fragile shipping issues.

2. Vintage or collectible items. No direct sourcing cost beyond time. Margins of 60-80% are normal if you know what to look for.

3. Niche hobby supplies. RC parts, fishing lures, specific tool accessories. Low competition. Buyers are motivated. Margins hold at 35-50%.

---

What disqualifies a product immediately:

Heavy items where shipping eats 20%+ of sale price.
Anything that competes with 50+ identical listings at lower prices.
Items that require returns. Returns kill margin fast.

---

The 25% net rule is the filter. Run every product through the full fee breakdown before buying.

If the math doesn't work on paper, it won't work in practice. The market doesn't care about your buying price. It only cares about what it will pay.

---

I broke down the full sourcing and listing process, including fee calculators and product filters, in the eBay Dropshipping Guide.

If you're building an eBay reselling operation, start here.

https://behikeai.gumroad.com/l/ebay-dropshipping-guide

---

## THREAD 2: 7 Python Tools I Use Every Day (All Free)
**Account:** @behikeai
**Hook:** "7 Python libraries. $0/month. The full AI automation stack I run on old laptops."

---

7 Python libraries. $0/month.

The full AI automation stack I run on old laptops.

---

You do not need a paid SaaS subscription for every part of your automation stack.

Most of what you need is already in Python, open-source, and maintained by thousands of contributors.

Here are the 7 I use every day.

---

1. trafilatura

pip install trafilatura

What it does: Scrapes web pages and extracts clean text. Strips ads, navigation, and boilerplate automatically.

What I use it for: Pulling product descriptions, article content, and competitor pages into my pipelines. Better output than BeautifulSoup for most sites.

---

2. fpdf2

pip install fpdf2

What it does: Generates PDF files programmatically from Python.

What I use it for: Building digital products. Feed it structured content, get a formatted PDF out. All 9 Behike guides were assembled this way.

---

3. python-telegram-bot

pip install python-telegram-bot

What it does: Full Telegram bot API wrapper. Handles messages, commands, inline keyboards, file uploads.

What I use it for: BehiqueBot, my personal accountability bot. Also the intake layer for my idea capture system. Runs 24/7 on Railway for free.

---

4. ollama Python client

pip install ollama

What it does: Connects your Python scripts to locally running LLMs via the Ollama server.

What I use it for: Running inference locally on Cobo (GTX 1080 Ti). Zero API costs. I use qwen2.5:7b for classification, summarization, and drafting tasks.

---

5. schedule

pip install schedule

What it does: Cron-style job scheduler in pure Python. No system cron setup needed.

What I use it for: Running the morning briefing at 7am, the news tracker at 9am, and nightly vault backups. Lightweight and readable.

---

6. python-dotenv

pip install python-dotenv

What it does: Loads environment variables from a .env file into your script.

What I use it for: Every single project. Secrets never go in code. API keys, tokens, passwords all live in .env files that stay out of git.

---

7. requests

pip install requests

What it does: HTTP calls. GET, POST, headers, auth, params. The standard for interacting with any API in Python.

What I use it for: Pulling data from eBay, Reddit, RSS feeds, Notion API, and any webhook endpoint. The backbone of every data pipeline.

---

These 7 libraries cover: web scraping, PDF generation, bot deployment, local AI, scheduling, secret management, and API calls.

That is a complete automation stack. $0/month.

Full guide on how I connect all of this into a working AI employee system:

https://behikeai.gumroad.com/l/ai-employee-guide

---

## THREAD 3: The $0 Tech Stack for a Digital Product Business
**Account:** @kalaniandrez
**Hook:** "You don't need Shopify. You don't need MailChimp. Here's what I use instead."

---

You don't need Shopify. You don't need MailChimp.

Here's what I use instead.

---

The standard advice for starting a digital product business: Shopify ($39/mo), ConvertKit ($29/mo), Canva Pro ($15/mo), a custom domain ($15/yr), maybe a course platform ($99/mo).

That's $180+ per month before you've made a single sale.

I run the same business for $20/month total.

---

Payments and product delivery: Gumroad

Free to start. They take 10% per sale, not a monthly fee.

That means $0 in month 1 whether you sell 0 or 100 units. You only pay when you earn.

I have 9 products live. No monthly subscription until I'm consistently above $2,000/month in sales.

---

Hosting: GitHub Pages or Cloudflare Tunnel

GitHub Pages: deploy a static HTML site from a repo. Free. Custom domain supported.

Cloudflare Tunnel: expose a local server to the internet with a real HTTPS URL. Also free.

For landing pages that don't need a CMS, this is everything you need.

---

Newsletter: Buttondown

Free up to 1,000 subscribers.

Clean interface. No bloat. Markdown-based writing. The free tier covers everything you need for the first year of audience building.

When you hit 1,000 subscribers and you're still not making money, the problem is the offer, not the platform.

---

Knowledge management: Obsidian

Free forever for personal use. All files stored locally.

I use it as the central vault for all content, research, product ideas, and project notes. Everything connects. Nothing is trapped in a SaaS database I don't control.

---

Automation: Telegram bot (self-hosted)

My bot handles idea capture, content reminders, and cross-machine task delegation.

Runs on Railway's free tier. Python. Open source.

Replaces $30-50/month in automation SaaS tools.

---

The one tool I do pay for: Claude Code. $20/month.

This is the only line item. It builds everything else.

Total monthly cost: $20.
Products available: 9.
Revenue ceiling: none.

---

Full breakdown of the self-hosted store architecture, including deployment steps and the complete cost breakdown:

https://behikeai.gumroad.com/l/self-hosted-store

---

## THREAD 4: I Analyzed 100 Roblox Games. Here's What Separates the Ones That Make Money.
**Account:** @kalaniandrez
**Hook:** "100 Roblox games. The pattern that separates $0/month from $500+/month."

---

100 Roblox games. The pattern that separates $0/month from $500+/month.

---

Most Roblox games make nothing. A small percentage make real money.

The difference is not graphics quality, map size, or game concept.

It is three specific mechanics.

---

The 3 mechanics every profitable game has:

1. Daily login reward. Players who have a reason to return every day generate compounding retention. Even a small reward creates a habit loop.

2. Visible progress bar or level counter. Players need to see how far they've come. Progress you can't see feels like nothing.

3. Checkpoints before hard sections. Losing 20 minutes of progress on a death is the fastest way to lose a player permanently.

These are not optional polish. They are the foundation of retention.

---

The 2 mistakes that kill retention immediately:

1. Full progress loss on death. One death that sends you back to the start will lose 60-70% of first-time players. Checkpoint on every major section, not just at the end.

2. No reward for coming back. If the game is identical on day 7 as it was on day 1, there is no reason to return. Daily rewards or rotating challenges fix this.

---

The monetization structure that converts:

Developer Products for consumables (coins, lives, boosts). These repeat. Players buy them more than once.

Game Passes for permanent perks. Sell once per player. Higher price point. Better for features that alter gameplay, not just cosmetics.

The mistake most games make: only using Game Passes. Players buy once and have no reason to spend again.

---

The one game type with the lowest competition and the highest conversion rate:

Simulator games with clear upgrade loops.

Why: The game loop (collect, upgrade, repeat) creates natural spending moments. The progression is visible. Players know exactly what they're working toward.

Obby (obstacle course) games have high traffic but almost no monetization. Simulator games have lower traffic but convert at 3-5x the rate.

---

Full guide on building profitable Roblox games, including the complete monetization framework and 6 game concepts with low competition:

https://behikeai.gumroad.com/l/roblox-builders-guide

---

## THREAD 5: How I Make Decisions When I Have 12 Projects Running at Once
**Account:** @kalaniandrez
**Hook:** "12 active projects. One decision rule that keeps everything on track."

---

12 active projects. One decision rule that keeps everything on track.

---

Most productivity advice assumes you have one thing to work on.

That's not how it works when you're building a business while in school, with multiple income streams at different stages.

The goal isn't to do less. The goal is to have a rule that tells you what to do today.

---

The rule: one primary output per day. Everything else is secondary.

A primary output is something that, when done, either moves money or moves a critical project forward by a measurable step.

Not tasks. Not research. Output. Something that exists after you're done that didn't exist before.

---

How to pick the primary output each morning:

Revenue proximity. How many steps is this action away from a sale.

Posting a product to Gumroad: 1 step.
Writing the product content: 2 steps.
Researching what product to build: 3 steps.

The lower the number, the higher the priority.

When in doubt, choose the action closest to revenue.

---

The Monday morning review. Three questions:

1. What shipped last week. Shipped means done and visible. Not "mostly done." Not "almost ready." Live.

2. What stalled and why. Stalled usually means the task was too large, the next step was unclear, or the project lost urgency.

3. What gets cut. One project gets removed from the active list every Monday if it has not moved in two weeks. No guilt. Just removal.

---

Why cutting is a skill:

Every active project takes a slice of your attention even when you're not working on it.

Twelve projects with 8% attention each is worse than 4 projects with 25% attention each.

The projects you refuse to cut are the ones killing the projects that could actually ship.

---

The Behike Method v2 is a full framework for this. Decision rules, project prioritization, the shipping mindset, and how to stop optimizing loops before they start.

Written for builders who have too many ideas and need a system, not more inspiration.

https://behikeai.gumroad.com/l/behike-method-v2

---

## POSTING SCHEDULE

| Thread | Account | Day | Notes |
|--------|---------|-----|-------|
| Thread 2 (7 Python Tools) | @behikeai | Week 1, Day 1 | High shareability. Pin candidate. |
| Thread 5 (12 Projects Rule) | @kalaniandrez | Week 1, Day 3 | Relatable. Warm audience entry point. |
| Thread 3 ($0 Tech Stack) | @kalaniandrez | Week 1, Day 5 | Practical value. Links to product. |
| Thread 1 (eBay Math) | @kalaniandrez | Week 2, Day 2 | Specific numbers. High trust builder. |
| Thread 4 (Roblox Analysis) | @kalaniandrez | Week 2, Day 4 | Niche pull. Roblox audience is large. |

---

## NOTES ON FORMAT

Each thread is posted as a reply chain. Hook tweet goes up first, standalone.

Every internal tweet works as a solo post if someone quote-tweets it. Write each one that way.

Threads 1 and 4 contain specific numbers. Numbers perform. Keep them exact.

Thread 2 is the most shareable for @behikeai. Pin it after posting.

Thread 5 is the highest-traffic entry point for new followers. It is universal enough to attract people who don't know the Behike brand yet.

Every CTA links to a specific product. No thread ends without a Gumroad link.

Cross-post each thread to Instagram as a carousel within 24 hours of posting on X.

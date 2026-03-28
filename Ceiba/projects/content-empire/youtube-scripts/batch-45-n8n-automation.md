---
title: YouTube Scripts Batch 45 -- n8n and Automation
topic: n8n automation for solopreneurs
created: 2026-03-22
scripts: 5
approx_runtime: 8-12 min each
brand: Behike
language: en
---

# Batch 45 -- n8n Automation for Solopreneurs

---

## Script 1: n8n vs Zapier: An Honest Comparison After 6 Months of Using Both

**Hook (0:00-0:30):**
I've run both Zapier and n8n side by side for six months. I've built workflows in both, hit the limits of both, and paid for one of them. In this video I'm going to give you an honest comparison, not a sponsored one, based on actual use cases from running a one-person business.

**Intro (0:30-1:30):**
I'm Kalani. I build automation workflows for my own business and for clients. I use n8n as my primary automation tool now, but I didn't start there. I started with Zapier like most people do, hit the pricing wall, and made the switch.

This comparison is going to cover four things: cost, flexibility, ease of use, and what each tool is actually best for. If you're trying to decide which one to use, this should give you a clear answer.

**Section 1 -- Cost: The Real Numbers (1:30-3:30):**
Zapier pricing is task-based. You pay per task, where one task equals one action in a workflow.

The free plan gives you 100 tasks per month. That sounds like a lot until you realize a single workflow with three steps running hourly will hit that limit in a few days.

The Starter plan is $19.99 per month for 750 tasks. The Professional plan is $49 per month for 2,000 tasks. If you're running any meaningful volume of automations, you're looking at $50 to $100 per month minimum.

n8n is different. The cloud hosted version starts at around $20 per month with 5,000 execution credits. But here's the thing: you can also self-host n8n for free. Run it on your own computer or on a $5 per month VPS and you pay only for the server, not the software.

I run n8n on a small server. My cost is roughly $5 to $7 per month, all in. I run dozens of workflows with no task limits.

If you're a solopreneur watching costs closely, this difference is not trivial.

**Section 2 -- Flexibility: What Each Tool Can Actually Do (3:30-6:00):**
Zapier is built for simplicity. You connect App A to App B with a trigger and an action. The interface is clean and it works well for linear, two-step automations.

Where Zapier struggles: conditional logic, loops, complex data transformations, and anything that requires code. You can add filters and formatters but there's a ceiling.

n8n is built for complexity. It has full support for conditional branches, loops, sub-workflows, JavaScript execution, and connections to almost anything with an API. The node library is large and it's open source, meaning people build custom integrations constantly.

The trade-off is that n8n's power comes with a learning curve. Setting up a complex workflow in n8n requires more thinking about the data structure. You can't just click through options like in Zapier.

For simple automations: Zapier is faster to build.
For complex automations: n8n is the only real choice.

**Section 3 -- Ease of Use: The Honest Assessment (6:00-8:00):**
Zapier is significantly easier for non-technical users. The interface walks you through each step. The error messages are readable. If you've never built an automation before, Zapier is the faster path to your first working workflow.

n8n requires some comfort with technical concepts. You need to understand how data flows between nodes, how to reference fields from previous steps, and occasionally how to write a small piece of JavaScript for data transformations.

I'm a computer engineering student, so n8n clicked for me relatively quickly. If you're not comfortable with any technical concepts, Zapier is the safer starting point.

That said, n8n has improved its interface significantly. The newer versions are much more approachable than they were two years ago.

**Section 4 -- My Recommendation (8:00-9:30):**
Use Zapier if:
- You need automations running fast with minimal setup
- You don't want to manage any infrastructure
- Your workflows are simple: trigger, one or two actions, done
- You're willing to pay $20 to $50 per month for convenience

Use n8n if:
- You want complex automation logic: conditions, loops, multiple branches
- You want to keep your costs low long-term
- You're comfortable with or interested in learning some technical concepts
- You want full control over your data and don't want it processed through third-party servers

I use n8n for everything now. The setup investment was worth it.

**CTA (9:30-10:00):**
If you want to see the specific n8n workflows I run for my business, I've got a dedicated video on that which I'll link below. If you're just getting started with automation, subscribe. Next week I'm covering how to build your first n8n workflow in 20 minutes.

**Approx runtime:** 9-10 min

---

## Script 2: 5 n8n Workflows That Save Me 10 Hours Per Week

**Hook (0:00-0:30):**
I run 5 n8n workflows that together save me roughly 10 hours per week. Not vaguely. Specifically: I timed the manual versions of each process, built the automation, and measured the difference. In this video I'm going to show you exactly what those 5 workflows are and how they work.

**Intro (0:30-1:30):**
I'm Kalani. I build automation systems for solopreneurs and use n8n as the backbone of my own operation. I started automating because I have limited time: I'm a student with a business to build and ADHD that makes repetitive tasks particularly expensive in terms of cognitive load.

These 5 workflows are the ones that had the most impact. Some of them are simple. One of them took me two days to build. I'll tell you which is which.

**Section 1 -- Workflow 1: Content Idea Capture and Classification (1:30-3:30):**
Time saved: approximately 2 hours per week.

The problem: I was capturing ideas in 5 different places. Voice notes on my phone, messages to myself on Telegram, a Notion page, a Notes app, and occasionally just a screenshot. None of them talked to each other.

The workflow: My Telegram bot receives a message (text or voice). If it's voice, it routes through OpenAI Whisper for transcription. The text then goes through Claude with a classification prompt that assigns a category (business, creative, technical, personal) and a priority level. The classified idea gets saved to a structured database with the original text, the category, and a timestamp.

Result: Every idea I capture ends up in one place, pre-classified, ready to be pulled into my weekly planning session.

Build difficulty: Medium. The voice transcription step adds complexity but it's worth it.

**Section 2 -- Workflow 2: eBay Product Research Alerts (3:30-5:30):**
Time saved: approximately 3 hours per week.

The problem: I was manually checking eBay and Google Trends every morning to look for products that were trending or showing increased search volume. This took 45 minutes to an hour daily.

The workflow: A scheduled trigger runs every morning at 7am. It pulls trending search data from a Google Trends endpoint, cross-references it against a list of categories I'm interested in, then queries the eBay API for active listings in matching categories. It filters for items with high sell-through rates and low competition, and sends me a summary message on Telegram with the top 5 opportunities for the day.

Result: I get a curated list every morning without opening a single browser tab manually.

Build difficulty: Hard. This one took two days. The Google Trends integration is not officially supported and requires some workarounds.

**Section 3 -- Workflow 3: Content Publishing Pipeline (5:30-7:00):**
Time saved: approximately 2 hours per week.

The problem: I was manually copying content from my drafts file, resizing images in Canva, and scheduling posts in Buffer one at a time. Tedious and easy to forget.

The workflow: I write content in a structured format in a Google Doc. When I mark a row in a connected Google Sheet as "ready to schedule," n8n picks it up, formats the content for each platform (Instagram needs different formatting than Twitter), pulls the associated image from a folder, and schedules it in Buffer via the API.

Result: Content goes from written to scheduled across three platforms without me touching anything after the Google Sheet update.

Build difficulty: Medium. The formatting logic per platform adds some complexity.

**Section 4 -- Workflows 4 and 5 (7:00-9:00):**
Workflow 4: Email list management.

When someone joins my email list, n8n triggers a welcome sequence in ConvertKit, tags them based on which lead magnet they downloaded, and sends me a notification so I know who's joining. Saves about 1.5 hours per week in manual tagging and follow-up.

Workflow 5: Weekly review digest.

Every Sunday morning at 8am, n8n pulls my stats from the week: Instagram follower count and reach, Gumroad sales, email list growth, and any pending tasks from my project database. It compiles them into a single Telegram message so my weekly review starts with all the numbers already in front of me.

Saves about 1.5 hours per week in manual data collection.

**CTA (9:00-9:30):**
All 5 of these workflows are buildable by someone with moderate technical comfort and a free n8n instance. I'll be publishing detailed build tutorials for the two most complex ones over the next few weeks. Subscribe so you don't miss those.

**Approx runtime:** 9-10 min

---

## Script 3: How to Build Your First n8n Automation in 20 Minutes

**Hook (0:00-0:30):**
By the end of this video you will have a working n8n automation. Not just an understanding of how n8n works, an actual workflow that does something useful. Twenty minutes, done.

**Intro (0:30-1:30):**
I'm Kalani. I'm going to walk you through building a simple but genuinely useful workflow: one that sends you a Telegram message when a new product gets added to a specific eBay category.

This is a good first workflow because it touches the three core concepts you need to understand to build anything in n8n: triggers, API calls, and message sending. Once you have those three, you can build almost anything.

Prerequisites: you need n8n installed (I'll link to the official setup guide below), a Telegram account, and a Telegram bot token. Getting the bot token takes about 3 minutes via BotFather. The n8n setup on a free cloud trial or local machine takes about 10 minutes.

**Section 1 -- Understanding the n8n Interface (1:30-3:00):**
When you open n8n, you see a blank canvas. Every workflow lives on this canvas.

Workflows are made of nodes. Each node does one thing: receives data, transforms data, or sends data somewhere.

Nodes are connected with arrows that show the direction data flows. Data moves from left to right. The first node is always a trigger.

Three types of nodes you'll use constantly:
- Trigger nodes: start the workflow. Can be scheduled, webhook-based, or manual.
- Action nodes: do something with data. Make an API call, send a message, write to a database.
- Logic nodes: control flow. If/else conditions, loops, error handling.

That's the whole model. Everything else is specifics.

**Section 2 -- Setting Up the Trigger (3:00-5:30):**
For this workflow, we're using a Schedule Trigger. We want this to run once a day.

Click the plus button on the canvas. Search for "Schedule Trigger." Add it.

Configure it: interval set to 1 day, time set to 8am. This means the workflow runs every morning at 8am.

Click "Save" at the top right. The trigger is done.

Now connect the trigger to the next node. Click the arrow coming out of the trigger and drag it to the blank canvas to add the next step.

**Section 3 -- The eBay API Call (5:30-9:00):**
We're going to call the eBay Browse API to get recent listings in a category.

Add an HTTP Request node after the trigger.

URL: https://api.ebay.com/buy/browse/v1/item_summary/search

Method: GET

Parameters: we'll add a q parameter for the search keyword and a limit parameter set to 5.

Authentication: eBay requires an OAuth token. In n8n, add a Header Auth credential with the name "Authorization" and your eBay app token as the value. I'll link to the eBay developer docs for how to get this token in the description.

Now run this node manually by clicking "Execute Node" to verify you get results back. You should see a JSON response with item data.

If you get an error, the most common issues are an expired token or an incorrect header format. The Authorization header should start with "Bearer" followed by your token.

Once you see item data in the output, the API call is working.

**Section 4 -- Sending the Telegram Message (9:00-12:00):**
Add a Telegram node after the HTTP Request.

In the Telegram node, add your bot credentials: the bot token you got from BotFather.

Operation: Send Message.

Chat ID: your personal Telegram chat ID. You can get this by sending a message to your bot and calling the getUpdates endpoint, or by using the IDBot on Telegram.

Message: here's where we use n8n's expression syntax to pull data from the previous step. Write: "New eBay listings:" followed by expressions that pull the item title and price from each result.

n8n uses double curly braces for expressions. The data from the previous node is accessible as $json. So item title would be something like $json["itemSummaries"][0]["title"].

Test the full workflow by clicking "Execute Workflow." If everything is configured correctly, you'll get a Telegram message within a few seconds.

Save the workflow and activate it using the toggle at the top. It will now run automatically every day at 8am.

**CTA (12:00-12:30):**
That's your first n8n automation. From here, the path forward is adding complexity gradually: filters to only alert on items below a certain price, multiple searches in different categories, saving results to a spreadsheet.

Subscribe and I'll cover those extensions in future videos.

**Approx runtime:** 12 min

---

## Script 4: Automating My Content Pipeline with n8n: The Full Setup

**Hook (0:00-0:30):**
Every week I publish content across Instagram, Twitter, and YouTube. I do not manually schedule all of it. I built a content pipeline in n8n that takes a structured document as input and handles everything from formatting to scheduling across platforms. In this video I'll show you the full architecture.

**Intro (0:30-1:30):**
I'm Kalani. I'm a one-person business running a content operation while also being a full-time university student. I had to automate my content pipeline or I couldn't have maintained any publishing consistency.

This video is not a beginner tutorial. If you haven't used n8n before, watch my "First Automation in 20 Minutes" video first. This one assumes you're comfortable with the basics and want to see a more complex real-world system.

**Section 1 -- The Pipeline Architecture (1:30-4:00):**
The pipeline has three stages: input, processing, and distribution.

Input: I write content in a Google Sheet. Each row is one piece of content with columns for platform, copy text, hook, image filename, publish date, and status. When I set status to "ready," it signals the pipeline to pick it up.

Processing: n8n polls the Google Sheet every hour. When it finds a row with status "ready," it reads the content, formats it for the target platform, pulls the corresponding image from a Google Drive folder, and prepares a complete publishing payload.

Distribution: the formatted content goes to Buffer via the Buffer API, which handles the actual scheduling and posting to each platform.

Three stages, each handled by a separate sub-workflow. Sub-workflows are n8n workflows that you call from another workflow, like functions in programming.

**Section 2 -- The Input Stage: The Google Sheet Structure (4:00-6:00):**
The sheet structure is the most important design decision because it determines what the automation can and can't do.

My columns:
- ID: unique identifier for each piece of content
- Platform: instagram, twitter, or youtube (drives formatting logic)
- Hook: the first line. Used separately from the body for Instagram.
- Body: the main content text
- Hashtags: stored separately so I can toggle whether to include them
- Image: filename of the image in Google Drive
- Publish Date: the target publish time
- Status: draft, ready, scheduled, published

The separation of hook and body is important. Instagram captions need the hook to be the very first thing before any line break. By keeping it as a separate field, the formatting node can assemble them correctly without text manipulation.

**Section 3 -- The Processing Stage: Platform Formatting (6:00-8:30):**
Different platforms need different formatting. This is where most simple pipelines fail: they copy-paste the same text everywhere and it looks wrong on every platform.

For Instagram: combine hook plus two line breaks plus body plus two line breaks plus hashtags. Instagram collapses whitespace in a specific way, so you need to know the formatting rules.

For Twitter: if the body is under 280 characters, post as a single tweet. If it's longer, the node splits it into a thread with numbered tweets.

For YouTube descriptions: the format is hook first, then a blank line, then the body structured as a script outline with timestamps.

Each of these formats is handled by a Code node in n8n where I've written the logic in JavaScript. The code is short, usually under 20 lines, but it makes the output look intentional on each platform.

**Section 4 -- The Distribution Stage and Error Handling (8:30-10:30):**
After formatting, the content goes to Buffer.

Buffer has an API endpoint for creating scheduled posts. The n8n HTTP Request node calls that endpoint with the formatted text, the image URL, and the publish timestamp.

Buffer handles the actual posting. I chose Buffer over posting directly to each platform API because Buffer normalizes the differences between platforms and handles rate limiting and retries automatically.

Error handling: I have a set of error workflow nodes that catch failures and send me a Telegram notification with the error details. If a post fails to schedule, I know within minutes and can fix it manually.

The status column in the Google Sheet updates automatically. When n8n successfully schedules a post in Buffer, it writes "scheduled" back to the row. When the post publishes, a webhook from Buffer updates it to "published." I can see the state of my entire content queue at a glance.

**CTA (10:30-11:00):**
This pipeline took me about a week to build and refine. It's saved me several hours every week since. If you want the n8n workflow JSON so you can import it as a starting point, it's in the description.

Subscribe for more of this. I document every system I build.

**Approx runtime:** 10-11 min

---

## Script 5: How I Use n8n to Research and List eBay Products Automatically

**Hook (0:00-0:30):**
Product research is the most time-consuming part of running an eBay dropshipping operation. I built an n8n workflow that does the research for me every morning and another workflow that prepopulates eBay listing drafts with the data it finds. In this video I'll show you both.

**Intro (0:30-1:30):**
I'm Kalani. I run an eBay reselling operation alongside my content business, and I'm a computer engineering student in Puerto Rico. Time is my scarcest resource. Automating product research was one of the highest-leverage things I've done for the eBay side of the business.

This video covers two workflows. The research workflow and the listing workflow. Both are built in n8n. I'll show you the architecture, the key nodes, and the specific APIs involved.

**Section 1 -- The Research Workflow: Finding Products (1:30-4:30):**
The research workflow runs every morning at 7am.

It pulls from three sources simultaneously using n8n's parallel branch feature:

Source 1: eBay Trending API. This returns items that are currently getting high search and view volume on eBay. I filter for categories I work with: electronics accessories, home goods, and fitness equipment.

Source 2: Google Trends via the unofficial Trends API. I query trends for broad category terms and look for things with a slope up over the past 7 days. Items with rising trend lines are better bets than items that peaked already.

Source 3: My own sales history from eBay's Seller Hub API. I look at items I've sold in the last 60 days with high sell-through rates and check if there's room to list more inventory.

After pulling from all three sources, a merge node combines the results and a deduplication step removes any items that appear in multiple sources. I then score each item using a simple formula: sell-through rate weight 40%, trend slope weight 30%, competition level (number of active listings) weight 30%.

The top 10 items by score get written to a Google Sheet and I get a Telegram summary.

**Section 2 -- The Listing Workflow: Going from Research to Draft (4:30-7:30):**
When I look at the research sheet in the morning and decide I want to list something, I change its status to "list this" in the sheet. That change triggers the listing workflow.

The listing workflow pulls the item data from the sheet and does four things automatically:

First, it searches eBay for comparable sold listings and pulls the average price for sold items in the last 30 days. This gives me a data-driven price to start with rather than guessing.

Second, it queries a product database (I use the eBay Catalog API) to pull the official product title, description, and specifications. This saves me from writing descriptions from scratch.

Third, it runs the title and description through Claude with a prompt that rewrites them in my listing style: specific, keyword-rich, without any claims I can't verify.

Fourth, it creates a draft listing on eBay via the Inventory API with the title, description, and suggested price pre-filled.

I still review and approve every listing before it goes live. The automation handles research and prep, not publishing.

**Section 3 -- The APIs and Authentication (7:30-9:30):**
The hardest part of building this workflow was authentication. Most of these APIs require OAuth 2.0, which is more complex than a simple API key.

eBay specifically uses OAuth with refresh tokens. When the token expires, n8n needs to automatically refresh it. I handle this with a separate credential refresh sub-workflow that runs every 12 hours and updates the stored credentials.

Google Trends does not have an official API. I use a library called pytrends that I run on a small Flask server on my local machine. n8n calls that local server via HTTP request. It's a workaround, but it's been stable.

For anyone who wants to replicate this without building the Google Trends wrapper, you can substitute it with a manual check or with a paid trends data service that has a proper API.

The Claude API integration is the simplest part: standard HTTP request with an API key, JSON body with the prompt and item data.

**Section 4 -- Results and Limitations (9:30-11:00):**
This system has meaningfully reduced the time I spend on product research. I used to spend 45 minutes to an hour every morning manually checking trends and comparable prices. Now I spend about 10 minutes reviewing the automated report.

The listing prep workflow saves another 20 to 30 minutes per listing. Writing a good eBay title and description from scratch takes time. Getting a 90% draft automatically means I'm editing instead of writing.

Limitations: the Google Trends integration is fragile. If the pytrends library breaks or the endpoint changes, that part of the workflow stops working and I have to debug it. I've had this happen twice in six months.

The Claude-written descriptions still need review. The model occasionally adds details that aren't verifiable from the product data I give it. I always fact-check before publishing.

And the system doesn't replace judgment. The algorithm scores items, but I still decide what to list. There have been items that scored high but that I knew from experience wouldn't sell well in my specific store.

**CTA (11:00-11:30):**
If you're running an eBay or Shopify operation and spending significant time on product research every day, n8n is worth learning. The upfront investment pays back quickly.

I'll link the workflow JSON exports in the description. Subscribe if you want to see more about the product research pipeline, I have a dedicated video planned that goes deeper into the scoring formula.

**Approx runtime:** 11 min

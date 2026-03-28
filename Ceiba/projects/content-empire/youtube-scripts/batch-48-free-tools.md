---
title: YouTube Scripts Batch 48 — Free Tools and Open Source
created: 2026-03-22
batch: 48
theme: Free Tools and Open Source
scripts: 5
target_length: 8-12 min
brand: Behike
---

# Batch 48 — Free Tools and Open Source

---

## Script 1: "The Free AI Stack That Replaced $200/Month in Subscriptions"

**Target length:** 9-11 min
**Hook type:** Cost-savings reveal
**CTA:** Free AI stack guide on Gumroad

---

### HOOK (0:00-0:45)

At one point I was paying $200 per month across AI subscriptions: ChatGPT Plus, Midjourney, a transcription service, a summarization tool, and two automation platforms.

I've cut that to about $20 per month. Not by downgrading what I can do — by replacing paid tools with free or open-source alternatives that do the same job or close to it.

Here's the current stack.

---

### SECTION 1 — What I Was Paying For (0:45-2:30)

Let me be specific about what the $200 covered and why I was paying for it.

ChatGPT Plus at $20/month: I needed GPT-4 access for complex writing and reasoning tasks.

Midjourney at $10-30/month depending on tier: image generation for product covers and content visuals.

A transcription service at $25/month: converting audio notes and voice memos to text.

A summarization tool at $15/month: summarizing long documents and research papers.

Zapier at $20-50/month: connecting tools and automating workflows.

A form and survey tool at $20/month: data collection for a product I was building.

Total: $110-160/month, plus occasional overages.

---

### SECTION 2 — The Replacements (2:30-6:00)

Here's what replaced each one.

**ChatGPT Plus replaced by:** Claude free tier for most tasks, combined with Ollama running local models on my machine. For tasks that need API-level access, I pay per token rather than a flat subscription. For most of my use cases, the monthly cost is under $5.

**Midjourney replaced by:** Stable Diffusion running locally via ComfyUI. Setup takes a few hours. After that it's free, runs offline, and I have full control over the output. For quick social graphics, Canva's free tier handles 90% of what I need.

**Transcription service replaced by:** OpenAI's Whisper, open-source and free, running locally. I call it from a Python script that watches a folder. Voice memo drops in, transcript comes out. Zero per-month cost.

**Summarization tool replaced by:** The same local models through Ollama, or the free tier of Claude for longer documents. The paid tool I had was a thin wrapper around an API I can call directly.

**Zapier replaced by:** n8n self-hosted on a $5/month VPS. Full workflow automation, no per-task fees, unlimited runs. More on this in a dedicated video.

**Form tool replaced by:** Tally.so free tier, which covers everything I need for standard data collection. For more complex needs, a simple HTML form that posts to a Google Sheet via Apps Script — free and permanent.

---

### SECTION 3 — The Actual Monthly Cost Now (6:00-7:30)

What I'm actually paying today:

- Anthropic API: variable, typically $3-8/month based on usage
- VPS for n8n self-hosted: $5/month
- Domain: ~$12/year, negligible monthly
- Gumroad: free tier (they take a cut per transaction, no subscription)
- GitHub: free for public repos, free for private repos under the limits I use

Total: roughly $10-15/month, occasionally hitting $20 if I have a heavy API month.

The savings paid for my Gumroad store setup, my domain, and a chunk of my early product research costs.

---

### SECTION 4 — The Trade-offs You Should Know About (7:30-9:30)

This isn't a free lunch. Here's what you're trading.

Setup time. Installing Ollama, setting up ComfyUI, configuring a self-hosted n8n instance — these take time the first time. A paid SaaS tool is faster to start using.

Hardware requirements. Running local AI models at any reasonable speed requires decent hardware. I have a machine with enough VRAM to run 7B-13B models. On weaker hardware, local models are slow.

Maintenance. A self-hosted tool is yours to maintain. When n8n releases an update, I handle the update. When a dependency breaks, I fix it. That's work that a paid SaaS handles invisibly.

No support. If something breaks in your local Whisper setup, there's no customer service to call.

My take: if you're a builder who's comfortable in a terminal and has decent hardware, these trade-offs are worth it. If you're not technical and your time is expensive, the paid tools may still be the right call.

---

### OUTRO (9:30-11:00)

The free AI stack guide with setup instructions for each tool is in the description. It includes the exact scripts I use for local Whisper, the n8n self-host setup process, and the Ollama model recommendations for different hardware profiles.

---

**CTA:** Free AI stack guide on Gumroad (free product)

---

---

## Script 2: "n8n Self-Hosted: Why I Stopped Using Zapier"

**Target length:** 10-12 min
**Hook type:** Direct comparison
**CTA:** n8n workflow bundle

---

### HOOK (0:00-0:45)

I used Zapier for about two years. It was fine. It got the job done for simple stuff.

Then I ran into pricing limits, got hit with an unexpected charge for going over task limits, and spent 30 minutes trying to figure out why a three-step Zap had stopped working.

I set up n8n self-hosted that weekend. I haven't gone back.

Here's the actual comparison.

---

### SECTION 1 — What Zapier Does Well (0:45-2:30)

I want to give Zapier a fair assessment because it genuinely does some things well.

Setup speed. Creating a simple two-step automation in Zapier takes about five minutes. The UI is clean, the trigger/action model is intuitive, and they have native integrations for almost every SaaS tool you're likely to use.

Reliability. Zapier has good uptime and handles retries automatically. For critical automations where you can't afford to babysit a self-hosted instance, that reliability has real value.

Non-technical access. If you're not a developer and you just need Gmail to talk to Notion without writing any code, Zapier is the right tool. It was designed for that use case.

---

### SECTION 2 — Where Zapier Fails at Scale (2:30-5:00)

The pricing model is the biggest problem.

Zapier charges per task. A "task" is defined as each action step that runs. A five-step Zap that runs 1,000 times per month is 4,000 tasks (the trigger doesn't count). On the free plan, you get 100 tasks/month. On the cheapest paid plan, 750 tasks at $20/month.

For any serious automation workload — especially if you're running product research pipelines, content workflows, or multi-step data processing — you will exceed these limits and the cost will scale with your usage.

The other limitation: Zapier doesn't allow arbitrary code execution in the flow without a specific plan tier. For anything beyond simple trigger-action, you're limited by what their native nodes support.

---

### SECTION 3 — How n8n Self-Hosted Works (5:00-7:30)

n8n is open source automation software. You can run it on your own server.

The basic setup: a cheap VPS (I use a $5/month instance from Hetzner), Docker to run the n8n container, and a reverse proxy to handle HTTPS. Total setup time, including DNS configuration: about two hours the first time, less if you've done it before.

What you get: unlimited workflows, unlimited task executions, no per-task fees, full access to all node types including code execution, and the ability to build custom nodes.

The n8n workflow model is the same as Zapier: triggers and actions connected in a visual graph. If you've used Zapier, n8n's interface is familiar within an hour.

The key difference: you can run arbitrary JavaScript or Python in a Code node. This means if a native integration doesn't do exactly what you need, you write the logic yourself. I've built integrations with tools that have no n8n native node by writing a few lines of code in a Code node.

---

### SECTION 4 — Specific Automations I Run on n8n (7:30-9:30)

Here's what's currently running on my n8n instance.

Product research pipeline: scrapes eBay sold listings for target categories, runs the data through a scoring function, and outputs a formatted report to a Notion database every morning.

Content calendar automation: checks my Obsidian vault for posts tagged "ready," formats them for the appropriate platform, and logs them to a scheduling queue.

BehiqueBot pipeline connection: when Telegram messages come in via BehiqueBot, an n8n workflow classifies and routes them to the appropriate storage location.

Gumroad sale notifications: when a Gumroad product sells, n8n catches the webhook and logs the sale with metadata to a tracking sheet.

None of these would be economically viable on Zapier's task pricing model at the volume I run them.

---

### SECTION 5 — When to Still Use Zapier (9:30-10:30)

If you're non-technical and you need one or two simple automations that don't exceed the free tier, Zapier is the right tool. Don't self-host something just to say you did.

If you need enterprise-grade SLA guarantees and you can't afford any downtime, the cost difference may be worth it for Zapier's managed reliability.

If you're building something for a client who needs to manage it themselves, Zapier's UI is more accessible to non-developers than n8n's.

---

### OUTRO (10:30-12:00)

My n8n workflow bundle includes the five workflows I use most, pre-configured and documented. Link in the description.

---

**CTA:** n8n workflow bundle

---

---

## Script 3: "Whisper AI for Free Transcription: Setup and Real World Use"

**Target length:** 8-10 min
**Hook type:** Tool tutorial
**CTA:** Free AI stack guide

---

### HOOK (0:00-0:45)

I record voice memos constantly. Ideas in the shower, notes while walking, full ramble sessions where I'm thinking out loud about a product or a problem.

For years, turning those recordings into text required either paying for a transcription service or typing them myself.

Whisper is free, runs offline, and produces transcripts that are good enough that I barely edit them. Here's how I have it set up.

---

### SECTION 1 — What Whisper Is (0:45-2:00)

Whisper is an automatic speech recognition model released by OpenAI as open-source software. You can run it on your own machine, for free, without sending audio to any server.

It supports dozens of languages including Spanish and English, handles accented speech well, and produces transcripts with timestamps.

There are different model sizes: tiny, base, small, medium, large. Larger models are more accurate but slower and require more memory. I use the medium model on my machine and get about real-time processing speed — a 5-minute audio file transcribes in about 5 minutes.

---

### SECTION 2 — Installation (2:00-4:00)

Whisper runs on Python. You need Python 3.9 or higher and pip.

Install command:
```
pip install openai-whisper
```

For GPU acceleration on Mac (Apple Silicon), the version optimized for Metal is called mlx-whisper. It runs significantly faster on M-series chips:
```
pip install mlx-whisper
```

On Windows or Linux with an Nvidia GPU, the standard whisper package will use CUDA automatically if it's available.

Verify the install worked:
```
whisper --version
```

---

### SECTION 3 — Basic Usage (4:00-5:30)

Simplest possible use: transcribe a single file.

```
whisper recording.m4a --model medium
```

This produces a text file, a JSON file with timestamps, and an SRT subtitle file, all in the same directory as the input.

For Spanish audio:
```
whisper recording.m4a --model medium --language Spanish
```

For translated output (Spanish audio to English text):
```
whisper recording.m4a --model medium --task translate
```

---

### SECTION 4 — The Automation I Use (5:30-7:30)

I have a Python script that watches a folder on my desktop. When I drop an audio file into that folder, it automatically transcribes it and saves the output to my Obsidian vault in a daily notes folder.

The core logic is a file watcher using the watchdog library, combined with a subprocess call to whisper. The output gets formatted with a timestamp and the source filename and written as a markdown file.

This cost me about an hour to set up. Since then, every voice memo I record is automatically in my vault within a few minutes of me syncing it from my phone.

The script is available in the free AI stack guide linked in the description.

---

### SECTION 5 — Real World Accuracy (7:30-8:30)

My honest assessment of accuracy on the medium model.

English speech from a quiet environment: excellent. I rarely edit more than a few words per page.

Spanish speech: very good. Better than most paid services I've used for Spanish, which often struggle with Puerto Rican Spanish specifically.

Noisy environments: noticeably worse. Street noise, wind, or background music degrades accuracy significantly. The large-v2 model handles noise better than medium.

Heavily accented or specialized vocabulary: some errors, but usually context makes them clear. Technical terms and proper nouns are the most common errors.

---

### OUTRO (8:30-9:30)

For anyone who thinks in audio and needs text output, this setup is worth the one-time installation cost. The free AI stack guide has the full script and setup instructions.

---

**CTA:** Free AI stack guide

---

---

## Script 4: "GitHub Pages as a Free Product Store: Complete Setup"

**Target length:** 9-11 min
**Hook type:** Tutorial with real example
**CTA:** Landing page template

---

### HOOK (0:00-0:45)

Every digital product I sell has a landing page. Most of those landing pages live on GitHub Pages. Total hosting cost: zero dollars per month, forever.

I'll show you exactly how to set this up from scratch, including custom domain configuration and what the actual HTML structure looks like.

---

### SECTION 1 — What GitHub Pages Is (0:45-2:00)

GitHub Pages is a static site hosting service built into GitHub. You push HTML, CSS, and JavaScript files to a repository, enable Pages in the settings, and GitHub serves those files as a public website.

There are no server costs, no database, no deployment pipeline to configure. The site is just files. GitHub serves them.

Limits: free tier supports one user site (username.github.io) and unlimited project sites (username.github.io/project-name). Storage limit is 1GB per site. Bandwidth limit is 100GB per month, which is more than enough for landing pages.

No dynamic functionality — no server-side code. But for a product landing page, you don't need server-side code.

---

### SECTION 2 — Setting Up Your First Page (2:00-4:30)

Create a new public repository on GitHub. The name can be anything.

In the repository settings, find the Pages section. Set the source to "Deploy from a branch" and select the main branch, root folder.

Create an index.html file in the root of the repository. Push it.

Within a few minutes, your site is live at username.github.io/repository-name.

That's the complete setup for the basic case.

---

### SECTION 3 — Custom Domain (4:30-6:30)

Connecting a custom domain is four steps.

One: buy the domain from any registrar (Namecheap, Porkbun, Google Domains).

Two: in the repository Pages settings, enter your custom domain.

Three: at your domain registrar, create a CNAME record pointing your domain to username.github.io.

Four: GitHub will automatically provision an HTTPS certificate via Let's Encrypt. This takes up to 24 hours but usually happens within an hour.

After this, your custom domain serves the same files from GitHub. The GitHub.io URL still works, but your custom domain is now the primary address.

---

### SECTION 4 — The Landing Page Structure I Use (6:30-9:00)

My product landing pages follow a consistent structure. Here's what's in each one.

Header: product name, one-line description, and the buy button. The buy button points to the Gumroad product URL. Above the fold, everything you need to make the decision is visible.

Social proof: one or two sentences from buyers or a concrete result. If I don't have reviews yet, I use a "here's what you'll be able to do after this" statement.

Product breakdown: a short list of what's in the product. Not a feature dump. Three to five specific things.

Who it's for: one paragraph describing the reader this is written for. This does two things — it qualifies buyers and it makes the right buyer feel seen.

Buy block: the Gumroad button again, with the price. No friction. One click to purchase.

The whole thing is one HTML file. No JavaScript required for the basic version. I add a simple scroll behavior and a mobile menu for longer pages, but the core is static HTML and CSS.

---

### OUTRO (9:00-10:30)

The landing page template I use — with Gumroad button integration already wired in — is linked in the description. It's one HTML file. Drop it into a GitHub repository and you have a live product page in twenty minutes.

---

**CTA:** Landing page template (paid or free)

---

---

## Script 5: "The $0 Tech Stack for a One-Person Digital Business"

**Target length:** 9-11 min
**Hook type:** Full system reveal
**CTA:** Solopreneur OS

---

### HOOK (0:00-0:45)

You don't need to spend money on software to start a digital business. You might spend money later, when the revenue justifies it. But at the start, every tool you need exists in a free or open-source version.

Here's the complete stack I'd use if I were starting today with zero budget.

---

### SECTION 1 — Products and Payments (0:45-2:30)

For selling digital products: Gumroad.

Gumroad's free tier takes a 10% cut of each sale but charges no monthly fee. For someone starting out, this is the right model. You pay nothing until you make money. The fee decreases as you make more.

What Gumroad handles for free: file hosting, payment processing, PDF delivery, license keys, discount codes, customer email list, and a basic analytics dashboard.

You don't need Shopify, WooCommerce, or Stripe until you're at a volume where Gumroad's cut exceeds the cost of those platforms plus the time to run them.

---

### SECTION 2 — Website and Landing Pages (2:30-4:30)

For a main website: GitHub Pages (covered in depth in the previous video).

For landing pages: same thing. One HTML file per product, each in its own GitHub repository or as subdirectories in one repository.

For a link-in-bio page: Carrd free tier. One page, clean design, links to your products and profiles. No coding required.

Total cost: $0. Custom domain is optional and costs $10-15/year if you want it.

---

### SECTION 3 — Email (4:30-6:00)

For email list: Beehiiv free tier. Up to 2,500 subscribers at no cost. Clean editor, good deliverability, basic analytics.

For transactional email (Gumroad sends purchase confirmations automatically, so you may not need this at first): Resend has a free tier that covers low-volume sends.

For email outreach and follow-up: Gmail or any free email provider. At the scale where this becomes a bottleneck, you'll have revenue to upgrade.

---

### SECTION 4 — Creation and Productivity (6:00-8:00)

For writing and notes: Obsidian. Free for personal use. Local markdown files. No subscription, no cloud dependency unless you want it.

For document creation and PDF export: LibreOffice is free and open source. Alternatively, the free tiers of Notion or Google Docs handle most document types.

For image creation: Canva free tier for social graphics, product covers, and simple designs. For AI image generation: Stable Diffusion via ComfyUI locally, or the free tiers of several web-based generators.

For video editing: CapCut desktop app, free tier. Handles Reels-length content well.

---

### SECTION 5 — Automation and AI (8:00-9:30)

For automation: n8n self-hosted on a $5/month VPS. If even $5/month is too much to start, Make (formerly Integromat) has a free tier that covers simple automations.

For AI: Claude free tier and ChatGPT free tier cover most daily writing and thinking tasks. For local models: Ollama, free and runs on your machine.

For transcription: Whisper, open source, runs locally for free.

For code: VS Code with GitHub Copilot's free tier, or Cursor's free tier.

The total monthly cost for the full stack: $0 if you skip the VPS, $5/month if you add n8n self-hosted. The domain, if you buy one, adds $1.25/month annualized.

---

### OUTRO (9:30-11:00)

There's no barrier to starting. The friction is building the thing and distributing it, not paying for software.

The Solopreneur OS covers how to structure the business around these tools — the product system, the content calendar, the revenue tracking. It's not software. It's the operating logic. Link in the description.

---

**CTA:** Solopreneur OS on Gumroad

---

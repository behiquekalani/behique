---
title: YouTube Scripts Batch 46 — Building Tools
created: 2026-03-22
batch: 46
theme: Building Tools
scripts: 5
target_length: 8-12 min
brand: Behike
---

# Batch 46 — Building Tools

---

## Script 1: "I Built 34 Digital Products in 6 Weeks Using AI. Here's How."

**Target length:** 10-12 min
**Hook type:** Process reveal
**CTA:** Gumroad store

---

### HOOK (0:00-0:45)

Six weeks ago I had zero digital products. Today I have 34.

Not drafts. Not ideas in a doc. Thirty-four products listed, priced, with cover art, descriptions, and landing pages. Some are already selling.

I'm going to show you exactly how I did it — the actual process, the tools, the failures, and what the output looks like. This is not a motivation video. It's a build log.

---

### SECTION 1 — Why I Did This (1:00-2:30)

I wanted to test a hypothesis: can one person build a digital product catalog at the speed of a small team using AI?

I wasn't trying to build perfect products. I was trying to find out which categories get traction — ebooks, guides, templates, mini-courses, checklists — and which price points work for a brand that didn't exist six weeks ago.

The goal was a living catalog. Ship fast, see what moves, iterate on winners.

Here's what I didn't do: I didn't spend three weeks on one product. I didn't hire anyone. I didn't wait until I "felt ready."

---

### SECTION 2 — The Stack (2:30-4:30)

Everything ran on three tools.

**Claude Code.** This is where most of the work happened. I'd describe a product concept and ask for a full content outline. Then I'd refine it section by section. For technical products, I'd pair it with actual code I'd written and ask Claude to document the reasoning and structure it into a guide.

**Obsidian.** Every product lived as a markdown file. I kept a product index with status tags: draft, review, ready, listed. When I needed to see the full picture, I opened the vault.

**Gumroad.** Zero dev work required. Upload the file, set a price, paste a description, publish. That's it. No Shopify config, no payment integration, no email system to set up first.

The pipeline was simple: idea in Obsidian, write in Claude Code, export as PDF, upload to Gumroad.

---

### SECTION 3 — What 34 Products Actually Looks Like (4:30-7:00)

Here's the breakdown by type:

- 9 PDF guides (AI tools, ADHD systems, finance, security, reselling)
- 6 template packs (Notion, spreadsheets, prompt libraries)
- 5 checklists and quick-reference sheets
- 4 mini-courses (structured markdown with exercises)
- 4 landing page templates
- 3 automation workflow bundles (n8n JSON exports)
- 2 app prototypes (web-based tools)
- 1 community access product

Prices range from $7.99 to $49.99. The median is around $19.

Not all 34 are strong. About a third I'd call solid. Another third are good enough. The final third are thin — and I know it. But shipping thin beats not shipping at all when you're in discovery mode.

---

### SECTION 4 — The Actual Workflow for One Product (7:00-9:30)

Let me walk through how I built the AI Employee Guide as a specific example.

I started with a one-line concept: "a guide for someone who wants to replace 20 hours per week of repetitive work using AI agents, without writing code."

Then I opened Claude Code and asked for a full table of contents. I gave it context: the reader is a solo operator, non-technical, budget-conscious. Claude gave me 12 chapters. I cut it to 8 and told it which ones to prioritize.

Then I wrote each section by prompting Claude for a draft and editing it myself. Total editing ratio was roughly 40/60 — 40% AI output that I kept, 60% rewritten or added. The voice had to be mine.

Cover art: Canva, fifteen minutes. I have a template now so it takes five.

PDF export from the markdown file. Upload to Gumroad. Write the description directly in the Gumroad editor — I don't pre-write these, I write them live because it's faster.

Total time for that product: about four hours across two days.

---

### SECTION 5 — What I'd Do Differently (9:30-11:00)

A few things I learned the hard way.

First: write the sales description before the product, not after. It forces you to be clear on who it's for and what problem it solves. I did this backwards for the first ten products.

Second: voice consistency matters more than I expected. Products I wrote quickly without re-reading my earlier work sound different. Readers notice.

Third: PDF is not always the right format. Some of my template products would have been better as Notion pages with a buy link. I'm rebuilding two of them.

---

### OUTRO (11:00-12:00)

The catalog is live. I'm adding products based on what's getting traction and pulling back on what isn't.

If you want to see the actual products, the link is in the description. And if you want the behind-the-scenes breakdown of the content system I use to build and distribute this stuff, I have a full guide on that too.

More build logs coming. Subscribe if that's the kind of content you want.

---

**CTA:** Gumroad store link + subscribe

---

---

## Script 2: "How to Build a Web App Without a Backend (HTML+JS+Gumroad)"

**Target length:** 9-11 min
**Hook type:** Technical reveal
**CTA:** GitHub template or guide

---

### HOOK (0:00-0:45)

Most "build without code" tutorials still assume you need a server, a database, and a hosting account before you can ship anything.

You don't.

I've built functional apps — tools people actually use and pay for — using nothing but an HTML file, vanilla JavaScript, and Gumroad as the payment and access layer. No backend. No server. No monthly hosting bill.

I'll show you exactly how it works and where the limits are.

---

### SECTION 1 — The Mental Model (0:45-2:30)

Here's what most people get wrong: they think "web app" means you need backend infrastructure. That's only true for a specific class of problems — user accounts, persistent data, multi-user interactions.

For a huge category of tools — calculators, generators, converters, checkers, one-time processors — you don't need any of that. The browser is the runtime. The user's machine does the computation. You store state in localStorage or not at all.

The apps I build this way are what I call "closed-loop tools." Everything the app needs lives in the HTML file. Input goes in, output comes out, nothing gets saved to a server.

This is a real constraint. But it's also the reason you can ship in a day.

---

### SECTION 2 — The Technical Structure (2:30-5:00)

Here's the actual file structure for one of my tools. One HTML file. That's it.

Inside that file:

- HTML: the interface layout
- CSS: styles, either inline or in a style block
- JavaScript: all the logic

When I say "no backend," I mean no Node server, no API routes, no database queries. The JavaScript runs entirely in the browser.

For tools that need AI, I make direct API calls to OpenAI or Anthropic from the front end. Yes, this means the API key is in the code. For products where the user brings their own key, this is fine. For products where you're providing the key, you need a different approach — I'll cover that.

For tools that need to process files, I use the FileReader API. For tools that need to remember settings, I use localStorage. For tools that need to do math, dates, or text processing, JavaScript handles all of it natively.

---

### SECTION 3 — Gumroad as the Gate (5:00-7:00)

Here's where this gets interesting from a product standpoint.

Gumroad has a feature called license keys. When someone buys your product, they get a unique license key. Your HTML app can check that key against the Gumroad API before granting access.

So the flow is: user buys on Gumroad, gets a key via email, enters the key in your app, the app calls the Gumroad license verification endpoint, and if it's valid, the full functionality unlocks.

This is a real paywall. It's not security theater. A user can't bypass it without valid credentials from Gumroad.

The Gumroad API endpoint is free to use. You don't need a Gumroad developer account. You just need your product's unique ID.

I'll link to the exact API documentation in the description.

---

### SECTION 4 — What You Can and Can't Build (7:00-9:00)

What works well:

- Text processing tools (prompt generators, content formatters, analyzers)
- Calculators (financial, fitness, business)
- Checklist and decision-tree apps
- Portfolio or catalog displays
- Simple games
- API-powered tools where the user brings their own key

What doesn't work:

- Anything that needs user accounts with persistent cross-device data
- Anything that needs server-side computation for security reasons (don't validate payments server-side from a front-end only app)
- Real-time collaborative tools
- Anything that stores sensitive data long-term

Knowing the boundary matters. Don't try to make this work outside its lane.

---

### SECTION 5 — A Real Example (9:00-10:30)

One of my products is a prompt engineering tool. The user pastes a rough idea, the tool reformats it into a structured prompt using a set of templates I built in, and outputs a ready-to-use prompt for Claude or GPT.

The entire app is 340 lines of HTML and JavaScript. The logic is simple: parse the input, apply the templates, render the output. No AI call required. No API key. Just string manipulation.

It sells for $9.99. A few hundred downloads. Zero hosting costs ever.

That's the model. Build the logic once. Distribute forever at zero marginal cost.

---

### OUTRO (10:30-11:00)

If you want the template I use as a starting point for these apps, it's in the description. It includes the Gumroad license check already wired up. You just swap in your product ID and build your logic on top.

---

**CTA:** GitHub template link or Gumroad guide

---

---

## Script 3: "The Behike Terminal: Building a Natural Language Interface for Non-Coders"

**Target length:** 10-12 min
**Hook type:** Product build narrative
**CTA:** Waitlist or early access

---

### HOOK (0:00-0:45)

The problem with most AI tools is they still require you to think like a developer. You need to know what prompt to write, what tool to call, what format the output should be in.

I wanted to build something different. A terminal where you type what you want in plain language and something actually happens. File gets created. Product gets drafted. Task gets logged. Code gets written.

I call it the Behike Terminal. Here's how I built it and why the architecture matters.

---

### SECTION 1 — What It Actually Is (0:45-2:30)

The Behike Terminal is a natural language command interface. You type a plain sentence and the system interprets it, routes it to the right tool or agent, executes it, and returns a result.

This is different from a chatbot. A chatbot gives you text back. The Terminal does things.

Examples of what works:

- "Draft a product description for my AI finance guide" — returns a formatted description, saves it to the product file
- "What are my open tasks?" — reads the task queue and returns a summary
- "Add this idea to the vault" — logs the idea to the appropriate category
- "Build a landing page for [product]" — generates the HTML file

The idea comes from how I actually work. I think in sentences, not in menus. Every time I had to context-switch to a different tool, I lost momentum. The Terminal collapses that.

---

### SECTION 2 — The Architecture (2:30-5:30)

Three layers.

**Layer 1: Intent Parser.** The raw input goes to Claude (the API, not the app). I give it a system prompt that defines a set of intents — roughly 20 categories. Claude classifies the input and returns a structured JSON object: intent, entities, parameters.

For example: "Draft a product description for my AI finance guide" returns:
```json
{
  "intent": "draft_content",
  "type": "product_description",
  "subject": "AI finance guide"
}
```

**Layer 2: Router.** A Python function reads the intent and calls the appropriate handler. Draft content goes to the content generator. Task queries go to the task manager. Vault operations go to the file system handler.

**Layer 3: Handlers.** Each handler is a self-contained module. The content generator has its own prompts, its own output formatting, its own file write logic. Adding a new handler doesn't touch anything else.

This is a standard agent architecture but kept intentionally simple. No LangGraph, no AutoGen. Just Python functions and the Anthropic API.

---

### SECTION 3 — What Was Hard (5:30-7:30)

Intent classification sounds simple until you deal with ambiguous inputs.

"Help me with the store" — is that content, code, or product listing? The parser guesses, but guesses wrong about 15% of the time.

My fix was adding a confirmation step for ambiguous inputs. If Claude's confidence score on the intent is below a threshold, the Terminal asks a clarifying question before executing. This slowed things down slightly but reduced bad executions significantly.

The other hard part: context. The Terminal doesn't have persistent memory across sessions by default. If I said "work on the thing we were building yesterday," it had no idea what I meant.

I solved this with a session context file. At the start of each session, I write the current project and focus area. The parser gets that context in every call. It's not elegant, but it works.

---

### SECTION 4 — What Non-Coders Actually Get From This (7:30-9:30)

I originally built this for myself. But when I showed it to a few people who don't code, the reaction was interesting.

The thing they responded to wasn't the speed. It was the reduction in decision fatigue. They didn't have to choose a tool, navigate a UI, or figure out which feature to use. They just said what they wanted.

One person told me it felt like having an assistant that actually understood context, as opposed to an app that makes you learn its language.

That's the design goal. The Terminal learns your language, not the other way around.

---

### SECTION 5 — Where This Goes (9:30-11:00)

The version I'm running now is personal. It knows my vault structure, my product catalog, my task system. It's tuned for my workflow.

The next phase is making it configurable. You define your context — your folders, your tools, your common intents — and the Terminal adapts. The core architecture stays the same; the handlers change.

I'm not sure yet whether this becomes a product or stays a personal tool. But building it taught me more about how to structure agent systems than any tutorial I've read.

---

### OUTRO (11:00-12:00)

If you want to follow the build, I'm documenting it as I go. Subscribe and check the description for the early access list if you want to try it when it's ready for other people.

---

**CTA:** Early access waitlist

---

---

## Script 4: "How I Use Claude Code to Build Faster Than a Team"

**Target length:** 9-11 min
**Hook type:** Honest comparison
**CTA:** Gumroad AI tools guide

---

### HOOK (0:00-0:45)

I want to be honest about something upfront: using Claude Code to build faster than a team comes with real trade-offs. It's not magic. It's a specific kind of speed that works in specific conditions.

I've been using it as my primary dev environment for several months. Here's what it's actually like, including where it fails.

---

### SECTION 1 — What Claude Code Is and Isn't (0:45-2:30)

Claude Code is a terminal-based interface where Claude has direct access to your file system. It can read files, write files, run commands, and execute code. It's not a chatbot you paste code into. It's an agent that operates in your project.

What this means practically: I don't context-switch between my editor and an AI chat window. I describe what I want, Claude does it, I review the result. The feedback loop is fast.

What it isn't: a replacement for understanding what you're building. If you don't know the architecture you want, Claude will invent one that may or may not match your mental model. You still have to make the design decisions. Claude executes them.

---

### SECTION 2 — What I Actually Use It For (2:30-5:00)

These are the categories where I get the most value.

**Scaffolding.** Starting a new project is always the most inertia-heavy part. I describe the structure I want — file layout, module names, class responsibilities — and Claude generates the skeleton. Then I fill it in. This alone saves me an hour on new projects.

**Boilerplate.** Argument parsing, logging setup, config file loading, error handling wrappers — I know how to write these. I just don't want to. Claude does them correctly while I focus on the logic that actually matters.

**Debugging.** When something breaks, I describe the symptom and ask Claude to trace through the relevant code. It's not always right, but it's fast. I usually find the issue within two rounds of back-and-forth.

**Documentation.** I write the code, Claude writes the docstrings and README. This is the highest-value swap for me because documentation is the thing I always skip.

---

### SECTION 3 — The Comparison to a Team (5:00-7:30)

I want to be careful here because "faster than a team" needs context.

What I mean: for the kind of projects I build — single-developer tools, digital products, automation scripts, small web apps — I can ship at a speed that would require 2-3 people working in parallel if I were writing everything myself.

What I don't mean: I can build Stripe or a healthcare platform faster than an engineering team. Those require architectural review, security audits, redundant systems, and coordination that no single operator can replace.

The use case where Claude Code wins is small-scope, move-fast, break-and-fix-quickly work. Prototypes. Product MVPs. Personal tools. Automation pipelines.

The two places where it slows me down:

First, when the codebase gets large. Claude has context limits. On big projects, it loses track of architecture decisions made in files it's not currently reading. I compensate with explicit context files that describe the project structure.

Second, when I don't know what I want. If my mental model is vague, Claude's output is vague. The quality of what comes out is directly proportional to the clarity of what I put in.

---

### SECTION 4 — Practical Habits That Make It Work (7:30-9:30)

Things I do consistently:

Write a CONTEXT.md in every project. One page, describes the project purpose, tech stack, file structure, and any non-obvious decisions. Claude reads this at the start of every session.

Review everything before it runs. Claude Code can execute commands. I read what it's about to do before I confirm. This caught a few cases where it was about to delete something I wanted.

Work in short sessions. I've found that 45-minute focused Claude Code sessions produce better results than open-ended ones. After 45 minutes the context gets noisy and I start seeing more hallucinations in the output.

Commit frequently. After every meaningful change, I commit. This gives me a rollback point if Claude's next change breaks something.

---

### OUTRO (9:30-11:00)

I'm not saying this is the right workflow for everyone. I'm saying it's the right workflow for how I build — fast, solo, iterative, with high tolerance for throwing away code that doesn't work.

If you want to see the full list of AI tools I use day-to-day, including Claude Code and what I pair it with, that guide is linked in the description.

---

**CTA:** AI tools guide on Gumroad

---

---

## Script 5: "Building in Puerto Rico: The Advantages Nobody Talks About"

**Target length:** 8-10 min
**Hook type:** Contrarian geographic angle
**CTA:** Newsletter or community

---

### HOOK (0:00-0:45)

Everyone talks about building in San Francisco or New York or Lisbon. I build in Puerto Rico and I think the advantages here are genuinely underrated.

Not lifestyle content. Not "here's my beach view." I mean actual structural advantages for running a digital business from here. Some of these are legal. Some are timezone-related. Some are cultural.

Let me walk through them.

---

### SECTION 1 — The Tax Structure (0:45-3:00)

Act 60 is real and it's worth understanding.

Under Act 60, if you establish bona fide residency in Puerto Rico and have a qualifying business, certain categories of income get taxed at very different rates than they would on the US mainland. Export services income can qualify for a 4% corporate tax rate. Capital gains accrued after becoming a resident can be taxed at 0% at the Puerto Rico level.

I'm not a tax attorney. I'm not giving you tax advice. What I'm saying is this: if you're building a digital business that generates income from services or products sold outside Puerto Rico, you owe it to yourself to spend two hours reading the actual Act 60 documentation and talking to a CPA who specializes in it.

The people who dismiss Act 60 as "tax dodging" usually haven't read it. It's a deliberate economic development incentive created by the Puerto Rico government to attract business investment. Using it legally is not a moral failing.

For someone building a digital product business or a services company, the math can look very different here than it does in a high-tax mainland state.

---

### SECTION 2 — Timezone (3:00-5:00)

Puerto Rico is Atlantic Standard Time year-round. No daylight saving. This is actually a significant operational advantage.

In the winter, I'm one hour ahead of EST. In the summer, I'm two hours ahead of EST. But I'm always four hours ahead of PST.

What this means: I can work my morning hours — roughly 7am to noon — and still be fully available to US East Coast clients or collaborators during their core business hours. By the time West Coast people start their day, I've already put in a full work session.

For someone building products with an international audience, being Atlantic Time means my morning overlap with Europe is also reasonable. I'm not fighting the Pacific Coast problem of being out of sync with the entire East Coast.

This is a small thing individually. Over a year of business operations, it compounds.

---

### SECTION 3 — Bilingual Default (5:00-7:00)

I think in Spanish and English at the same time. This is not a skill I cultivated — it's just what growing up here produces.

For building a content business, this is a genuine multiplier. The US Spanish-speaking market is the second-largest Spanish-speaking market in the world. It is also consistently under-served by the tech and business education space.

When I create a product in English and then adapt it for a Spanish-speaking audience, I'm not translating. I'm rewriting from the same native context. The voice stays consistent. The cultural references land. The framing makes sense.

Most US-based creators who try to reach Latin American or US Hispanic audiences either skip it entirely or do a surface-level translation that reads like a machine output. I don't have that problem.

The untapped market here is real. I'm building toward it.

---

### SECTION 4 — Cost Structure (7:00-8:30)

My operating costs are lower here than they would be in New York or San Francisco. Not dramatically lower on everything, but meaningfully lower on rent and certain services.

For a bootstrapped solo business where margin matters at every stage, this is real. The money I'm not spending on overhead is capital I can put into product development, tools, or inventory for the reselling side.

This is not a "tropical paradise cost of living" pitch. Puerto Rico is not a cheap place to live. But it is materially cheaper than the major US tech hubs, and when you pair that with the Act 60 potential, the math starts to look interesting for a certain profile of digital business owner.

---

### OUTRO (8:30-9:30)

I'm not saying Puerto Rico is the right base for every builder. I'm saying the people who write it off without doing the actual analysis are leaving something on the table.

If you're thinking seriously about where to base a digital business and you haven't looked at Puerto Rico, look at Puerto Rico.

More on how I structure the business side of this in the newsletter. Link in the description.

---

**CTA:** Newsletter signup

---

---
title: "Batch 28 — AI Workflow & Productivity"
batch: 28
theme: ai-workflow
created: 2026-03-22
scripts: 5
status: ready
---

# Batch 28 — AI Workflow & Productivity
# 5 scripts on how I actually use AI to build faster

---

## SCRIPT 1
### "How I use Claude to build 10x faster (actual workflow, not theory)"

**Target length:** 1,000-1,200 words
**Product tie-in:** Claude Code Course ($19.99) — behike.shop
**Thumbnail concept:** Split screen. Left: terminal with Claude output. Right: completed product. Text: "10x faster. For real."

---

**[HOOK — 0:00-0:15]**

[B-roll: terminal window, Claude generating code in real time]

Six months ago I was spending three hours building something that now takes twenty minutes. Same problem. Same me. Different approach.

This is what changed.

---

**[INTRO — 0:15-0:45]**

[B-roll: laptop on desk, Puerto Rico through the window]

I'm a computer engineering student. I build AI products on the side. I have 25 of them live on Gumroad right now, most of them built with Claude as my primary tool.

Not as a chatbot. As a collaborator that holds context, understands my architecture, and writes code that actually fits my system.

There's a specific way to use Claude that makes it 10x faster. Most people skip it. I'm going to show you exactly what it looks like.

---

**[SECTION 1 — 0:45-2:30]**
**[00:45] The mistake: using Claude like a search engine**

[B-roll: browser search bar, generic AI chat interface]

The default way people use Claude: type a question, get an answer, copy the code.

That's not a workflow. That's autocomplete with better grammar.

The problem is context. When you start a new chat every time, Claude knows nothing about your project. It gives you generic code. Generic answers. You spend more time fixing the output than writing it yourself.

The fix is simple. You give Claude context before you ask for anything.

---

**[SECTION 2 — 2:30-4:15]**
**[02:30] CLAUDE.md: the file that changes everything**

[B-roll: VS Code with CLAUDE.md file open, scrolling through it]

CLAUDE.md is a plain text file you put in your project root. Claude reads it at the start of every session.

In that file I put: what the project does, what the tech stack is, what patterns I use, what I never want Claude to do.

The result: Claude stops giving me generic code and starts giving me code that fits my actual project.

Every minute you spend writing CLAUDE.md saves ten minutes of back-and-forth later.

---

**[SECTION 3 — 4:15-6:00]**
**[04:15] The three-phase build loop**

[B-roll: split screen, code on left, Claude conversation on right]

My actual build loop has three phases.

Phase one: architecture. I describe what I'm building and ask Claude to outline the structure before writing a single line. This surfaces problems before they're in code.

Phase two: implementation. I work section by section. I paste the current state, describe the next piece, and let Claude write it. I review. I ask one targeted follow-up if something is off.

Phase three: review. I paste the full file and ask Claude to check for bugs, missing edge cases, and anything that contradicts the architecture from phase one.

Three phases. Not one long session. Not ten short ones.

---

**[SECTION 4 — 6:00-7:45]**
**[06:00] How I handle context limits**

[B-roll: long scroll through a codebase, then a fresh chat window]

Claude has a context window. For long projects, you will hit it. Here's what I do.

I keep a running file called progress.md. At the end of each session, I paste a summary of what was built, what decisions were made, and what comes next. When I start a new session, that file goes in first.

It's not perfect memory. But it's good enough. The session doesn't feel like starting over.

[B-roll: progress.md file being pasted into a chat]

This habit also forces me to think clearly about what I just built. That clarity saves time on its own.

---

**[SECTION 5 — 7:45-9:30]**
**[07:45] The prompts that actually work**

[B-roll: typing into Claude interface, response appearing]

Most prompts are too vague. "Build me a web scraper." Claude gives you something generic that may not fit anything.

The prompts that work follow a pattern: context, constraint, output format.

"Here is my current data pipeline [paste]. I need a function that takes a URL, fetches the HTML, and returns a dict of the title, description, and first three image URLs. Return only the function and its imports."

That specificity gives Claude a narrow target. Narrow targets produce usable output.

---

**[SECTION 6 — 9:30-11:00]**
**[09:30] What 10x actually means**

[B-roll: calendar view, compressed timeline of product builds]

Ten times faster doesn't mean you build ten times more. It means the same effort produces ten times the output.

For me that looks like: 25 digital products in six weeks. Guides, apps, templates, web tools. One person. One laptop. No team.

Claude handled most of the first drafts. I handled the decisions, the architecture, and the edit passes.

That's the honest picture. Claude is fast. I'm the one who decides what gets built and whether it's any good.

---

**[CONCLUSION + CTA — 11:00-11:30]**

[B-roll: Gumroad page, behike.shop storefront]

The full breakdown of my Claude workflow, including the CLAUDE.md template, the prompts I use most, and the build loop step by step, is in my Claude Code Course.

It's $19.99. Link in the description.

If you're building anything with AI and you're still starting from scratch every session, that's the thing to fix first.

---

---

## SCRIPT 2
### "The CLAUDE.md file that runs my entire dev setup"

**Target length:** 1,000-1,200 words
**Product tie-in:** Claude Code Course ($19.99) — behike.shop
**Thumbnail concept:** Close-up of CLAUDE.md file contents. Text overlay: "This file changed everything."

---

**[HOOK — 0:00-0:15]**

[B-roll: terminal, ls command showing CLAUDE.md in project root]

One file. 200 lines. It's the reason every project I start feels like Claude has been working on it for weeks.

I'm going to show you exactly what's in it.

---

**[INTRO — 0:15-0:45]**

[B-roll: desk setup, laptop open]

Most people who use Claude for development treat it like a calculator. Type in a problem, get an answer, move on.

The problem: every session starts cold. Claude has no idea who you are, how you code, what tools you use, or what already exists in your project.

CLAUDE.md fixes that. It's a context file that loads at the beginning of every session and tells Claude everything it needs to know to be useful immediately.

This is the format I've settled on after months of iteration.

---

**[SECTION 1 — 0:45-2:30]**
**[00:45] What CLAUDE.md actually is**

[B-roll: plain text editor with CLAUDE.md open, slow scroll]

CLAUDE.md is a Markdown file you put in the root of your project. When you start a Claude session in that directory, it reads the file automatically.

Think of it as a briefing document. The same way a new contractor reads the codebase docs before touching anything, Claude reads your CLAUDE.md before writing a single line.

It's not magic. It's context management. But context management is most of the work.

---

**[SECTION 2 — 2:30-4:30]**
**[02:30] The five sections I include in every CLAUDE.md**

[B-roll: each section heading highlighted in sequence]

Every one of my project CLAUDE.md files has these five sections.

One: Who you are. What the project is, who built it, and what problem it solves. Three sentences max.

Two: Tech stack. Languages, frameworks, tools, versions. A clean list.

Three: Architecture decisions. Why I chose what I chose. This is the section that prevents Claude from suggesting a React rewrite when you're intentionally in vanilla JS.

Four: Code style rules. Variable naming conventions, file structure preferences, things I always want done a certain way. This replaces the need to repeat yourself every session.

Five: What not to do. Specific patterns I want Claude to avoid. Overengineering. Unnecessary abstractions. Anything I've had to undo before.

---

**[SECTION 3 — 4:30-6:15]**
**[04:30] The actual content I have in mine**

[B-roll: CLAUDE.md file, specific lines visible on screen]

A few lines from my main one so you can hear what it sounds like in practice.

"This project is a personal operating system for a one-person business. Python backend. Minimal dependencies. No Docker. Do not suggest cloud services unless I ask."

"File naming: snake_case for Python, kebab-case for HTML/CSS files. Never camelCase."

"Priority order: working, readable, fast. In that order. Do not optimize prematurely."

Those three lines alone save 20 minutes per session of corrective prompting.

---

**[SECTION 4 — 6:15-8:00]**
**[06:15] The difference it makes in practice**

[B-roll: side by side chat, one without CLAUDE.md context, one with]

Without CLAUDE.md: "Here's a Python script to connect to your database. I used SQLAlchemy with PostgreSQL since that's a common setup."

I don't use PostgreSQL. I don't use SQLAlchemy. Now I have to explain my actual setup before I can use any of that.

With CLAUDE.md: "Here's the SQLite connection using your existing db.py pattern."

It reads the file. It knows your setup. It gives you code that fits.

That's the difference between a tool and a collaborator.

---

**[SECTION 5 — 8:00-9:30]**
**[08:00] One CLAUDE.md vs multiple**

[B-roll: file tree with multiple projects, each with its own CLAUDE.md]

I have one per project. They're not long. The shortest one I have is 40 lines.

The key is specificity. A CLAUDE.md that says "I like clean code" is useless. A CLAUDE.md that says "Functions should be under 30 lines, one responsibility each, no nested conditionals deeper than two levels" changes your output.

Write it like you're briefing a capable developer who just joined the project today.

---

**[SECTION 6 — 9:30-10:45]**
**[09:30] The master CLAUDE.md**

[B-roll: ~/behique CLAUDE.md file, long scroll through all sections]

Beyond per-project files, I have a master one at my root directory. It contains everything about me as a developer: my general preferences, the tools I have installed, my personal philosophy about what good code looks like.

That file is the reason even brand new projects start with a Claude that already knows how I think.

It took three hours to write. It's saved thirty.

---

**[CONCLUSION + CTA — 10:45-11:15]**

[B-roll: Claude Code Course product page on Gumroad]

My Claude Code Course includes my actual CLAUDE.md template, a walkthrough of how I built it, and the exact session structure I use for every project.

$19.99 at behike.shop. Link below.

Write the file once. It pays for itself the first week.

---

---

## SCRIPT 3
### "Background agents explained: build while you sleep"

**Target length:** 1,000-1,200 words
**Product tie-in:** AI Employee Guide ($19.99) + Claude Code Course ($19.99) — behike.shop
**Thumbnail concept:** Laptop closed on a desk, dark room. Notification pops up: "Task complete." Text: "While you were asleep."

---

**[HOOK — 0:00-0:15]**

[B-roll: phone screen showing a completed task notification at 3am]

I went to sleep with five unfinished tasks. I woke up to five completed files.

No one else was working. Here's what actually happened.

---

**[INTRO — 0:15-0:45]**

[B-roll: laptop desk, files open in a file manager]

Background agents are AI processes that run without you watching them. You give them a task, they execute it, they return the result.

Most people have heard of this concept. Few have set it up in a way that's reliable enough to trust while they sleep.

This is how I use them in my actual build pipeline right now.

---

**[SECTION 1 — 0:45-2:30]**
**[00:45] What a background agent actually is**

[B-roll: terminal window, process running, cursor blinking in a separate window]

A background agent is a script or process that runs on your machine or in the cloud and performs a task without continuous human input.

The task can be anything with a well-defined output: write a document, generate 10 product descriptions, scrape a list of URLs, build a file from a template.

The key word is "well-defined." Agents that fail usually fail because the task wasn't specified well enough. Garbage in, garbage out.

The better the brief, the better the output. True for human contractors and AI agents both.

---

**[SECTION 2 — 2:30-4:15]**
**[02:30] My current background agent setup**

[B-roll: task queue list, multiple items with status indicators]

Right now I run background agents for three categories of work.

Content creation: product descriptions, Instagram captions, newsletter drafts. These follow templates. The agent fills the template from a spec file.

Research: competitive analysis, pricing checks, trend summaries. The agent fetches data, structures it, saves it to a file for me to review.

Code generation: boilerplate files, landing page shells, configuration templates. The agent uses my CLAUDE.md patterns to generate code that fits my stack.

None of these require me to be at the computer.

---

**[SECTION 3 — 4:15-6:00]**
**[04:15] How I structure the task files**

[B-roll: task file open in editor, JSON or YAML format]

Every background agent task gets a spec file. The format I use:

Task name. What it is. Output path. Where to save the result. Context. Any files the agent needs to read first. Requirements. Specific rules for this task. Format. What the output should look like.

With a spec file this complete, the agent doesn't guess. It produces something I can use within one edit pass.

That edit pass is important. I always review background agent output. I never ship it raw.

---

**[SECTION 4 — 6:00-7:45]**
**[06:00] The failures and how to avoid them**

[B-roll: error output in terminal, then corrected spec file]

Background agents fail in predictable ways.

Vague task definition: the agent produces something technically correct but wrong for your context.

Missing context: the agent doesn't know what already exists, so it contradicts or duplicates it.

No output format specified: you get a wall of text instead of a structured file.

All three are spec file problems, not agent problems. Fix the spec. The agent fixes itself.

---

**[SECTION 5 — 7:45-9:30]**
**[07:45] The economics of background agents**

[B-roll: calendar, 6 weeks of build output across 25 products]

I built 25 digital products in six weeks. Some of that happened during active sessions. A significant portion happened while I was in class, sleeping, or doing something else.

The time I spent on background agent setup: maybe four hours total, spread across the whole period.

The time those agents saved: I don't have an exact number. But I can tell you that 25 products in six weeks is not possible for one person without them.

[B-roll: Gumroad storefront with 25 products visible]

Four hours of setup. Continuous background output for weeks.

---

**[SECTION 6 — 9:30-10:45]**
**[09:30] What you need to get started**

[B-roll: minimal setup: laptop, terminal, a few folders]

You don't need a server. You don't need a GPU. You need: a task spec format you trust, a model with good instruction-following, and a review habit.

The review habit is the most important. Background agents are multipliers. They multiply what you give them. If you give them bad specs and ship the output without looking, you publish bad content at scale.

Give them good specs. Review the output. Then ship.

---

**[CONCLUSION + CTA — 10:45-11:15]**

[B-roll: AI Employee Guide product on behike.shop]

The AI Employee Guide covers my full background agent setup, the spec file templates I use, and the exact categories of work I've automated.

$19.99 at behike.shop. Link in the description. The guide is the actual system, not a tutorial on how to think about it.

---

---

## SCRIPT 4
### "Why most AI productivity advice is wrong (and what actually works)"

**Target length:** 1,000-1,200 words
**Product tie-in:** Solopreneur OS ($12.99) + AI Prompt Cheat Sheet ($9.99) — behike.shop
**Thumbnail concept:** Red X over a generic "AI productivity tips" title card. Text: "This is why it doesn't work."

---

**[HOOK — 0:00-0:15]**

[B-roll: scrolling through a generic AI tips Twitter thread]

"Use AI to save 10 hours a week." The advice sounds good. Then you try it and save maybe 20 minutes.

Here's what's actually happening.

---

**[INTRO — 0:15-0:45]**

[B-roll: desk, notebook, laptop, no phone visible]

Most AI productivity content is written by people who use AI to write content about using AI. The loop is self-referential and mostly useless.

I'm going to give you an honest picture of what AI productivity looks like when you're building something real. What works. What doesn't. And why the gap exists.

---

**[SECTION 1 — 0:45-2:30]**
**[00:45] The problem with tip-based advice**

[B-roll: listicle article on screen: "7 ways AI saves time"]

Tips are surface-level. "Use AI to write your emails." "Use ChatGPT for brainstorming." "Let AI handle repetitive tasks."

All technically true. None of them tell you what to actually change about how you work.

The underlying issue: AI tools don't save time on their own. They save time when they fit into a system. A system that doesn't exist yet for most people.

Without the system, AI is one more thing to think about. It adds cognitive load instead of removing it.

---

**[SECTION 2 — 2:30-4:30]**
**[02:30] What actually saves time: context, not prompts**

[B-roll: CLAUDE.md file, progress.md file, system folder structure]

The single biggest productivity gain I've gotten from AI has nothing to do with prompts. It's from context management.

When Claude knows my project, my stack, my style, and my current state, the quality of output goes up dramatically. That quality gap is where the time savings live.

A slightly better prompt saves two minutes. A well-structured context system saves two hours.

Most AI productivity advice focuses on prompts. That's the wrong layer.

---

**[SECTION 3 — 4:30-6:15]**
**[04:30] The "10 hours saved per week" problem**

[B-roll: time tracking app, realistic week layout]

Here's what I actually track. Not time saved. Output per unit of focused time.

Before: one product built per week, actively working.
After: one product built per two days, same hours of focused work.

The productivity gain is real. But it's not "AI does your work while you relax." It's "AI removes friction at specific bottlenecks, so your focused hours produce more."

The hours you "save" get filled with more work. That's a good thing if you're building.

---

**[SECTION 4 — 6:15-8:00]**
**[06:15] What I actually do differently**

[B-roll: morning routine, screen showing primer.md loaded]

Three specific things I do that generic advice doesn't cover.

One: I start every work session by reading a context file, not by picking up from memory. The file tells Claude and me both what the current state is.

Two: I use AI for first drafts only. I never publish raw AI output. The edit pass is where my voice and judgment go in.

Three: I batch AI work. I don't ask Claude for one caption. I ask for thirty, review them, save the good ones. That batching is where the leverage is.

---

**[SECTION 5 — 8:00-9:30]**
**[08:00] The tools that actually matter**

[B-roll: simple tool list: Claude, VS Code, one note-taking app]

The AI productivity space has a new tool every week. Most of them don't matter.

What matters is depth with a small number of tools, not surface familiarity with many.

I use Claude for almost everything. Claude Code for dev work. n8n for automation. That's the core. Everything else is peripheral.

Every new tool you add requires time to learn, time to maintain, and time to troubleshoot when it breaks. The opportunity cost is real.

---

**[SECTION 6 — 9:30-10:45]**
**[09:30] The honest timeline**

[B-roll: calendar, first month marked "learning", second marked "building", third marked "shipping"]

It took me about a month of active use before AI genuinely accelerated my output. Before that month, it mostly created new kinds of work.

That's the part nobody says. The tool is not immediately faster. The system you build around it is what makes it faster.

If you're one month in and it doesn't feel 10x better, you're not behind. You're normal. Keep building the system.

---

**[CONCLUSION + CTA — 10:45-11:15]**

[B-roll: Solopreneur OS on behike.shop]

Solopreneur OS is the actual system I use. Not tips. A working structure with the context files, the session format, and the batching habits built in.

$12.99 at behike.shop. If you're tired of advice that doesn't translate to anything, this is the alternative.

---

---

## SCRIPT 5
### "My complete AI stack for building a solo product business"

**Target length:** 1,000-1,200 words
**Product tie-in:** Complete Bundle ($149.99) or AI Employee Guide ($19.99) — behike.shop
**Thumbnail concept:** Minimal grid of tool names. Clean background. Text: "The actual stack. No sponsorships."

---

**[HOOK — 0:00-0:15]**

[B-roll: terminal open, multiple tool windows visible on screen]

No sponsors. No affiliate links. Just the tools I actually use to run a product business as one person in college.

Here's the stack.

---

**[INTRO — 0:15-0:45]**

[B-roll: desk, laptop, PR through window]

I have 25 digital products live. Three channels of content publishing. A background agent pipeline that runs without me. One laptop.

The tools that make this work are not the ones you see in most "AI tools" videos. Some of them you've never heard of. Some are obvious. All of them have been tested against real work, not just demos.

---

**[SECTION 1 — 0:45-2:30]**
**[00:45] The core: Claude**

[B-roll: Claude interface, code and content generation on screen]

Claude is the center of everything. Writing, code, research, editing, summarizing.

I use the API for background agents and Claude.ai for live sessions. Live sessions give me an interactive collaborator. The API gives me a background worker.

Why Claude and not GPT-4? Honest answer: Claude follows complex instructions more consistently in my experience. That consistency matters more than raw capability at the task level.

The context management system is what makes it worth the subscription. Without that system, any model feels the same.

---

**[SECTION 2 — 2:30-4:15]**
**[02:30] Development: VS Code + Claude Code**

[B-roll: VS Code interface with Claude Code extension active]

For anything involving code, Claude Code runs inside VS Code. It has context of the full codebase, not just a single file.

The difference: instead of pasting code into a chat, Claude reads the whole project. It catches cross-file inconsistencies. It suggests changes in context.

Significant when you're building something with ten interconnected files.

---

**[SECTION 3 — 4:15-6:00]**
**[04:15] Automation: n8n**

[B-roll: n8n canvas with a workflow visible, nodes connecting]

n8n is my automation layer. It runs locally. It connects every service I use.

Current workflows: when a new Gumroad sale comes in, log it and send a summary. When I add a task to my note system, create a structured brief. When a background agent completes, send me a notification.

None of these are impressive on their own. Together, they remove the low-value work that used to interrupt my build sessions.

---

**[SECTION 4 — 6:00-7:45]**
**[06:00] Content: CapCut + transcript pipeline**

[B-roll: CapCut interface, video editing with AI tools visible]

For content I use CapCut and a custom transcript pipeline.

The pipeline: I record or find audio, run it through Whisper for transcription, clean the transcript with Claude, use the cleaned text as a base for captions, threads, or newsletter sections.

One piece of content becomes five. That's the batching system in practice.

---

**[SECTION 5 — 7:45-9:30]**
**[07:45] Storage and memory: Obsidian + flat files**

[B-roll: Obsidian graph view, connected notes]

I use Obsidian for knowledge management and flat files for everything operational.

The operational layer is intentionally simple. Markdown files in a folder. No database. No sync service.

The reason: complexity in storage creates friction in retrieval. When I need context, I want to open a file, not query a system.

Obsidian is for patterns and knowledge. The flat file system is for the state of the business right now.

---

**[SECTION 6 — 9:30-10:45]**
**[09:30] What's not in the stack**

[B-roll: long list of popular tools with soft strikethrough effect]

Notion: tried it. The structure felt heavier than the value it gave.

Zapier: replaced by n8n. More control, runs locally, costs less.

Midjourney: I use it occasionally. Not in my daily stack.

Perplexity, Gemini, and everything else: I try them. They don't displace Claude for my use case.

The tools I don't use are not worse tools. They're tools that don't fit how I work. Know the difference.

---

**[CONCLUSION + CTA — 10:45-11:15]**

[B-roll: behike.shop Complete Bundle page]

The complete stack breakdown, with setup notes and the context files that make each tool useful, is in the AI Employee Guide at behike.shop.

If you want everything at once, the Complete Bundle has all 25 products. $149.99 for the full set.

Links in the description.

---

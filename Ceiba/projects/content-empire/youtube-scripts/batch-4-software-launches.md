# YouTube Scripts — Batch 4: Software Product Launches
# Channel: Main (personal brand) + AI Tools faceless
# Created: 2026-03-22 (Session 17)

---

## SCRIPT 1: "I Built a Local AI That Reads Your Books"
**Product:** Book Agent
**Channel:** Main (personal brand) or AI Tools faceless
**Format:** Screen recording demo + talking head
**Length:** 6-8 minutes
**Hook type:** Problem → reveal

---

[HOOK — first 15 seconds]

You spend $30 on a book. You read it. Three weeks later someone asks you about it and you remember... maybe a chapter.

Here's the app I built to fix that. It runs on your laptop. It never sends your data anywhere. And it cost me $9.99 to buy.

[INTRO CARD: "Book Agent — Chat with your books. Built local. Privacy first."]

---

[PROBLEM — 60 seconds]

There's a whole stack of books I've bought that I can barely summarize. I'll remember a quote or a concept, but not where it came from. So I search the whole thing manually.

That's not reading. That's archaeology.

I also tried ChatGPT. Uploaded a PDF and asked questions. Two problems: it gets things wrong. It hallucinates. And it costs money every time I send a message.

I wanted something that answers from the actual text. Not from training data. Not from memory. From the book itself, every time.

---

[SOLUTION REVEAL — 90 seconds]

So I built Book Agent.

[SCREEN SHARE: browser opens to localhost:7860]

It's a Flask web app. One Python file. You run it locally, it never sends anything to a server.

[DEMO: drag Atomic Habits PDF into the upload zone]

Watch what happens when I drop a PDF in.

It reads the whole book. Chunks it into sections. Builds a search index. Takes about 10 seconds.

[DEMO: type "What is the 2-minute rule?"]

And now I can ask questions.

[DEMO: read the answer out loud]

That answer came from page 162 of the book. The actual text, not ChatGPT's training memory.

[DEMO: ask "What chapter covers identity?"]

It searches by relevance. It finds the actual section. And because it runs on Ollama, which is a local AI framework, the whole conversation happens on my machine. No API costs. No privacy risk.

---

[HOW IT WORKS — 90 seconds]

Here's the technical bit. Skip to the next chapter if you just want the demo.

When you upload a book, Book Agent breaks it into 500-word chunks. Then it builds a TF-IDF index. That's a standard information retrieval technique — it scores each chunk by how relevant it is to your question.

When you ask something, it finds the 4 most relevant chunks. Then it passes those to the AI with instructions: "Answer from these excerpts only. If the answer isn't here, say so."

That's the key. The AI is grounded. It can't make things up because we're not asking it to recall from memory. We're feeding it the answer and asking it to explain it clearly.

And because the whole thing runs locally on Ollama — no internet required.

---

[DEMO EXTENDED — 2 minutes]

Let me show you a few more queries.

[DEMO: "What does the book say about habits and identity?"]
[DEMO: "Summarize the Four Laws of Behavior Change"]
[DEMO: Load a second book — $100M Offers — and switch between them]

I have 12 books indexed right now. Different genres. Different topics. Each one is its own conversation thread.

---

[SETUP — 60 seconds]

Setup takes 3 commands.

[SCREEN: terminal]

```
pip install flask requests PyPDF2
```

Then if you have Ollama: `ollama pull qwen2.5:7b`

Then: `python3 app.py`

Open localhost:7860. That's it.

If you don't want to install Ollama, set your OpenAI API key as an environment variable and it'll use GPT-4o-mini instead. Still private, just uses OpenAI's server.

---

[CLOSE]

Book Agent is $9.99. One-time. Link in the description.

If you want to build this yourself from scratch, I'll do a full coding breakdown in a separate video. Drop a comment if you want that.

And if you liked this, there's more coming. I'm building a whole stack of tools that run locally on my laptop. Next up is a screen wellness app. Timestamp in the description when that goes live.

Subscribe and I'll see you there.

---

## SCRIPT 2: "I Deleted f.lux and Built Something Better"
**Product:** Lumina
**Channel:** Main or Productivity faceless
**Format:** Screen demo + talking head
**Length:** 5-7 minutes
**Hook type:** Comparison → reveal

---

[HOOK — first 15 seconds]

I've been using f.lux since 2016. It's a great app. It was built in 2008.

I wanted something built for how I actually use a computer in 2026. So I built Lumina.

[INTRO CARD: "Lumina — Blue light. Focus. Sleep. Sound. One app."]

---

[THE PROBLEM — 90 seconds]

Here's my screen stack from last month:

- f.lux for blue light
- Noisli for ambient sound ($7/month)
- Flow for Pomodoro timers ($5/month)
- Calm for breathing exercises ($70/year)
- Some random sleep calculator I found on Google

Five apps. $100+ a year. None of them talk to each other.

And f.lux specifically — love it, but it's one thing. It filters blue light. That's it. The interface hasn't changed since the Obama administration.

I wanted everything in one place. No subscriptions. No sign-up. No data anywhere.

---

[SOLUTION REVEAL — 2 minutes]

[SCREEN: open Lumina in browser]

This is Lumina. It's a single HTML file. You open it in your browser. Nothing to install.

Dashboard shows the time, sunrise and sunset, and your current screen temperature.

[DEMO: drag the temperature slider from 6500K to 2700K]

Watch the whole screen. The overlay shifts warm as I pull it toward candlelight.

That's the blue light filter. The actual color shift is a CSS overlay on the browser window. It doesn't control your OS color temperature — I'll explain what that means in a second — but for browser work, it's genuinely effective.

[DEMO: click on Rain sound and start it]

Ambient sound. This is real Web Audio API synthesis. I'm generating noise patterns in your browser with no audio file downloaded. The rain sound is mathematical. It never loops awkwardly.

[DEMO: go to Focus tab, start a 25-minute Pomodoro]

ADHD Focus Mode. 25 minutes on. 5 minutes off. After 4 sessions, a 15-minute long break. Same as the standard Pomodoro, but it also dims the overlay slightly when you're in focus mode.

[DEMO: go to Breathe tab, start 4-7-8 breathing]

Breathing. Three patterns: 4-7-8 for sleep, box breathing for stress, calm 5-5 for general use. The orb expands and contracts with the rhythm.

[DEMO: go to Sleep tab, enter wake time 7am]

Sleep Coach. Enter when you need to wake up. It calculates bedtimes based on 90-minute sleep cycles. Six cycles is 9 hours. Five is 7.5. Four is 6. The research says waking at the end of a cycle feels better than being interrupted mid-cycle.

---

[LIMITS — 60 seconds, honest]

Couple things to be honest about.

The blue light filter is browser-only. It applies a CSS color overlay to the browser window. If you're watching a movie in QuickTime or using a different app, Lumina doesn't affect that. A full system-wide color temperature change — like what f.lux actually does — requires a native app with OS-level access. That's the Electron app I'm building for Phase 2.

But for browser work — writing, coding, reading, watching videos in Chrome — it works exactly as intended.

---

[HOW IT CONNECTS — 30 seconds]

Here's the part I actually like: it's all in one place.

Before Lumina, I'd be in focus mode in one app, then switch to another for ambient sound, then forget to turn on the blue light filter. Three apps, three friction points.

Now I open one browser tab at the start of my work session and everything runs together.

---

[CLOSE]

Lumina is $9.99. Free tier includes the full Pomodoro, all breathing exercises, and rain sound. Pro unlocks the other five soundscapes and the sleep coach.

Link in the description. It's a single HTML file. No install. No sign-up.

More tools coming. Subscribe and I'll see you in the next one.

---

## SCRIPT 3: "I Automated My Morning Routine with One Python Script"
**Product:** AI News Tracker Guide
**Channel:** AI Tools or Main
**Format:** Screen recording
**Length:** 5-6 minutes
**Hook type:** Routine → system reveal

---

[HOOK]

Every morning I used to spend 30 minutes reading about AI. Scrolling Twitter, checking newsletters, opening Reddit.

I still read about AI every morning. Now it takes 8 minutes. And I built a Python script to do the scrolling for me.

[INTRO CARD: "AI News Tracker — Build your own personalized feed. Zero algorithm."]

---

[PROBLEM]

The problem with Twitter for AI news: the algorithm shows you what's viral, not what's important. The problem with newsletters: they're weekly. The problem with Reddit: you have to wade through it.

I wanted a system that checks 18 sources every morning, scores each story by relevance, and gives me a clean HTML digest. No algorithm. No noise. Just what matters.

---

[DEMO — the output]

[SCREEN: open the digest HTML file in browser]

This is what I wake up to. Today's AI news, scored and ranked. Top story, estimated impact score, key entities, linked source.

Underneath that, the next 10-15 stories ranked by importance. Stories that hit multiple sources get a higher score. New topics bubble up. Recurring noise gets filtered.

---

[HOW IT WORKS]

[SCREEN: open the Python script]

It's reading 18 RSS feeds. Sources like: The Verge AI, MIT Technology Review, Wired, Hugging Face blog, OpenAI announcements, Anthropic's news, ArXiv AI papers, Google DeepMind.

For each story it pulls: title, summary, link, publication date. Then it runs a quick scoring pass. Newer stories score higher. Stories from multiple sources score higher. Stories matching keywords I care about score higher.

Then it renders everything into a clean HTML file and opens it in the browser.

The whole run takes about 45 seconds.

---

[SETUP]

The code exists as a single Python file. Dependencies: requests, feedparser, and the standard library.

[SCREEN: show the guide PDF cover]

The AI News Tracker Guide walks through every function. How to add sources. How to customize the scoring. How to set up a scheduled task so it runs automatically at 7am.

$4.99. Link in the description.

---

[CLOSE]

If you want to build this instead of buy the guide, drop a comment and I'll do a step-by-step build video.

Subscribe. New video soon.

---

## SCRIPT 4: "The $0 Workspace Setup I Actually Use"
**Product:** Lead magnet — Zero Dollar AI Stack
**Channel:** Main / faceless hybrid
**Format:** Talking head + screen b-roll
**Length:** 5-7 minutes
**Hook type:** Curiosity gap — lifestyle contrast

---

[HOOK]

I'm a computer engineering student in Puerto Rico. I don't have a big budget. My setup costs $0/month in software.

Here's the exact stack.

---

[INTRO]

There's this idea that you need expensive tools to build things. SaaS subscriptions, cloud servers, premium software. That's mostly marketing.

Everything I run to build my business: $0/month.

I'll show you each tool, what I use it for, and what I use instead of the paid alternative.

---

[THE STACK]

**Claude Code** — free tier. This is my AI assistant for writing code, building systems, planning projects. The paid version is $20/month. The free tier does everything I need.

**Ollama** — completely free. Local AI on my laptop. I run qwen2.5:7b for quick tasks. It's running on a MacBook M4. Most tasks that used to cost me $5-10 in OpenAI credits now cost me nothing.

**Obsidian** — free for personal use. Knowledge base, linked notes, project tracking. The paid sync is $10/month. I use Syncthing instead (free, open source, self-hosted sync across machines).

**n8n** — self-hosted, free. Automation workflows. The cloud version starts at $20/month. I run it on a $0 spare Windows computer I had anyway.

**GitHub** — free for public and private repos. CI/CD, version control, code storage.

**Cloudflare** — free tier. DNS management, basic DDoS protection, tunnels for exposing local services to the internet.

**Railway** — free tier for small deployments. That's where my Telegram bot runs.

**Telegram** — free. My main communication channel with myself. I have a bot that captures ideas from my phone.

**Gumroad** — free to start. They take 10% of sales. But I'm not paying anything until I'm making money.

**Canva** — free tier. Cover images, social graphics, basic design.

The only things I pay for: my domain ($10/year) and iCloud storage ($3/month because I have too many PDFs).

---

[CLOSE]

I put the full list together as a free download. It's a checklist format with links and alternatives for each tool. Link in the description. No email required.

If this was useful, subscribe. I'm building everything in public.

---

## SCRIPT 5: "I Stopped Paying for Notion and Built My Own System"
**Product:** Self-Hosted Store Guide (indirect) / lead magnet
**Channel:** Productivity faceless
**Format:** Screen recording
**Length:** 5-6 minutes
**Hook type:** Anti-SaaS, DIY revelation

---

[HOOK]

Notion is $16/month if you want AI. $12/month just for the base plan. I canceled.

Here's what I replaced it with, and it's free.

---

[THE REPLACEMENT STACK]

For notes and linked knowledge: Obsidian. Free, local, markdown files. The philosophy is your files are just files. They live on your computer. They're readable in any text editor. They never get locked in a proprietary format.

For project management: a folder system with markdown files. MASTER_TODO.md is the source of truth. PROJECTS/ contains active project files. DONE/ archives completed work.

For databases: JSON files and SQLite. Overkill for most people, but when you're a developer it's cleaner than Notion databases.

For sharing: GitHub. A private repo. Everything is backed up, version-controlled, and accessible from any machine.

The total cost: $0/month in software.

---

[WHY I DID THIS]

When Notion went down in 2024 I lost access to everything in the middle of a project. Cloud dependency is a risk.

When Notion changed their pricing I suddenly needed to pay more for the same features.

Local-first removes both risks.

---

[THE TRADE-OFF]

The trade-off is real: Notion is more polished. Notion has mobile apps that sync seamlessly. Notion has a better team collaboration model.

If you're working with a team or live on your phone, local-first isn't the right choice yet.

If you're a solo builder who sits at a desk, it's worth it.

---

[CLOSE]

I wrote a guide on building a self-hosted product store using the same philosophy — HTML, local files, no platform. It's $4.99. Link in the description.

Subscribe if you want to see more content about building without SaaS dependency.

---

## POSTING SCHEDULE

| Script | Platform | Post Date | CTA |
|--------|----------|-----------|-----|
| Script 1 (Book Agent) | Main channel | Week 1, Day 1 | book-agent.html landing page |
| Script 2 (Lumina) | Main channel | Week 1, Day 3 | lumina.html landing page |
| Script 3 (AI News Tracker) | AI Tools faceless | Week 2, Day 1 | gumroad/ai-news-tracker-guide |
| Script 4 (Zero Dollar Stack) | Main channel | Week 2, Day 3 | free download link |
| Script 5 (No Notion) | Productivity faceless | Week 3, Day 1 | self-hosted-store landing page |

## THUMBNAIL IDEAS

**Script 1 (Book Agent):** Split screen — pile of books (left) vs. clean chat interface (right). Text: "I can search any book in 3 seconds"

**Script 2 (Lumina):** f.lux UI (old, dated looking) vs Lumina UI (clean, dark). Text: "f.lux was built in 2008. I made this."

**Script 3 (AI News Tracker):** Messy Twitter feed vs clean HTML digest. Text: "My morning news: 8 minutes, zero algorithm"

**Script 4 (Zero Dollar Stack):** Tool logos with ❌ prices crossed out. Text: "$0/month AI workspace"

**Script 5 (No Notion):** Notion logo with $ → replaced by folder icons. Text: "Canceled Notion. Here's what I use."

# YouTube Scripts — Batch 34: Tool Builds
# Brand: Behike (@behikeai) | behike.shop
# Tone: Dan Koe, direct, thesis first, no hype
# Rules: No em dashes, no exclamation marks, no banned words
# Date: 2026-03-22

---

## Script 1: "I built a Pomodoro timer specifically for ADHD brains. Here is how it works."

**Format:** Tutorial / build breakdown
**Length:** ~8-10 min
**Hook type:** Problem-first

---

### HOOK (0:00 - 0:30)

The Pomodoro method doesn't work for ADHD the way it's usually taught.

Twenty-five minutes on, five off. That's the standard. The problem is that ADHD doesn't follow a clock. You either can't start, or you can't stop. The timer becomes one more thing to manage.

So I built my own version. It runs in the browser, it talks to me, and it doesn't care about the rules.

Here is exactly how it works.

---

### SECTION 1: Why the standard Pomodoro breaks down (0:30 - 2:00)

The original Pomodoro was designed for a neurotypical brain that needs to avoid burnout. Fixed intervals work when your attention is steady.

ADHD attention isn't steady. It spikes. You get hyperfocused for ninety minutes, then you can't read a sentence. The twenty-five minute interval cuts the hyperfocus and doesn't help the crash.

Three specific failures:

First: the break is a context switch. If you're deep in something, stopping to take a five-minute break destroys the state you built up. Getting back in takes longer than the break itself.

Second: the alarm creates friction. The sound interrupts. It pulls you out of flow. Then you have to decide whether to restart. That decision costs energy ADHD brains don't have left over.

Third: the system assumes you can start on command. Most ADHD sessions don't start at the top of the hour. They start whenever the brain agrees to engage, which can be 2 PM or 11 PM.

The fix isn't a different interval. The fix is a timer that adapts to the session, not the other way around.

---

### SECTION 2: What I built (2:00 - 4:30)

The tool is a single HTML file. No install, no account, no backend. You open it in a browser and it runs.

Three modes:

Mode one is called Flow. No hard stop. It tracks elapsed time in the background and surfaces a soft nudge after forty-five minutes. The nudge is a color change on the screen. Not an alarm. You can keep going or stop. The decision is yours.

Mode two is called Sprint. Fifteen minutes. Hard stop with a sound. Built for tasks you're avoiding. The kind of thing where you say "I'll do it for fifteen minutes and then quit." The short window removes the weight of the task.

Mode three is called Recovery. Ten minutes. Plays generated ambient sound. Dim screen. No text except a single countdown. It's not a break you fill with content. It's a pause.

The interface has three elements: the mode selector, the timer, and a task label you type before starting. That label matters. Naming the task before you start activates the intention. Research on ADHD executive function backs this up. The brain needs the cue.

---

### SECTION 3: The technical build (4:30 - 7:00)

The whole thing is vanilla JavaScript. No frameworks. No dependencies.

The timer is built on `setInterval` with a 1000ms tick. State lives in a single object: mode, elapsed time, task label, running status. Nothing persists after the tab closes. That's intentional. No tracking, no history, no guilt about missed sessions.

The ambient sound in Recovery mode uses the Web Audio API. A pure tone oscillator running at 40 Hz with a low-pass filter. That frequency sits in the gamma range. Some studies link it to focus. Whether it works or it's placebo, it creates a ritual. That's the real value.

The color logic is simple. Each mode has a base color. Flow is a dark teal. Sprint is a muted orange. Recovery is near-black with a blue tint. The colors signal state without words. If you glance at the screen and see orange, you know you're in a sprint. That cognitive shortcut reduces load.

The nudge in Flow mode is a gradient fade across the background. It starts at the forty-minute mark and takes five minutes to complete. By the time you notice it, you've already had forty-five minutes of work. If you want to stop, stop. If not, hit a button and the color resets.

The whole file is under 300 lines.

---

### SECTION 4: What I'd change (7:00 - 8:30)

Two things I'd add if I built version two.

First: a session log. Not a full history. Just a plaintext note appended to a local file via the File System Access API. You start a session, name the task, end the session. One line in a file. Something like: `2026-03-22 | 14:23 | Flow | 52 min | Wrote newsletter`. That record creates momentum. You can look at a week of logs and see what got done even on the hard days.

Second: a voice start. Instead of clicking a button, you say the task name out loud. The browser picks it up via the Web Speech API and starts the timer. It's a small thing but it changes the feel. Speaking the task out loud is an activation cue. It works the same way writing the name does, but faster.

I haven't built either of these yet. But I will.

---

### CLOSE (8:30 - 9:00)

The file is linked in the description. It's free. Download it, open it in a browser, use it.

If you want the next version with session logging, subscribe. I'll build it on camera.

---

---

## Script 2: "How to set up the Overnight Machine: eBay automation from scratch"

**Format:** Tutorial / system breakdown
**Length:** ~10-12 min
**Hook type:** Results-first, then method

---

### HOOK (0:00 - 0:45)

The Overnight Machine is what I call the part of my business that runs while I sleep.

It finds products, prices them, and drafts listings. In the morning I review the queue and approve the ones worth posting. The whole review takes about fifteen minutes.

This video is the build. Every tool, every step, every decision. You can copy this exactly or use it as a starting point.

---

### SECTION 1: What the machine actually does (0:45 - 2:30)

There are three stages.

Stage one is research. A script runs through eBay's sold listings using their Browse API and flags items with specific criteria: high sell-through rate, low competition in the active listings, margin above thirty percent at average sold price.

Stage two is sourcing match. The flagged items get run against a supplier list. Right now that list is Amazon, Walmart, and AliExpress via a simple web scraper. If the item exists at a source price that hits the margin target, it gets added to the queue.

Stage three is draft generation. For each approved source match, a second script generates a title, condition description, and item specifics. It follows eBay's SEO patterns: primary keyword first, condition second, key attributes third. No creative writing needed. It's formula.

The queue lives in a spreadsheet. Every morning I open it, sort by margin, and approve or reject. Approvals go directly to eBay via a listing API call.

---

### SECTION 2: The tools (2:30 - 5:00)

eBay Browse API. Free with a developer account. Gives you access to sold listings, active listings, and category data. You need this to validate demand before you source anything.

Python with requests and pandas. Requests handles the API calls. Pandas handles the data cleaning and filtering. Nothing exotic.

A sourcing scraper. I built a lightweight one using Playwright. It loads product pages on Amazon and Walmart, pulls the price, and checks stock status. This part is the most fragile because those sites change layouts. Plan to maintain it.

Google Sheets via the gspread library. The queue lives here. It's shareable, it's readable on my phone, and it doesn't require a database.

The eBay Trading API for listing creation. Separate from the Browse API. This one posts the actual listing. It requires a seller account with API access enabled.

Total cost: zero for the APIs, a few dollars a month for a VPS if you want it running automatically at night. You can also just run it manually from your laptop.

---

### SECTION 3: The setup, step by step (5:00 - 9:00)

Step one. Create an eBay developer account at developer.ebay.com. Get your App ID, Dev ID, and Cert ID. Then generate a user token. This token lets the API act on behalf of your seller account.

Step two. Set up a Python virtual environment. Install requests, pandas, gspread, and playwright. Run `playwright install` to download the browser binaries.

Step three. Write the research script. Pull sold listings for a category you know. Filter by sell-through rate above sixty percent and active listing count below twenty. This combination means high demand, low competition.

Step four. Write the sourcing script. For each flagged item, search Amazon and Walmart by title. Parse the price from the first organic result. Calculate margin: (sold price * 0.87) minus source price. The 0.87 accounts for eBay's final value fee plus PayPal. If margin is above eight dollars, add to queue.

Step five. Write the draft script. Pull the eBay title from the top-selling listing for that item. Strip out seller-specific text. Use it as the base. Add condition and key specifics. Save to Google Sheets via gspread.

Step six. Schedule it. On a Mac, use cron. On a VPS, same. A nightly run at 2 AM means the queue is ready when you wake up.

---

### SECTION 4: What breaks and how to fix it (9:00 - 10:30)

The scraper breaks most often. Amazon and Walmart update their HTML structure periodically. When the scraper returns empty, check if the selector still matches the price element. Usually a ten-minute fix.

The eBay token expires. User tokens last eighteen months. Set a calendar reminder. When it expires, the listing calls fail silently if you don't have good error handling. Add a check at the top of the listing script that validates the token before running.

Margin calculations drift. Shipping costs change, eBay adjusts fees. Revisit your margin formula every quarter. The eight-dollar floor I use today might need to be ten dollars next year.

---

### CLOSE (10:30 - 11:00)

The code for each script is in the description. It's not a polished package. It's the working version I actually use.

If you want to see me run through a real product find from research to listing in real time, let me know in the comments.

---

---

## Script 3: "Competitor Radar: the tool I built to monitor my Gumroad competitors"

**Format:** Build breakdown / strategy
**Length:** ~8 min
**Hook type:** Insight-first

---

### HOOK (0:00 - 0:30)

Pricing on Gumroad is not a one-time decision. Every week a new creator lists a product in your category. Their price affects yours. Their title affects your SEO ranking in search.

I got tired of discovering this by accident. So I built a tool that checks it for me.

---

### SECTION 1: What the tool monitors (0:30 - 2:00)

Competitor Radar tracks three things.

Price changes. If a direct competitor drops their price on a product that competes with mine, I want to know the same day, not after I notice a sales drop.

New products. When someone in my niche lists something new, I want to see the title and price. Sometimes it's noise. Sometimes it tells me what the market wants next.

Review velocity. How many new reviews a product is getting per week. A product jumping from 50 to 80 reviews in two weeks is a signal. Someone is promoting it. Worth knowing.

The tool doesn't automate any response. It just puts the information in front of me. What I do with it is my call.

---

### SECTION 2: The technical build (2:00 - 5:00)

Gumroad doesn't have a public API for competitor data. So this is a scraper.

The tool uses Playwright to load product pages in a headless browser. It pulls the title, price, review count, and rating. It stores each scrape in a SQLite database with a timestamp.

On each run, it compares the latest scrape to the previous one. If price changed, it logs it. If review count jumped by more than five percent in a week, it logs it. New products from tracked creator profiles get flagged automatically.

The alert system is simple. A Python script reads the change log and sends a Telegram message if anything crossed a threshold. I see it in my phone the same way I see any other message.

Setup takes about two hours. You need a list of competitor Gumroad URLs. Start with five. You can expand later.

---

### SECTION 3: What I actually do with the data (5:00 - 7:00)

Three decisions this has changed.

Pricing. I used to set a price and forget it. Now I see when competitors are discounting. Sometimes I match, sometimes I hold. The key is that I'm choosing, not reacting weeks later.

Product gaps. When I see a new product category get listed by three different creators in one month, that's a market signal. The Niche Sniper guide I just released came directly from this kind of observation. I noticed three creators listing product research tools. I built a better one.

Title optimization. Gumroad has a search function. Title keywords matter. When I see a competitor change their title and their review velocity increases, I study the new title. What keywords did they add? What did they remove? That's free market research.

---

### CLOSE (7:00 - 8:00)

The tool is in the description. It's a Python file and a SQLite schema. It's minimal but it works.

If you sell anything online, knowing what your competitors are doing in near real time is worth the two hours to set this up.

---

---

## Script 4: "Building a web terminal with vanilla JavaScript (the Behike Terminal breakdown)"

**Format:** Technical tutorial / build breakdown
**Length:** ~9 min
**Hook type:** Aesthetic-first

---

### HOOK (0:00 - 0:30)

The first thing people say when they see the Behike Terminal is that it looks like something out of a movie.

It's a browser-based terminal. Dark background, green text, a blinking cursor. You type commands, it responds. But unlike a real terminal, it only knows about Behike. Products, pricing, links, contact. It's a UI that feels like a developer experience even for someone who has never opened a terminal.

Here is how I built it from scratch.

---

### SECTION 1: Why a terminal UI (0:30 - 2:00)

Most store UIs look the same. Card grid, price, add to cart, checkout. That's fine. It works. But it doesn't create a memory.

The target audience for Behike is builders. People who build things. A terminal interface is their native language. When they land on a page that looks like a terminal, they feel something. Recognition. Curiosity. They want to interact.

That's the goal. Not to impress. To create a reason to stay and explore.

The terminal is not the main store. It's an entry point. After you type `products` and browse the list, there's a link to the full store. The terminal is a filter. It self-selects for the exact people I want as customers.

---

### SECTION 2: The core architecture (2:00 - 5:00)

The whole thing is one HTML file. Inline CSS, inline JavaScript. No frameworks.

The structure has four parts.

The display area. A div with overflow-y scroll and a monospace font. Lines get appended to this div as the conversation progresses. The terminal never clears. It scrolls.

The input line. A text input at the bottom of the screen, styled to look like a terminal prompt. It shows the current directory path, a `$` character, and the user's input as they type.

The command registry. A JavaScript object where keys are command names and values are functions. When the user submits a command, the input gets looked up in this object. If found, the function runs and the output gets appended to the display area.

The autocomplete. When the user presses Tab, the input checks the command registry for a prefix match and fills in the closest command. It's one of those small things that makes the interface feel real.

---

### SECTION 3: The interesting parts (5:00 - 7:30)

The typing animation. Instead of appending the full output string at once, I append it one character at a time using `setInterval`. The interval is eight milliseconds. It creates a typewriter effect. It slows the eye down and makes the response feel deliberate, not instant.

The color system. Different types of output have different colors. Commands the user types are white. System responses are green. Errors are red. Links are cyan and underlined. All of this is applied by wrapping output in span elements with specific classes. The CSS is ten lines.

The command history. Pressing the up arrow cycles through previous commands. This is standard terminal behavior. I implemented it with a simple array that stores the last twenty inputs. The up and down arrow keys move an index through the array.

The `help` command. It dynamically reads the command registry and prints all available commands with descriptions. This means I never have to update the help text manually. When I add a command, the description shows up in `help` automatically.

---

### SECTION 4: What I'd build next (7:30 - 8:30)

One thing I want to add: a `buy` command that opens the Gumroad checkout page in a new tab. Right now, the terminal gives you a link. Clicking it works but it's not the same as typing `buy solopreneur-os` and having it open directly.

That requires matching product names to their Gumroad URLs. A small lookup table. Maybe twenty products. It's the next weekend project.

---

### CLOSE (8:30 - 9:00)

The full file is in the description. It's around 400 lines total.

If you want to understand how a clean UI gets built without a single dependency, this is a good study.

---

---

## Script 5: "La Ceiba Guild: how to build a Telegram community from zero"

**Format:** Strategy / build breakdown
**Length:** ~9 min
**Hook type:** Community-first insight

---

### HOOK (0:00 - 0:30)

Most Telegram communities die in the first thirty days. Someone creates a group, invites everyone they know, posts for a week, stops, and the group goes silent.

The ones that survive share one thing: a clear reason for existing. Not "we're all interested in AI" but a specific, repeatable activity that brings people back.

This is how I designed La Ceiba Guild from the beginning.

---

### SECTION 1: Design before launch (0:30 - 2:30)

Before I invited a single person, I answered three questions.

What happens in this group that doesn't happen anywhere else? For La Ceiba Guild, it's two things: weekly product research drops from the Overnight Machine, and accountability threads where members share what they're working on. Both are actions, not just information.

Who is this not for? If the answer to that question is "everyone is welcome," the community will be unfocused. La Ceiba Guild is not for people who want to browse. It's for people actively building. That's the filter.

What is the minimum viable activity? If I disappeared for two weeks, what would keep the community alive? I designed two recurring posts that could run automatically: a Monday brief (automated) and a Friday wins thread (prompt from a scheduled bot message). Even without me, the group has a rhythm.

---

### SECTION 2: The technical setup (2:30 - 5:00)

Telegram group with topics enabled. Topics let you separate channels within one group. The structure I use: announcements, product research, accountability, resources, and off-topic.

The bot. BehiqueBot runs inside the group. It handles three tasks: welcoming new members with a message that explains the group rules and format, posting the Monday brief automatically, and archiving all resource links shared in the group to a running document.

The welcome message is important. Most groups skip it. The welcome message tells new members what to expect, what the norms are, and what the first step is. For La Ceiba Guild, the first step is introducing yourself in the accountability channel with one sentence: what you're building. That prompt breaks the silence immediately.

For the automated posts, I use python-telegram-bot with APScheduler. A job runs at 9 AM Monday and posts the weekly brief. Another job runs Friday at 5 PM and posts a single question: "What did you ship this week?"

---

### SECTION 3: Growing from zero (5:00 - 7:30)

The first thirty members came from Instagram. I posted three times about what the guild was for, not what it was. I said: "If you're building a digital product business and want weekly product research and real accountability, reply and I'll send you the link."

I got forty-two DM replies. Invited thirty-one. Ten were active in the first week.

From there, growth was word of mouth and content. When members shipped something, I asked if I could share it in the weekly brief. Most said yes. Those posts brought in new members who saw the results and wanted in.

The number that matters is active members, not total. A group of forty people where twenty are regularly posting is healthier than a group of four hundred where eight people talk.

---

### SECTION 4: What to avoid (7:30 - 8:30)

Posting without a prompt. The empty group syndrome. You post something, nobody responds, you feel like it's failing. The fix is that almost every post should be a question or a task, not just information. Information gets ignored. Questions create responses.

Allowing off-topic too early. Off-topic topics are fine eventually but they dilute focus in the first three months. If every conversation drifts to memes, the signal-to-noise ratio drops and the serious builders leave.

Making yourself the center. The goal is for members to have conversations with each other, not just with you. Your job is to facilitate. When two members are helping each other in the thread, that's the system working.

---

### CLOSE (8:30 - 9:00)

La Ceiba Guild is currently invite-only. If you want in, there is a link in the description.

If you want the bot code for the automated posts, that's in there too.

---

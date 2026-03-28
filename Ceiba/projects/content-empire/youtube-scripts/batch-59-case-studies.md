---
title: "YouTube Batch 59 -- Case Studies"
type: youtube-scripts
batch: 59
theme: case-studies
created: 2026-03-22
status: draft
scripts: 5
estimated_length: "8-12 min each"
---

# YouTube Batch 59 -- Case Studies

---

## Script 1: How I Built the Focus DJ App in One Session (Live Build Analysis)

**Hook (first 15 seconds):**

> Four hours. One session. A working web app that plays binaural beats matched to your focus state.
>
> I'm going to break down exactly how that session went. What I planned, what I had to improvise, what broke, and what the build process looks like when you're working fast with AI as a collaborator.

---

**[SECTION 1: The Problem I Was Solving]**

I have ADHD. Deep focus is possible but it requires the right environment. Binaural beats work for me. The problem: every app with binaural beats is either behind a subscription, bloated with features I don't want, or doesn't let me control the frequency precisely.

The specific thing I needed: a browser tab that plays a carrier tone plus a binaural offset, lets me pick the frequency range (delta, theta, alpha, beta), and runs without an internet connection after the first load.

That's a specific need. The apps on the market were built for the broadest possible user. None of them did exactly this.

---

**[SECTION 2: The Plan Before Opening the Editor]**

Ten minutes of planning before touching code. I've learned this the hard way. Jumping straight into building without a plan creates three hours of wandering.

My notes from before the session:

```
- HTML/CSS/JS only. No framework. It needs to run in a browser tab, period.
- Web Audio API for tone generation. No external audio files.
- Two oscillators: carrier + (carrier + offset). Binaural only works in headphones.
- UI: frequency selector, volume slider, start/stop. Nothing else.
- No data storage. No user accounts. Stateless.
- Target: working in under a session.
```

The constraint "working in under a session" is intentional. It forces scope discipline. Every feature I wanted to add had to pass the question: does this block the core functionality? If no, cut it.

---

**[SECTION 3: The Build -- What Actually Happened]**

Hour 1: Web Audio API research and core oscillator setup.

The Web Audio API is powerful and its documentation is adequate. I built the two-oscillator setup in about 45 minutes. The tricky part: the binaural effect requires sending different frequencies to left and right audio channels separately. That requires channel splitter/merger nodes in the audio graph.

The moment it worked -- two slightly different tones, one in each ear, a clear beat frequency in the middle of my head -- was genuinely satisfying.

Hour 2: UI and frequency mapping.

Built the interface in vanilla HTML and CSS. The frequency presets (delta: 0.5-4Hz, theta: 4-8Hz, alpha: 8-14Hz, beta: 14-30Hz) map to actual neuroscience ranges. Each preset has a specific default offset within that range.

The visual design: dark, minimal, no chrome. Just the controls you need and an indicator showing the current state.

Hour 3: Problems.

The Safari bug. Web Audio API behaves differently in Safari. The oscillators started fine but the gain node wasn't updating in real time. Thirty minutes debugging. The fix was wrapping the gain change in `audioContext.currentTime` scheduling instead of direct assignment.

Hour 4: Polish and the addition I didn't plan.

One addition that didn't make the plan but should have: a timer. Being able to set a 25-minute focus session with a soft audio cue at the end is more useful than I expected. Added it at hour 3.5. It required about 20 minutes of work. Worth it.

---

**[SECTION 4: The Role Claude Played]**

I want to be specific about this because I see a lot of vague claims about "building with AI."

What Claude did: wrote the initial Web Audio API boilerplate when I described what I needed. Caught the Safari bug when I pasted the problematic code and described the symptom. Suggested the channel merger approach for stereo separation.

What I did: made the architectural decisions. Decided what features to include and cut. Debugged the gain node issue by reading the spec (Claude's suggestion was close but wrong on the first try). Designed the UI by hand.

The session probably would have taken seven hours without Claude. It took four. The saving was primarily in boilerplate and documentation lookup. The design decisions were still mine.

---

**[SECTION 5: What I'd Do Differently]**

Two things.

First: test in multiple browsers at hour 1, not hour 3. The Safari issue would have been caught and fixed earlier with less cognitive load from the rebuild.

Second: the timer feature should have been in the initial plan. It's core to the use case. I excluded it because I was being aggressive about scope. In hindsight, a 25-minute focus timer is not a nice-to-have. It's the thing that makes it usable.

The lesson: scope discipline is good. But there's a version of scope discipline that cuts things that are actually core to the value. I cut the timer because it felt like scope creep. It wasn't.

---

**[CLOSING]**

The Focus DJ is live at [link]. Free. No account. Runs in a browser tab. The source code is on GitHub. If you want to build your own version with different frequencies, fork it and change the preset values. The code is straightforward.

The takeaway from the build: constraints produce speed. The rule "HTML/JS only, runs in a tab" cut every decision about frameworks and infrastructure. The rule "one session" cut every feature debate. Working within constraints is not a limitation. It's a method.

---

## Script 2: Ceiba Sanctuary: What It Took to Build a Complete Wellness Environment in HTML

**Hook (first 15 seconds):**

> A wellness app, entirely in one HTML file, running offline, with a soundscape system, a breathing guide, and a focus timer. No framework. No server. No subscription.
>
> Here's how it got built and what the process revealed about HTML as a medium.

---

**[SECTION 1: Why HTML]**

The honest answer: I was tired of over-engineered solutions.

I've built apps in React. I've deployed to servers. I've managed dependencies. For a personal tool that runs in a browser tab and doesn't store user data, that entire stack is overhead I don't need.

HTML, CSS, and vanilla JS run everywhere. They don't break when Node.js updates. They don't need a build step. A single file can be opened on any device with a browser.

For wellness tools specifically, this matters. You want the thing to work at 2am when your focus is poor and you need it most. A complex deployment is a fragile one.

---

**[SECTION 2: The Feature Inventory]**

Before building: write the complete feature list, then cut it in half.

Initial list I wrote:
- Ambient soundscape (multiple environments)
- Breathing guide (box, 4-7-8, basic)
- Binaural tones
- Pomodoro timer with session count
- Affirmation display
- Color theme system
- Fullscreen mode

Final list after cutting:
- Ambient soundscape (3 environments: rain, white noise, forest)
- Breathing guide (box and 4-7-8)
- Pomodoro timer
- Minimal dark theme, one option

The cuts: binaural tones (already in Focus DJ), affirmations (felt like clutter), color theme system (scope creep). Fullscreen mode I kept because it changes the experience of the whole app.

---

**[SECTION 3: The Web Audio Architecture]**

All sound runs through the Web Audio API. No audio files. No network requests after first load.

The ambient soundscapes use noise generation. White noise: a buffer of random values run through a gain node. Brown noise (more relaxing than white for focus): the same buffer with a low-pass filter applied, cutoff around 1000Hz.

Rain sound: this one is more complex. Layered filters on a pink noise source plus occasional burst envelopes to simulate individual drops. It took about two hours to get this to sound right. The test: close your eyes and see if it reads as rain. It does.

The breathing guide uses a slow LFO (low-frequency oscillator) to drive a subtle tone that rises and falls with the breathing cycle. This gives the breathing pattern an audio anchor in addition to the visual circle animation.

---

**[SECTION 4: The CSS Animation System]**

The breathing circle is pure CSS animation. The circle expands and contracts on a timing cycle that matches the selected breathing pattern.

Box breathing: 4s in, 4s hold, 4s out, 4s hold. Total cycle: 16s. CSS keyframes with four stops.

4-7-8: 4s in, 7s hold, 8s out. Total cycle: 19s. Requires a different keyframe set.

The challenge: CSS animations don't natively support dynamic timing. The breathing pattern selector swaps out the animation class on the circle element. Each class has its own keyframe definition. Simple, but it works.

The visual: a circle that breathes. On inhale it's cool blue. On hold it's neutral. On exhale it shifts toward a warmer tone. Subtle. Just enough to track without being distracting.

---

**[SECTION 5: What the Process Revealed About HTML as a Medium]**

Three things I didn't expect.

First: HTML files are surprisingly expressive. When everything is in one file, you develop a clarity about what the app actually is. There's nowhere to hide complexity. If it's complicated to read, it's complicated, full stop.

Second: the constraints produced better decisions. I can't abstract too far. I can't over-engineer the state management. Everything is either a variable, a DOM element, or an audio node. That clarity is good.

Third: single-file apps are genuinely portable. I opened Ceiba Sanctuary on my phone by putting the file in my iCloud Drive and opening it in Safari. It worked. No build step. No deployment. The file is the app.

---

**[SECTION 6: Limits of the Approach]**

Three things HTML single-files cannot do well:

Data persistence across sessions. You can use localStorage, which I do for the timer history. But anything complex requires a real database and a server.

Collaboration. Single-file apps are personal tools. They can't sync state between devices without a server in between.

Large-scale UI complexity. When the UI has dozens of views and complex state, the single-file approach becomes unmanageable. The boundary is around 2000-3000 lines of code. After that, a framework earns its overhead.

Ceiba Sanctuary is 1,400 lines. Still in the zone.

---

**[CLOSING]**

The file is in the description. Download it, open it in a browser, use it.

The thing I'm proudest of: I've used it every day for three weeks. The test of any tool I build is whether I reach for it. This one I do.

---

## Script 3: The Study Buddy App: Solving My Own ADHD Studying Problem

**Hook (first 15 seconds):**

> I was failing to study. Not because I wasn't trying. Because every study method I tried was designed for a neurotypical attention span and I don't have one.
>
> So I built something for my actual brain. Here's what it does and how I built it.

---

**[SECTION 1: The Actual Problem]**

ADHD doesn't mean I can't focus. It means focus is harder to initiate and harder to sustain without the right conditions. The conditions are:

- Clear time boundaries. Unbounded study time is the fastest path to not studying.
- Visible progress. Without feedback that something is happening, motivation collapses.
- Low friction to start. A complicated study setup guarantees I'll do something else.
- External accountability. When it's just me and a textbook, avoidance wins.

No existing study app addressed all four of these. Pomodoro timers handle time boundaries. Anki handles progress. But they're separate tools with separate setups. The friction of coordinating them is enough to break the habit.

Study Buddy is one tool that handles all four.

---

**[SECTION 2: The Feature Design]**

I wrote the requirements as user stories, which forced me to think about behavior rather than features.

"As someone with ADHD, I want to start a study session in under 10 seconds so the startup friction doesn't give me time to avoid it."

That story produced: the app opens in a ready state. No configuration required. You click Start and the timer runs.

"I want to see exactly how much time is left so I can tell myself 'just four more minutes.'"

That story produced: the timer counts down from the session length, not up. Counting up shows you how long you've been sitting. Counting down shows you how little time is left. That framing is more motivating for ADHD brains.

"I want the session to feel contained so I know I'm allowed to stop at the end."

That story produced: an explicit "session complete" state. Not just the timer hitting zero. A clear visual and audio signal that the session is done and stopping is correct behavior.

---

**[SECTION 3: The Technical Build]**

Single HTML file. The entire app is around 900 lines.

Core components:

**Session manager** -- handles start, pause, resume, end. State machine with five states: idle, running, paused, break, complete.

**Focus sound** -- low-volume ambient brown noise that runs during sessions. Can be turned off. I keep it on. It signals to my brain that the session is active.

**Progress tracking** -- localStorage stores session history. Total sessions this week, total time, streak count. These three numbers are visible on the main screen.

**Subject log** -- before starting, you type the subject. One line. This creates a micro-commitment. "I am now studying algorithms." Saying it makes it real.

---

**[SECTION 4: The ADHD-Specific Design Decisions]**

Five design decisions that specifically address ADHD patterns.

**Session lengths: 15, 25, 40 minutes.** No custom entry. Custom entry requires a decision. Making decisions before studying costs mental energy I need for the studying.

**Visual timer: ring, not text.** A circle that depletes as time passes. Peripheral awareness without requiring you to read the numbers. You can study while seeing the session progress in your peripheral field.

**Break enforcement.** After a session, the Start button is grayed out for two minutes. Forced break. This prevents the "one more session" trap that leads to burnout.

**No notifications.** The app doesn't send any notifications. This was a deliberate decision. Notifications pull attention. When I'm studying, my phone is face down and the app is running silently on my laptop. The audio cue at session end is enough.

**Session notes.** At the end of each session, a one-line text input appears: "What did you cover?" Optional. But if you fill it in, it builds a study log over time. Looking at a month of study logs is genuinely motivating.

---

**[SECTION 5: What Changed After I Started Using It]**

Before: average study sessions of maybe 18 minutes. Consistent restarts when focus broke. No log of what was covered.

After three weeks of Study Buddy: average session length 28 minutes. Clear log of what was covered. The streak counter matters more than I expected. Missing a day doesn't feel good. That's the design working.

This is an n=1. My ADHD is not your ADHD. But the design principles are grounded in how ADHD actually presents, not how people imagine it does.

---

**[CLOSING]**

The app is in the description. The code is commented. If you have ADHD and want to adapt it for your specific patterns, the session lengths and break enforcement are the first things to adjust.

If it helps: let me know. I want to know what works and what doesn't.

---

## Script 4: Building Lumina: A Circadian Wellness Tool That Runs in a Browser Tab

**Hook (first 15 seconds):**

> Light controls your circadian rhythm. Most people interact with light completely unconsciously. Lumina is a tool that makes the right light visible at the right time of day, running as a browser tab.
>
> Here's how I built it and what I learned about circadian science while doing it.

---

**[SECTION 1: The Concept -- Light as a Wellness Input]**

Circadian rhythm is not just about sleep. It controls cortisol production, body temperature, alertness, mood regulation, and immune function. The primary input that sets your circadian clock is light, specifically blue-spectrum light.

The research is consistent: bright, blue-shifted light in the morning accelerates cortisol rise and sets a strong circadian anchor. Warm, amber-shifted light in the evening slows cortisol, reduces core body temperature, and prepares the nervous system for sleep.

Most people know this in a vague way. "I shouldn't look at screens before bed." That knowledge doesn't change behavior because there's nothing making it concrete.

Lumina makes it concrete. It's a browser tab that adjusts its light output and coaching guidance throughout the day based on your location's sunrise and sunset times.

---

**[SECTION 2: The Science Behind the Tool]**

Three mechanisms at play:

**Blue light suppression.** In the 2-3 hours before sleep, blue light (wavelengths around 480nm) suppresses melatonin production. Lumina displays a warm amber gradient in this window and shows a countdown to sleep-readiness time.

**Morning activation.** In the first hour after calculated wake time, Lumina displays high-contrast, cool-toned light and shows a breathing exercise designed for cortisol activation (4 counts in, 4 out, higher pace than relaxation breathing).

**Midday transition.** Around solar noon, the tool shows neutral white and marks it as peak cognitive performance time.

I built these based on Andrew Huberman's circadian work and the original research he cites, primarily from the Czeisler lab at Harvard. The tool is not medical advice. It's a structured way to apply what the research suggests.

---

**[SECTION 3: Geolocation and Time Calculation]**

This was the technically interesting part of the build.

The browser Geolocation API gives me latitude and longitude. From that, I calculate sunrise and sunset times using the NOAA solar calculator algorithm. This is standard enough that there are clean JavaScript implementations.

The key variables:
- `sunriseTime` -- local sunrise in minutes since midnight
- `sunsetTime` -- local sunset in minutes since midnight
- `currentTime` -- current time in minutes since midnight

From these I derive the five phase thresholds:
- Morning window: sunrise to sunrise + 60 minutes
- Full day: sunrise + 60 to sunset - 120 minutes
- Evening wind-down: sunset - 120 to sunset
- Night: sunset to midnight
- Pre-sunrise: midnight to sunrise

Each phase has its own color temperature, brightness level, and coaching guidance.

---

**[SECTION 4: The Visual Design]**

The interface is a full-viewport gradient that shifts throughout the day. Morning is a blue-shifted sky tone. Midday is neutral near-white. Evening transitions through amber to deep red. Night is near-black with a dim amber.

The gradient is not decorative. It's functional. It's the light your screen is emitting for that part of the day.

In the center: a large clock showing current time, a phase indicator ("Evening Wind-Down"), and a countdown to the next phase transition.

Below that: one coaching card. One instruction. "Put your screens away in 47 minutes." Or "Now is your peak cognitive window. Start the hardest task." Context-appropriate, not generic.

---

**[SECTION 5: The Challenge -- Making It Actually Useful]**

Building the tool took a few days. Making it useful took longer.

The first version was technically correct and completely ignored. I had it open in a tab and never looked at it because it didn't demand attention.

The fix: audio cues at phase transitions. When you move from Day to Evening Wind-Down, a soft chime plays. Just a half-second tone. Enough to notice without being disruptive.

Second fix: a persistent browser notification at the start of the night phase that says "Close screens in 30 minutes." You have to grant notification permission once. After that it runs silently.

Third fix: the coaching card changes language depending on whether you've been following the guidance. It reads your screen brightness setting (where permission allows) and notes whether you've adjusted it toward the recommendation.

That third fix made the biggest difference. The tool went from ambient information to mild accountability.

---

**[CLOSING]**

Lumina is in the description. It asks for geolocation permission once, then everything is calculated locally. No data sent anywhere.

The biggest thing I learned: information alone doesn't change behavior. The chime at phase transitions changed my behavior. The coaching card changed my behavior. The gradient alone didn't.

If you build wellness tools, build in accountability mechanisms from the start. Don't add them after you realize the information alone isn't working.

---

## Script 5: The Behike Terminal: How I Built a Natural Language Interface

**Hook (first 15 seconds):**

> A terminal interface that understands plain language. You type "what did I work on yesterday" and it reads your project logs and answers. You type "start a 25-minute work session" and the timer runs.
>
> Here's how the Behike Terminal works and what the build looked like.

---

**[SECTION 1: The Problem With Normal Terminals]**

The terminal is the most capable tool on any computer. It's also the most hostile to anyone who doesn't have commands memorized.

I know bash well enough to work efficiently. But there are three kinds of situations where even fluent terminal users slow down: complex command construction (what flag was it again), context lookup (what did I do on this project last week), and multi-step sequences (I want to do A, then B, then C if A succeeded).

The Behike Terminal is an interface that sits between you and bash and handles those three cases through natural language.

---

**[SECTION 2: Architecture -- What the Tool Actually Is]**

Three components:

**Parser layer.** A Python module that takes natural language input and classifies it into one of several command categories: query, action, sequence, and direct bash passthrough. If the input is classified as direct bash, it runs unchanged.

**Context engine.** A read layer that has access to key files: `primer.md`, `project_memory.md`, the git log, and the bridge task queue. When the parser classifies input as a query, the context engine retrieves the relevant information.

**Action handlers.** Specific handlers for common actions: start/stop timer, create project notes, run content scripts, push git checkpoints.

The whole thing runs as a Python CLI. You launch it with `behike` from any directory.

---

**[SECTION 3: The Parser -- How Natural Language Becomes Intent]**

I want to be precise about what "natural language" means here. This is not GPT-4 parsing arbitrary sentences. This is a pattern-matching system with an LLM fallback.

First pass: regex and keyword matching. "what did I work on" triggers the git log + primer.md query. "start session" triggers the timer handler. "commit" with anything after it triggers the git checkpoint handler.

Second pass (LLM fallback): if first pass doesn't match, the input goes to a local Llama model (Ollama) with a short system prompt explaining the available actions. The model classifies the input and returns a structured JSON with the action and parameters. The Python code executes the action.

This two-pass approach keeps 80% of commands fast (regex, no LLM latency) while handling the long tail.

---

**[SECTION 4: The Query System]**

This is what makes the tool feel different from a regular terminal.

"What did I work on yesterday?"

The query goes to `project_memory.md`, filters for entries from the previous calendar day, and returns a summary. Five lines or less.

"What's on the bridge queue?"

Reads `bridge/tasks.md`, returns the open tasks.

"What were the last five commits on BehiqueBot?"

Runs `git log --oneline -5` from the BehiqueBot directory and formats the output for readability.

"What's the status of all active projects?"

Reads the README files from each active project folder, extracts the status field from the YAML frontmatter, and returns a table.

None of these are magic. They're structured file reads. The natural language interface is a thin wrapper that makes them accessible without memorizing paths and command syntax.

---

**[SECTION 5: What It Can't Do]**

Three honest limitations.

It's slow when it hits the LLM fallback. Local Llama at 2B parameters is fast, but it's 500-800ms. For commands I run constantly, that latency adds up. The fix I'm working on: pre-cache common query patterns so they never hit the LLM.

It doesn't understand ambiguity well. "What's the latest?" without context is ambiguous. The parser asks for clarification, but the clarification request is formatted as a terminal prompt and people sometimes don't realize it's asking them something.

It can't chain complex logic. "If the git push fails, send me a Telegram message" is beyond the current action handler system. This requires a proper state machine, which I haven't built yet.

---

**[SECTION 6: What It Changed About My Workflow]**

Two things happened after I started using it daily.

First: I started querying my own logs more. Before, reading project_memory.md required opening the file manually. It was a friction I often skipped. Now I check it conversationally. "What did I do on product research last week." This makes the logs actually useful instead of archival.

Second: I started building handlers for things I wanted to be able to do from anywhere. "Log idea: [text]" now writes directly to the ideas backlog in Obsidian with a timestamp. That handler took 20 minutes to build. It saves me the Obsidian open-navigate-type-save sequence every time I have a quick idea. Small. Compounding.

---

**[CLOSING]**

The Behike Terminal is in early form. The core is working. The edges are rough.

The code is on GitHub. If you want to build your own version, the parser and context engine are the things to study. The action handlers are the part you'll customize for your own workflow.

The broader point: the best tool is the one built for your specific situation. Not the most general tool. The most specific one.

---

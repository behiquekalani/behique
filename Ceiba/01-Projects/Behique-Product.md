---
type: project
status: idea
related:
  - BehiqueBot
  - Psychologist-Framework
  - Kalani
  - North-Star
tags: [project, product, revenue, core]
---

# Behique — The Product
# Captured: 2026-03-16 (voice memo)
# Status: IDEA — thesis defined, no build yet

---

## THE THESIS

Take the psychological systems and coping strategies designed for people with ADD — and build them into a product that anyone can use.

**Not marketed as "for ADD people"** — that makes non-ADD people self-select out, even though they'd benefit just as much.

---

## THE INSIGHT

Kalani didn't find out he had ADD until last year, at 37. He spent his whole life developing workarounds without knowing why he needed them. Those workarounds, systematized, ARE the product.

If he needed them without knowing he had ADD — so does everyone else.

---

## THE VISUAL METAPHOR

Like the auto-sort mods in Minecraft — you press a button and everything goes to the right place automatically. Not manual organization. Intelligent routing of your thoughts, tasks, and attention.

---

## WHAT IT IS NOT

- Not a calendar
- Not another productivity app
- Not a to-do list with a skin
- Not "for ADD people" (even though it's born from ADD)

---

## WHAT IT IS

A smart external brain that handles the cognitive overhead you've been doing manually your whole life.

- Thought goes in (text, voice, any format) → system routes it automatically
- No decision fatigue about where things belong
- Categories, priorities, and connections handled by the system
- You interact with it like a person, not like software

---

## POSITIONING

Lead with the universal benefit. Let ADD people recognize themselves in it, but don't gate it behind a diagnosis.

"Everyone's brain drops things. This catches them."

---

## WHY THIS MATTERS (connection to [[North-Star]])

This isn't a side project. This is the thing that connects:
- The psychologist's framework → systematized into product logic
- BehiqueBot → the working prototype of the capture + classify engine
- Kalani's personal experience → the authenticity that marketing can't fake
- The $100K Q3 target → this is a product people would pay for

---

## WHAT ALREADY EXISTS (from [[BehiqueBot]])

BehiqueBot is the v0 of this product:
- Voice + text input via Telegram ✅
- Auto-classification into 5 categories (CREATIVE, BUSINESS, KNOWLEDGE, PERSONAL, TECHNICAL) ✅
- Life pillar tagging (health, wealth, relationships, general) ✅
- Immutable seed + living updates per idea ✅
- Notion persistence ✅
- Ollama-first, OpenAI fallback ✅

What's missing to make it a product:
- The "auto-sort" feeling — user shouldn't even see the classification, just trust it
- Retrieval — "what did I say about X last week?" (memory query layer)
- Cross-idea connections — "this idea connects to that one" (graph, not list)
- Multi-platform — not just Telegram (Discord, web app, mobile app eventually)
- The accountability layer — not just capture, but follow-through tracking
- Onboarding that doesn't mention ADD

---

## BEHAVIOR MONITORING (from 2026-03-16 voice memo #2)

Not just idea capture — **activity and behavior logging throughout the day.**

What Kalani wants:
- Track what he does, when, and how he feels about it
- Timestamp everything automatically — build a map of his daily rhythms
- Prove the night creativity hypothesis with real data ("when am I most productive?")
- System should adapt to his patterns over time (surface ideas at night, surface tasks in the morning)

What already exists for this:
- BehiqueBot timestamps every message ✅
- Whisper transcribes voice → text ✅
- Notion stores classified entries ✅
- Life pillar tagging gives emotional/domain context ✅

What's missing:
- **Activity type tagging** — not just "idea" but "working on X", "took a break", "switched to Y"
- **Time-of-day analysis** — after 1 week of data, BehiqueBot can answer "when do I have the most ideas?"
- **Pattern reports** — weekly summary of behavioral data (not a fancy alarm clock — real insights from real data)
- **Adaptive responses** — if it's 11pm and Kalani sends a voice memo, BehiqueBot knows this is peak creative time and responds accordingly

### The Immediate Friction (solve first)
Kalani is on his iPhone, talking to Claude mobile, copying transcripts manually to his computer. BehiqueBot on Telegram already has the voice → Whisper → classify pipeline. He should be sending voice memos to BehiqueBot, not to Claude mobile. The pipeline exists — it just needs to be the default input.

---

## PERSONALITY FILTERS — Book-Trained Thinking Frameworks (2026-03-16)

Core idea: books that changed how Kalani thinks become **toggleable filters** in Behique. Not chatbot personas — thinking frameworks that shape how the system responds, prioritizes, and challenges the user.

### How it works:
- User selects a filter (or the system suggests one based on context)
- Every response from Behique runs through that framework's lens
- The filter affects prioritization, questioning style, and what gets surfaced

### First filters:
| Filter | Source | What It Does |
|--------|--------|-------------|
| **Psychologist** | Kalani's real psychologist framework | Default — accountability, ADHD-aware, emotional check-ins |
| **The ONE Thing** | Gary Keller | Forces single-focus: "what's the ONE thing that makes everything else easier?" |
| **Hormozi** | Alex Hormozi / $100M Offers | Revenue lens: "does this make money? how fast?" |
| **Stoic** | Marcus Aurelius / Ryan Holiday | Control filter: "is this in your control? then act. if not, let go." |

### Why this is different:
- Productivity apps give you features. This gives you **frameworks.**
- Users aren't just organizing tasks — they're choosing how to THINK about them
- Each filter is trained on real book content, not a summary — the system actually applies the philosophy
- This is the "more than a calendar" differentiator. No other app does this.

### Technical approach:
- Each filter = a system prompt + curated knowledge base from the book
- Could use RAG (book content as embeddings) or distilled prompt engineering
- Filters can stack or be exclusive depending on the use case
- BehiqueBot already has classification logic — filters are an extension of the same routing

---

## BREADCRUMBS
- First captured: 2026-03-16 voice memo session
- No build work done yet — thesis only
- Next step: define the MVP feature set that separates this from BehiqueBot
- Connection to [[Psychologist-Framework]] is the secret weapon — real clinical logic, not productivity theater

---

*[[BehiqueBot]] [[Psychologist-Framework]] [[Kalani]] [[North-Star]] [[Q3-2026]]*

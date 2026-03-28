# AI Writing Workflows

**How to use Claude, ChatGPT, and local AI to write faster without losing your voice**

**Price:** $19.99
**By Kalani Andre — Behike**

---

## What This Is

This is a practical system for writers and content creators who want to use AI without sounding like they do.

Not a list of prompts. Not a "here are 100 AI hacks" PDF. A workflow system, built around the way real writers think and work.

If you write threads, newsletters, blog posts, YouTube scripts, or any kind of content for an audience, this guide will help you produce more of it, faster, without the uncanny valley feeling that comes from handing your voice over to a machine.

The goal is simple: you write more. You sound more like you.

---

## Section 1: The AI Writing Paradox

There is a reason AI-generated content has a smell to it.

You can feel it within a sentence or two. The cadence is too smooth. The structure is too predictable. The energy is somewhere between competent and hollow. The kind of writing that says nothing wrong and means nothing either.

The paradox is this: AI is incredibly good at writing, and that is precisely why it produces bad content.

It optimizes for coherence, completeness, and broad comprehension. Your actual readers do not want those things. They want recognition. They want the feeling that a real person who thinks like them, who has struggled with the same things, is talking directly to them. That feeling does not come from coherent and complete. It comes from specific, opinionated, and occasionally rough.

When most people use AI for writing, they treat it as a replacement. They type a vague instruction: "write me a LinkedIn post about productivity." The AI writes something technically correct. They post it. The engagement is flat. They blame AI.

The actual problem is the model they used: outsource the hard part, ship the easy part.

The hard part of writing is the thinking. The voice. The specific angle you chose because of something that happened to you, something you noticed that nobody else is saying. That part is not replaceable. The AI should handle the parts that are not specifically you. The structure. The transitions. The first draft grunt work. The reformatting for different platforms.

This guide is built on that distinction.

**What AI should do:**
- Draft from your notes and ideas
- Generate structural options
- Reformat for different platforms
- Suggest angles you have not considered
- Handle the parts that do not require your specific perspective

**What you should do:**
- Choose the angle
- Set the tone
- Define your position
- Edit until it sounds like you again
- Be the one who decides what gets published

The moment you flip those roles is the moment your content starts sounding like everyone else's.

---

## Section 2: Your Voice First

Before you touch a single prompt, you need to know what your voice actually is. Most writers cannot articulate this. They know it when they read it. They know when something sounds off. But they cannot describe it precisely enough to feed it to an AI.

That imprecision is why AI output sounds generic. The model cannot read your mind. You have to give it the raw material.

**The Voice Extraction Exercise**

Pull five pieces of writing you have produced that you are proud of. These should be real ones: threads that hit, newsletters you re-read yourself, blog posts that felt honest. Do not pick the ones with the most engagement. Pick the ones that felt most like you.

Now answer these questions about them:

1. What sentence length is most common? Do you write in bursts or long build-ups?
2. Do you open with a question, a statement, or a scene?
3. How often do you use the word "I"? Is it frequent or sparse?
4. What topics do you return to obsessively? What lens do you apply to everything?
5. What words or phrases appear repeatedly? What do you never say?
6. How do you handle disagreement? Blunt or layered?
7. Do you use humor? What kind?
8. What is your default structure? Problem then solution? Observation then implication?

Write answers to all eight. Then condense those answers into a paragraph that describes your writing style to someone who has never read you.

That paragraph is your Voice Brief. It goes into every prompt.

**Example Voice Brief:**

"I write in short, declarative sentences. I tend to open with a provocative statement rather than a question. I use 'I' sparingly. I write about systems, solopreneurship, and the gap between theory and execution. I never say 'leverage,' 'unlock,' or 'game-changer.' My tone is direct but not aggressive. I use specific numbers and time estimates. I end pieces with a clear call to action or a reframe."

That brief takes fifteen minutes to write. It will save you hours of editing every week.

**Save this as `voice-brief.txt` in your prompts folder. Every AI session starts with it.**

---

## Section 3: The Workflow Map

This is the full production cycle. Each stage has a specific AI role and a specific human role.

```
Stage 1: IDEATION
Human: choose topic, angle, target reader
AI: generate angle variations, suggest hooks

Stage 2: OUTLINE
Human: select structure, kill bad ideas
AI: draft chapter/section breakdown

Stage 3: FIRST DRAFT
Human: provide notes, key points, voice brief
AI: write the draft

Stage 4: EDIT LOOP
Human: read, mark what sounds wrong, rewrite those parts
AI: fix transitions, tighten sections on command

Stage 5: PLATFORM ADAPTATION
Human: choose which platforms
AI: reformat for each one

Stage 6: PUBLISH
Human: final read, publish
AI: generate metadata, descriptions, tags
```

The mistake most people make is skipping stage 1 and 2 entirely. They go straight to "write me a blog post about X." The AI has no angle to work with. It invents one. The invented angle is always generic because the AI is averaging across everything it has seen about topic X.

You need to have an opinion first. Then you give AI the structure problem.

**Time estimates by content type:**

| Format | Human time | AI time | Total |
|--------|-----------|---------|-------|
| Twitter thread (7-10 tweets) | 15 min | 5 min | 20 min |
| Newsletter (600-1000 words) | 30 min | 15 min | 45 min |
| Blog post (1500-2500 words) | 60 min | 30 min | 90 min |
| YouTube script (8-12 min) | 45 min | 20 min | 65 min |
| TikTok/Reel script (60-90s) | 10 min | 5 min | 15 min |
| LinkedIn post | 15 min | 5 min | 20 min |

Human time here means: thinking, choosing angle, editing, final read. Not staring at a blank page.

---

## Section 4: Claude vs. ChatGPT vs. Local AI

Honest comparison. No affiliation with any of these.

### Claude (Anthropic)

**Best for:** Long-form writing, editing, following nuanced instructions, maintaining voice across a document.

Claude is better at following a detailed voice brief and sticking to it across a long piece. If you give it ten constraints, it will generally respect all ten. It reads as more thoughtful and less salesy in its default output.

**Use Claude when:** You are writing a newsletter, long-form essay, detailed tutorial, or any piece where your voice needs to carry across 1,000+ words.

**Weakness:** Sometimes overly careful. Will hedge when you want a bold statement. You often have to push it.

**Prompt:** "Do not hedge. State this directly, even if it sounds blunt."

### ChatGPT (OpenAI)

**Best for:** Ideation, angles, first-draft hooks, rapid variation generation, structured output.

ChatGPT generates a lot of options fast. If you need five different hooks for a post, or six different angles on a topic, it is faster to run ChatGPT for that and then pick. It is also better with structured data formats if you need specific JSON or table outputs.

**Use ChatGPT when:** You are in ideation mode. You need options, not a finished draft. You want five versions of an opening sentence.

**Weakness:** The default output has a consistent salesy energy. It loves phrases like "in today's fast-paced world" and "it's more important than ever." You have to train it out of this each session.

**Prompt:** "Do not use filler phrases. Do not write marketing-speak. Be direct."

### Local AI (Ollama, LM Studio, etc.)

**Best for:** Privacy-sensitive work, repetitive tasks, running without API costs, experimentation.

Local models running on consumer hardware (Llama 3, Mistral, Gemma) are capable but slower and less consistent than the frontier models. They are useful for: preprocessing raw notes, summarizing long documents, generating rough outlines, running batch reformatting jobs.

**Use local AI when:** You are reformatting content you have already written, summarizing research, preprocessing transcripts, or you want to iterate on prompts without running up API costs.

**Weakness:** The output needs more editing. The voice is less controllable. You will spend more time in the edit loop.

**Hardware baseline:** Any Apple Silicon Mac (M1 or newer) can run Ollama with Llama 3.2 3B or 8B competently. The 70B models need a Mac with 64GB+ RAM.

### Decision Matrix

| Task | Use |
|------|-----|
| Long-form draft | Claude |
| Hook variations | ChatGPT |
| Editing a draft | Claude |
| Generating 10 subject lines | ChatGPT |
| Reformatting content | Local or either |
| Privacy-sensitive writing | Local |
| Batch processing | Local |
| Final polish | Claude |

---

## Section 5: Prompt Engineering for Writers

The principle: prompts are instructions, not wishes. Be specific. Give context. Show, do not tell.

Every prompt you use for writing should include:
1. Your role (who is writing this)
2. The reader (who is reading this)
3. The format (thread, newsletter, blog, etc.)
4. The voice brief (paste it in)
5. The specific ask

**Template: Thread Prompt**

```
You are writing as [your name/persona], a [brief description] who writes about [topics].

Voice brief: [paste your voice brief]

Audience: [who reads your content, what they want]

Task: Write a Twitter/X thread about [topic].

Angle: [your specific take, the thing you believe that most people don't say]

Format:
- 8-10 tweets
- First tweet is the hook (bold claim or provocative statement, no questions)
- Each tweet stands alone but builds toward the conclusion
- Final tweet is a clear, direct call to action
- No hashtags
- No emojis
- Short sentences

Key points to include:
- [point 1]
- [point 2]
- [point 3]

Do not include:
- Hype language
- Generic advice
- Phrases like "game-changer" or "unlock"
```

**Template: Newsletter Prompt**

```
You are writing as [your name/persona].

Voice brief: [paste your voice brief]

Newsletter: [name of newsletter, brief description, what readers expect]

Issue topic: [specific topic]

Angle: [your take on it]

Structure:
- Opening hook (1-2 sentences, strong statement or specific observation)
- Context (why this matters, 2-3 paragraphs)
- The main insight (your actual point, the thing you want them to leave with)
- Practical section (steps, examples, or a framework they can use)
- Closing (2-3 sentences, not a summary, forward-looking or a question)

Target length: [600-1000 words]

Tone: [describe your tone, reference your voice brief]

Include these specific points:
- [point 1]
- [point 2]

Do not include:
- A summary at the end
- Lists of "top X tips"
- Generic closes like "I hope this was helpful"
```

**Template: Blog Post Prompt**

```
You are writing as [your name/persona].

Voice brief: [paste your voice brief]

Blog post topic: [topic]

Target reader: [describe them specifically — not "entrepreneurs," but "solo founders who are one year into their first business and feel stuck"]

Angle: [your specific argument or position]

Intended outcome: What should the reader think, feel, or do after reading?

Structure:
- Title
- Opening (no generic scene-setting, start with the real thing)
- Problem section (make them feel understood, not lectured)
- Insight section (your actual point)
- Evidence or examples (specific, not generic)
- Practical framework or steps
- Conclusion (not a summary, a reframe or forward look)

Target length: [1500-2500 words]

Include these specific examples or data points:
- [your specific examples, stats, stories]

SEO keyword to include naturally (not to stuff): [keyword]
```

**Template: YouTube Script Prompt**

```
You are writing as [your name/persona], scripting a YouTube video.

Voice brief: [paste your voice brief]

Video topic: [topic]

Target viewer: [specific description]

Angle: [your take]

Video structure:
- Hook (first 30 seconds, no intro, start with the most interesting thing)
- Problem or context (1-2 minutes)
- Main content (4-6 minutes, broken into 3-4 clear sections)
- Practical demonstration or example (1-2 minutes)
- Close (30-60 seconds, not a summary, a specific next action)

Target length: [8-12 minutes = approximately 1500-2000 words]

Delivery notes: [your style — conversational, direct, fast-paced, etc.]

Include visual cue suggestions in [brackets].

Specific points to cover:
- [point 1]
- [point 2]
```

**Template: Short-form Caption / Reel Script Prompt**

```
You are writing as [your name/persona].

Voice brief: [paste your voice brief]

Platform: [TikTok / Instagram Reels / YouTube Shorts]

Topic: [specific topic]

Angle: [your take]

Format:
- Spoken script for 45-75 seconds
- First 3 seconds must be a hook that stops the scroll
- No greeting, no intro, start with the tension or the point
- Conversational, sounds like natural speech
- Clear single takeaway
- Optional: on-screen text suggestions in [brackets]

Do not:
- Start with "Hey guys"
- Use hype language
- End with "let me know in the comments"
```

---

## Section 6: The Edit Loop

First drafts from AI are not finished. That is the assumption. The edit loop is where your content becomes yours.

**The three-pass edit:**

**Pass 1: Read for energy.** Read the entire draft without editing. Mark any sentence that feels wrong, hollow, or not like you. Do not fix anything yet. Just mark.

**Pass 2: Rewrite the marked sections.** These are the parts where the AI defaulted to something generic. Rewrite them yourself. These sections are usually: the opening, the conclusion, any place where a strong opinion was needed, and any place where the AI added unnecessary caveats.

**Pass 3: Read aloud.** Read the full draft aloud. Anything that trips you up, that you stumble over or would not actually say, rewrite it. This catches the rhythm problems that read fine on screen but land wrong when spoken.

**Prompts to use during editing:**

```
This section sounds too formal. Rewrite it in a more direct, conversational tone.
Keep all the same information.
```

```
Remove all hedging language from this paragraph. Be direct.
Do not use phrases like "it's worth noting," "it's important to remember," or "some might argue."
```

```
This is too long. Cut it by 30% without losing the main point.
Remove filler. Keep specifics.
```

```
Rewrite the opening. It starts too slow. The reader should be interested
by the end of the first sentence, not the end of the first paragraph.
```

```
The conclusion is too soft. Rewrite it to end on a strong, specific statement.
Not a summary. A forward-looking thought or a direct instruction.
```

**What to never delegate to AI in editing:**
- Deciding what your final opinion is on a topic
- Choosing which examples to include (your specific examples are what make it real)
- Writing the opening sentence (do this yourself, always)
- The final read before publishing

---

## Section 7: Speed Runs

Real-time walkthroughs for the most common content formats.

### Newsletter in 45 Minutes

**Minutes 0-10:** Open a blank document. Write notes from your brain about the topic. Your angle, your examples, what you want the reader to leave with. Do not write prose. Bullet points are fine. If you have done research or reading, add key facts. This is the thinking step. Do not skip it.

**Minutes 10-15:** Open your AI tool. Paste your newsletter prompt template. Fill in your angle, voice brief, key points from your notes. Submit. Read the draft.

**Minutes 15-25:** Edit loop. Pass 1 (mark what feels wrong). Rewrite the opening. Rewrite any hedged opinions. Rewrite the close if it is too soft.

**Minutes 25-35:** Read aloud. Fix rhythm issues. Tighten.

**Minutes 35-40:** Format for your newsletter tool. Subject line: write three options, pick the best one.

**Minutes 40-45:** Final read. Send.

### Thread in 15 Minutes

**Minutes 0-5:** Write the core idea in one sentence. What is the single claim this thread makes? Write four supporting points or examples.

**Minutes 5-10:** Paste into thread prompt. Get draft. Check: does tweet 1 hook? Does each tweet add something new? Does the last tweet have a clear action?

**Minutes 10-15:** Edit the first tweet (always), the last tweet (always), any tweet that uses generic language. Read the full thread as a reader would: does it build? Does it earn the ending?

Publish.

### Blog Post in 2 Hours

**Hour 1, 0-20 minutes:** Research and thinking. Notes, sources, your angle, your examples. Write your own outline (not AI-generated). The outline is the thinking. Do not delegate this.

**Hour 1, 20-60 minutes:** Paste outline + voice brief + key points into blog prompt. Get draft. Read entire draft. Mark problem sections.

**Hour 2, 0-40 minutes:** Rewrite the opening. Fix the marked sections. Tighten each section. Add your specific examples where the AI used generic ones. Read aloud.

**Hour 2, 40-60 minutes:** Write metadata (title, meta description, tags). Format for your platform. Final read. Publish.

---

## Section 8: Building a Prompt Library

The first time you write a good prompt, it takes twenty minutes. The tenth time you use it, it takes thirty seconds. The gap between those two numbers is why you need a prompt library.

**Structure:**

Create a folder called `prompt-library/`. Inside it, keep one file per content format.

```
prompt-library/
  thread-prompt.txt
  newsletter-prompt.txt
  blog-post-prompt.txt
  youtube-script-prompt.txt
  reel-script-prompt.txt
  linkedin-post-prompt.txt
  caption-prompt.txt
  subject-lines-prompt.txt
  voice-brief.txt
```

Each file contains the template with placeholders in [brackets]. When you sit down to write, you open the file, fill in the brackets, paste into your AI tool.

**Add to the library when:**
- You get output that sounds exactly like you on the first try (study what made that prompt work, add notes at the top)
- You find a specific instruction that solves a recurring problem ("no hedging," "cut by 30%," "rewrite the opening")
- You write for a new platform or format

**Annotate your prompts.** At the top of each prompt file, keep a short log:

```
# Thread Prompt
# Last updated: [date]
# What works: [note what consistently produces good output]
# What doesn't work: [note what you had to remove]
# Version history: [brief notes on what changed]
```

This turns your prompt library into a learning system. Every session makes it better.

**Backup rule:** Prompt library lives in your main project folder, synced wherever your other work lives. Losing your prompt library is losing weeks of calibration.

---

## Section 9: Repurposing Workflows

One piece of long-form content can produce ten platform-specific pieces without writing anything new. This is not about copy-paste. It is about reformatting for how each platform is consumed.

**The Repurposing Chain:**

```
Blog Post / Newsletter (source)
|
|-- Twitter Thread (key argument + 3-4 supporting points)
|-- LinkedIn Post (professional frame of the same idea)
|-- 3x Instagram Captions (one hook per caption, single idea each)
|-- TikTok Script (hook + single takeaway, 60 seconds)
|-- YouTube Short (same as TikTok, slightly different framing)
|-- Pinterest Pin (headline + key stat or insight)
|-- Email subject line test (3 variations)
|-- Story carousel frames (5-7 slides summarizing key points)
|-- Podcast talking points (if applicable)
```

**The Repurposing Prompt:**

```
Here is a [blog post / newsletter / essay]. I want to repurpose it
for multiple platforms. The core idea is: [state it in one sentence].

My voice brief: [paste it]

Create the following, each formatted for its specific platform:

1. Twitter thread (8 tweets, start with the strongest hook from the piece)
2. LinkedIn post (300-500 words, professional tone, single key insight)
3. Instagram caption (200-300 words, conversational, hook in first line)
4. TikTok/Reel script (60-75 seconds, spoken word, one takeaway)
5. Pinterest pin headline + description (80 characters headline, 200 characters description)

Keep the core argument consistent across all formats.
Do not just copy-paste sections. Rewrite for each platform's context.

Source content:
[paste the piece]
```

**What changes per platform:**
- Length (obvious)
- Opening format (threads hook with claims, LinkedIn hooks with relevance, TikTok hooks with pattern interrupts)
- Assumed reader context (LinkedIn readers are skimming between meetings, TikTok viewers are on a couch, newsletter readers chose to be there)
- Call to action (follow, comment, buy, click are different asks for different contexts)

**What stays the same:**
- Your core argument
- Your specific examples
- Your position
- Your tone

The AI handles the reformatting. You make sure the core stays intact.

---

## Section 10: The Long Game

Building a content moat is not about volume. It is about compression.

Every piece you publish contains your point of view. Over time, your point of view becomes something readers can identify and seek out. That is a moat. It takes years. AI compresses the time it takes to produce the volume that builds that library, but it cannot compress the underlying work of developing a perspective worth following.

What this looks like in practice:

**Year 1:** You have a point of view but not a library. You post consistently. Some things land, some do not. You learn which angles resonate. You build your prompt library.

**Year 2:** You have 200-300 pieces of content in the world. You start to see patterns. You know which topics your audience engages with. You know your best-performing formats. You double down on those.

**Year 3:** Your voice is distinct enough that readers can identify your writing without a byline. You have built something that takes real time to replicate.

AI accelerates the output side of year 1. But the thinking that makes year 3 possible is still yours to develop.

**What to track (simple version):**

Keep a spreadsheet with one row per published piece:
- Date
- Platform
- Topic
- Format
- Angle (the specific claim or take)
- Performance (views, engagement, clicks, whatever metric matters for that platform)

After 30 pieces, look at the angle column. What positions consistently get engagement? Write more of those. That data is more valuable than any prompt.

**The compounding effect:**

When you have been writing consistently for a year, you have something that most people do not have: a searchable body of opinion. Your readers know where you stand. New readers can look at 50 pieces and understand your worldview in an hour.

AI writing tools will continue to improve. The baseline quality of AI output will rise. The differentiator will not be access to the tools. It will be having built a recognizable perspective over time, a thing AI cannot fake because it requires being a real person with a real track record.

Use these workflows to build faster. But never let the speed become a reason to stop thinking. The work that compounds is the thinking, not the publishing.

---

## Appendix: Quick Reference

### Voice Brief Template
```
I write in [short/medium/long] sentences.
I open with [statements/questions/scenes].
I use "I" [frequently/sparingly].
My core topics are [list].
My tone is [describe].
I never say [list of banned words/phrases].
My default structure is [describe].
I use humor [how/when/never].
```

### Platform Character Limits (approximate)
- Twitter/X: 280 characters per tweet (threads stack)
- LinkedIn: 700 characters visible before "see more," 3,000 characters max
- Instagram: 2,200 characters, first 125 visible before cut
- TikTok: 150 characters caption, no real limit on script
- YouTube: 5,000 characters description, no script limit
- Newsletter: no limit, but 600-1,200 words is the practical range for engagement

### Prompt Checklist
Before submitting any prompt, confirm it includes:
- [ ] Who is writing (your persona/voice)
- [ ] Who is reading (specific audience)
- [ ] Voice brief (pasted in full)
- [ ] Specific angle (not just topic)
- [ ] Format requirements (structure, length, platform)
- [ ] What to avoid (your list of banned language)
- [ ] Your specific points, examples, or data to include

### The Non-Negotiable Rules
1. You choose the angle. Every time.
2. You write the opening. The AI can draft it, but you rewrite it.
3. You do the read-aloud before publishing.
4. You make the final call on what gets published.
5. Your prompt library is a living document. Update it constantly.

---

*AI Writing Workflows is a Behike product. behike.com*

*If this guide helped you, the best thing you can do is use it. Build something with it. That is the whole point.*

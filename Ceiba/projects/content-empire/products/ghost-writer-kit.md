---
title: "Ghost Writer Kit"
type: product
tags: [ghost-writing, content, voice, ai-tools, guide]
created: 2026-03-22
price: $99
---

# Ghost Writer Kit
## A System That Writes Like You. Not Like AI.

**What is in the kit:**
- This guide (the methodology)
- voice_bible_template.md (the configuration file for your writing voice)
- ghost_writer.py (the Python script that generates content using your Voice Bible)
- 5 sample Voice Bibles from different creator archetypes

---

## Introduction: The AI Voice Problem

Every AI-generated piece of content reads the same. Not because AI is bad. Because most people use it wrong.

They open ChatGPT, type "write me a LinkedIn post about productivity," and paste whatever comes out. The result sounds like every other LinkedIn post written by someone who also typed that exact prompt. Polished. Generic. Forgettable.

The problem is not the tool. The problem is that they gave the AI nothing to work with. No voice. No rules. No personality. Just a topic.

AI can copy style. Feed it three paragraphs of Hemingway and it will write like Hemingway. But your voice is not style. Your voice is the specific combination of things you say, how you say them, what you refuse to say, what you always come back to, and how you think on the page. That is harder to transfer. It requires a system.

That is what this kit builds. Not a prompt. Not a template. A system.

The Ghost Writer Kit does one thing: it gives AI enough information about how you write that the output actually sounds like you. Not a version of you filtered through corporate language. Not a polished stranger. You.

It is built around a document called the Voice Bible, and a Python script that uses that document to generate content. You fill in the Voice Bible once. You run the script whenever you need content. The output is yours to edit and publish.

This is not for people who want AI to replace their thinking. It is for people who already have ideas and need help getting them out consistently without spending three hours per post.

Who this is for: content creators, solopreneurs, and business owners who produce content regularly and have existing writing to reference. You need a backlog of your own work to make this kit work. If you have never written anything, start there first.

Who this is not for: people looking for a one-click content machine. You still have to edit. You still have to think. This kit just removes the blank page problem.

---

## Chapter 1: Building Your Voice Bible

The Voice Bible is a structured document that defines your voice for AI. Think of it as the configuration file for your writing. Before you run any content generation, the system reads this file. Every piece of output is filtered through it.

Most people try to replicate their voice by including a few examples and hoping the AI figures it out. It does not work. AI needs explicit rules, not just samples. The Voice Bible gives it both.

There are six sections. Fill all of them.

### Section 1: Who You Are

This is not a bio. It is a brief statement of role, expertise, and personality as they show up in your writing. Be specific.

Bad example: "I am a content creator who writes about business."

Good example: "I am a 22-year-old computer engineering student building a one-person business. I write about AI tools, digital products, and building systems. My personality on the page is direct and skeptical. I do not celebrate effort, I celebrate results. I am not here to inspire anyone. I am here to give people things that actually work."

The AI uses this section to set tone and filter out language that does not fit your persona.

### Section 2: Banned Words

This is a list of words you do not use. Not because they are bad words. Because they are not your words.

Every writer has a vocabulary fingerprint. The words you avoid are as defining as the words you use. Your banned list signals to the AI what kind of writer you are not.

Sample banned list: leverage, streamline, unlock, game-changing, impactful, synergy, deep dive, transformative, comprehensive, ultimate, master, revolutionize, empower, holistic, journey.

Add words you have noticed AI defaulting to that feel wrong when you read them. Update this list every time you edit output and find yourself deleting the same word twice.

### Section 3: Sentence Structure Rules

How do you write? Short punchy sentences? Long flowing ones? Questions? Fragments? A specific rhythm?

Describe it in plain terms. You do not need to use grammatical terminology. Just describe what your writing sounds like at the sentence level.

Sample rules:
- Short sentences as the default. One idea per sentence.
- Questions used sparingly and only when the question is genuinely unanswered.
- No filler at the start of paragraphs. No "Interestingly," or "It's worth noting that."
- Transitions happen inside paragraphs, not between them with connector words.
- Paragraph length: 2 to 4 sentences for body content. Never more than 5.

### Section 4: Topics You Will Not Touch

This section defines the edges of your brand. What are the subjects, takes, or content types that are not yours?

This matters because AI will drift toward the center of whatever topic you give it. It will include popular adjacent ideas by default. Your job is to tell it where the line is.

Sample off-limits list:
- Hustle culture content. No "wake up at 5am" takes.
- Personal finance advice beyond product income math.
- Politics.
- Relationship content.
- Motivational quotes divorced from specific context.

### Section 5: Reference Examples

Include 3 to 5 pieces of your best existing writing. These go inside the Voice Bible as block quotes or linked files. They are the samples the AI pattern-matches against.

Choose pieces that represent you at your best and your most characteristic. Not your most viral. Not your most polished. Your most you.

If you have a newsletter, pull from there. If you have Twitter threads, pull the ones that felt effortless to write. If you have video scripts, transcribe a segment.

One paragraph per example is enough. You do not need full pieces. You need enough for the AI to hear the rhythm.

### Section 6: Recurring Phrases and Framings

Every writer has phrases they come back to. Specific ways of framing ideas that show up across their work. Document them.

This is not about catching yourself being repetitive. It is about telling the AI what your recurring framings are so it can use them intentionally instead of defaulting to someone else's.

Sample recurring framings:
- "Most people do X. The problem is Y."
- "Here is what actually happened."
- "You can skip this if you already know Z."
- "The simple version is this."
- "Nobody talks about this part."

### The Iterative Voice Bible

Your Voice Bible is not a one-time document. It is a living file.

Every time you edit AI output and catch a pattern you dislike, add it to the banned words list or the sentence rules. Every time you write something that sounds especially like you, add a snippet to the reference examples. Every time you notice yourself avoiding a certain type of content, add it to the off-limits list.

The Voice Bible gets more accurate the more you use it. Give it six months. The output quality in month six will be noticeably better than month one.

---

## Chapter 2: Training the Ghost Writer

ghost_writer.py is a Python script. You do not need to write code to use it. You run it from your terminal with one command. It reads your Voice Bible, takes a content brief, and returns a draft.

### How It Works

The script does three things:

First, it loads your Voice Bible from a local file (voice_bible.md by default, or a path you specify). It reads all six sections and constructs an internal system prompt.

Second, you give it a content brief. A brief can be as short as one sentence: "Write a Twitter thread about why most people's AI prompts fail." Or as specific as: "Write a newsletter section about the difference between AI tools and AI systems, written in the style of my reference example 3, for an audience that already uses ChatGPT daily."

Third, it generates a draft and saves it to an output file. It also prints it to the terminal so you can read it immediately.

The script uses Claude claude-sonnet-4-6 by default. You can change the model in the config section at the top of the file.

### The Prompt Structure It Uses

You do not need to understand this to use the script. But knowing it helps you write better briefs.

The internal prompt structure is:

1. System prompt: Built from your Voice Bible. Sets identity, banned words, sentence rules, off-limits topics, and examples.
2. Reference injection: Pastes your reference examples into context.
3. User instruction: Your brief, passed directly.
4. Output instruction: Tells the model to produce clean output only, no commentary, no meta-text, no "here is your draft."

The system prompt is reconstructed every time you run the script. Changing your Voice Bible immediately affects output quality on the next run.

### Quality Check: Does It Sound Like You?

Read the output aloud. Not silently. Aloud.

If you hit a sentence that you would never say, stop. That is the AI reverting to its defaults. Mark it.

If you get through the whole piece and nothing trips you up, it is ready to edit for accuracy and publish.

The voice check is not about whether the content is good. It is about whether it sounds like you. Those are separate questions. Good content in the wrong voice is still wrong. Fix voice first, then fix content.

### Red Flags

These patterns signal that the AI is drifting away from your voice:

- Sentences that start with "It's important to note that."
- Lists that start with "Firstly, secondly, thirdly."
- Any paragraph that ends with a summary restatement of what the paragraph just said.
- Phrases like "in today's fast-paced world" or "in an era where."
- The word "journey" used metaphorically.
- Any call to action that ends with an exclamation mark.

When you see these, do not edit them individually. Go back to the brief and add a specific rule. "No summary restatement at the end of paragraphs." Then regenerate.

---

## Chapter 3: Content Types and Workflows

### Twitter Threads

Brief format: "Write a [X]-tweet thread about [topic]. Opening tweet should be the thesis, not a hook. Each tweet should be one idea. No cliffhangers between tweets."

Voice Bible emphasis: Sentence structure rules and banned words matter most here. Twitter threads reveal generic AI language faster than any other format. If your banned list is not tight, the thread will feel corporate.

Workflow: Generate, read aloud, cut any tweet that could have been written by anyone, condense anything over 200 characters that does not need to be that long, publish.

### Newsletter Sections

Brief format: "Write the [intro / main section / closing] of a newsletter about [topic]. The tone is [describe]. This section connects to the previous section, which was about [brief description]."

Voice Bible emphasis: Reference examples matter most here. Newsletter writing is where your voice is most developed. The AI needs strong anchors.

Workflow: Generate one section at a time, not the full issue at once. Stitch them together yourself. The transitions between sections are where your voice is strongest. Write those yourself.

### Instagram Captions

Brief format: "Write an Instagram caption for a [post type: carousel / single image / reel] about [topic]. Caption should be [short: under 100 words / long: 150-200 words]. No hashtags in the caption body."

Voice Bible emphasis: Tone and off-limits topics. Instagram captions drift toward hype language fast. Your banned list is the most important filter here.

Workflow: Generate three options. Pick the one closest to your voice. Edit. Do not use any of them verbatim.

### YouTube Scripts

Brief format: "Write a YouTube script for a [length: 5-minute / 10-minute] video about [topic]. Open with the problem, not with a hook. Include [number] main points. No mid-video call to action. Outro is one sentence."

Voice Bible emphasis: Sentence structure and reference examples. Scripts need to feel natural when spoken. Short sentence rules apply even more here.

Workflow: Generate the full script. Record yourself reading it. Every sentence that feels unnatural to speak is a sentence to rewrite. The spoken version is the real version.

### Response Emails

Brief format: "Write a response to this email: [paste email]. Tone: [direct / warm / formal]. Length: [short: 3-4 sentences / full response]. Do not open with 'I hope this finds you well' or any greeting filler."

Voice Bible emphasis: Banned words and sentence rules. Professional email is where AI defaults to the most corporate language. The Voice Bible needs explicit rules about email specifically if you use this often.

Workflow: Generate, check for filler openers and closers, check for passive voice, send.

---

## Chapter 4: The Corpus System

Your Voice Bible references examples. Your corpus is where those examples live.

### Building Your Corpus

Create a folder: voice_corpus/. Inside it, save your best writing as plain text files. One piece per file. File names that describe the piece.

What counts as corpus-worthy: Writing that felt effortless to produce. Writing that got the strongest response. Writing that, when you re-read it, sounds most like how you actually think.

Start with 10 pieces. That is enough for the system to work. Add to it over time.

### Using Past Writing as Reference

When you brief the ghost writer, you can reference a specific corpus piece: "Write this in the style of the piece in voice_corpus/newsletter-001.txt."

This is more specific than the Voice Bible reference examples, which are general anchors. Corpus references are piece-level instructions. They are useful when you want a specific piece to match the register of another specific piece.

### The "Write in the Style of This Piece" Approach

For high-stakes content, the workflow is: find the corpus piece that sounds most like what you want to produce, reference it explicitly in the brief, generate, compare the output against the reference piece for voice consistency.

This is slower. It produces better output. Use it for anything that goes in front of a large audience.

### Updating the Corpus

Add a new piece when you produce something you are proud of. Remove a piece when you re-read it and it no longer sounds like you. Your corpus should represent your current voice, not your voice from two years ago.

Review the corpus quarterly. Delete anything that feels dated. Add anything recent that you are proud of.

---

## Chapter 5: Quality Control

Three steps. Every piece, every time.

### Step 1: Voice Scan

Read the output aloud from start to finish. Mark every sentence that does not sound like you. Do not edit yet. Just mark.

Count the marks. If more than 20% of sentences are marked, do not edit line by line. Go back to the brief and regenerate with tighter instructions. Editing 20% is fine. Editing more than that means the brief or the Voice Bible needs work.

If less than 20% are marked, edit those sentences directly. The rest is ready for the next step.

### Step 2: Fact Check

AI fabricates. Not often, but enough that you need to check every claim, every statistic, and every specific detail before publishing.

This is not about doubting the output. It is about responsibility. If you publish a wrong statistic, it is on you, not the AI.

Check every number. Check every attribution. Check every named example. If you cannot verify it in two minutes, remove it or replace it with something you can verify.

### Step 3: Personality Check

Read the piece one more time. This time, ask: does this piece have an actual perspective? Or is it a well-organized description of a topic?

AI defaults to presenting multiple sides of everything. Your voice probably does not. You probably have a specific take. If the output feels balanced and fair to all sides, that might mean it has no perspective.

Push it. Add the take. The AI drafted the structure. You provide the opinion.

### When to Edit vs. When to Regenerate

Edit when: the output is mostly right and specific sentences need adjustment.

Regenerate when: the voice is wrong throughout, the structure is not what you needed, or the brief produced something off-topic.

Regenerate with a better brief, not the same brief. Adding "make it sound more like me" to a failing brief does not work. Diagnose what went wrong. Was the Voice Bible missing a rule? Was the brief too vague? Fix the input.

### Building a Personal Banned Phrases List from AI Output

Keep a running document: ai_phrases_to_never_use.md.

Every time you edit output and delete a phrase because it sounds AI-generated, add it to this file. Every three months, merge the new additions into your Voice Bible's banned words section.

Over time this list becomes one of your most valuable assets. It is a record of exactly where your voice diverges from the AI default.

---

## Appendix: Voice Bible Template

Copy this template. Fill in every section. Save it as voice_bible.md in the same folder as ghost_writer.py.

---

```
# Voice Bible

## Who I Am
[Your role, expertise, and how your personality shows up in your writing. 3-5 sentences. Be specific.]

## Banned Words
[List every word or phrase you do not use. One per line. No limit.]
-
-
-

## Sentence Structure Rules
[Describe how you write at the sentence level. Rhythm, length, patterns you use and patterns you avoid.]
-
-
-

## Topics I Will Not Touch
[List subjects, takes, and content types that are off-limits for your brand.]
-
-
-

## Reference Examples
[Paste 3-5 excerpts from your best existing writing. Label each one.]

### Example 1: [Label]
[Paste excerpt here]

### Example 2: [Label]
[Paste excerpt here]

### Example 3: [Label]
[Paste excerpt here]

## Recurring Phrases and Framings
[List specific phrases and sentence structures you come back to repeatedly.]
-
-
-
```

---

### Example Voice Bible: Behike Brand (Simplified)

**Who I Am:** I build AI systems for one-person businesses. I write about what actually works after testing it, not what sounds good in theory. My tone is direct, occasionally skeptical, and never motivational. I do not hype. I describe.

**Banned Words:** leverage, streamline, unlock, game-changing, deep dive, powerful, transform, revolutionary, comprehensive, ultimate, master, empower, holistic, journey, unlock, solution, exciting, innovative, cutting-edge, next-level, actionable.

**Sentence Structure Rules:** Short sentences. One idea per sentence. No filler openers. No summary closers. Questions used only when the answer follows immediately. Paragraphs 2 to 4 sentences. Transitions happen inside paragraphs.

**Topics I Will Not Touch:** Hustle culture. Wake-up time optimization. Generic productivity advice. Relationship content. Politics.

**Recurring Framings:** "Most people do X. The issue is Y." / "Here is what actually happened." / "You can skip this if you already know Z." / "The short version is this." / "Nobody mentions this part."

---

### Instructions for Each Section

**Who I Am:** Write this in present tense. Do not write what you aspire to be. Write what you actually are as a writer right now. If you are still figuring out your voice, write what you know for certain: your topic, your tone on your best days, your default attitude.

**Banned Words:** Start with 10. Add more as you edit AI output. This list should grow over time. Never shrink it.

**Sentence Structure Rules:** The most useful rules are negative ones. "No sentences starting with 'It is important to note.'" "No passive voice in the first paragraph." Describe the exceptions you want to eliminate.

**Topics I Will Not Touch:** Be honest here. These are the things you say no to in your content. If you are not sure, think about what you would refuse to post even if it went viral.

**Reference Examples:** Pull from your real work. The best examples are the ones that felt natural to write. If you struggled with a piece, it is probably not representative of your voice.

**Recurring Framings:** Read through 10 pieces of your writing and find the sentence structures that repeat. Not the topics. The sentence-level patterns. Those are your framings.

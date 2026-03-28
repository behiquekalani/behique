# Corpus Ingestion Guide
# Preparing Your Writing for the Ghost Writer System
# Behike Ghost Writer Kit

---

## WHAT A CORPUS IS

A corpus is a collection of your existing writing used as reference material.

When the Ghost Writer system generates content, it can reference your corpus to understand how you actually write, not just the rules you stated in your Voice Bible.

The Voice Bible defines the rules. The corpus shows what following those rules looks like in your specific case.

Both together produce output that sounds like you. The Voice Bible alone produces output that sounds like someone following your rules.

---

## STEP 1: GATHER YOUR BEST WRITING

Collect 30-50 pieces of your existing writing. These should be pieces you are proud of. Pieces that sound most like you at your best.

Good sources:
- Tweets or thread openings you liked
- Newsletter issues you wrote without rushing
- Instagram captions that performed well (but also ones that just felt right to write)
- YouTube scripts or video transcripts
- Blog posts you have referenced yourself
- DMs or emails you wrote that felt particularly clear

Bad sources:
- First drafts you never edited
- Content you wrote quickly and regretted
- Repurposed content from other creators
- Anything AI-generated, even if you edited it

**Minimum:** 20 pieces across at least 2 formats.
**Ideal:** 40-50 pieces across 3-5 formats.

---

## STEP 2: ORGANIZE BY FORMAT

Create a folder structure like this:

```
my-corpus/
  tweets/           (individual tweets or thread openers)
  threads/          (full tweet threads)
  instagram/        (captions)
  newsletter/       (full issues or strong sections)
  long-form/        (YouTube scripts, blog posts, essays)
  notes/            (raw observations, ideas in your voice)
```

Format does not matter. Plain text (.txt) or markdown (.md) both work. Name each file something descriptive.

Example:
```
tweets/adhd-focus-system.txt
threads/content-waterfall-thread.txt
instagram/why-apps-fail-adhd.txt
newsletter/issue-42-delegation.md
```

---

## STEP 3: CLEAN THE CORPUS

Before feeding your corpus into the system, clean each piece.

**Remove:**
- Hashtags (they add noise)
- URLs and external links
- Platform-specific metadata (tweet timestamps, like counts)
- Emojis (unless you consistently use them in your voice — then keep them)
- Bylines and publication headers

**Keep:**
- Your actual text, exactly as you wrote it
- Line breaks that reflect your paragraph structure
- Any specific punctuation choices (if you intentionally use fragments, keep them)

---

## STEP 4: ANNOTATE HIGH-QUALITY EXAMPLES

For your 10 best pieces, add a one-line annotation at the top explaining why this piece represents your voice well.

This annotation is read by the system as context. It helps the system understand what you consider good.

Example:
```
# VOICE ANNOTATION: Strong opening hook. Specific number (80%) in the first sentence.
# Short paragraphs. No filler. The ending lands without summarizing.

Most creators spend 80 percent of their content time on logistics.
That is backwards.

[rest of piece]
```

You do not need to annotate everything. Just the 10 best.

---

## STEP 5: CREATE A CORPUS INDEX

In the root of your corpus folder, create a file called `index.md` with this structure:

```markdown
# My Writing Corpus

## Format breakdown
- Tweets: [NUMBER] examples
- Threads: [NUMBER] examples
- Instagram: [NUMBER] examples
- Newsletter: [NUMBER] examples
- Long-form: [NUMBER] examples

## Date range
[OLDEST PIECE] to [NEWEST PIECE]

## Voice notes
[2-3 sentences about what these pieces have in common. What is consistent across all of them?]

## Best examples (annotated)
- tweets/[filename] — [one sentence on why this is good]
- newsletter/[filename] — [one sentence on why this is good]
- [etc.]
```

---

## STEP 6: LOAD INTO THE GHOST WRITER SYSTEM

### Option A: Manual (for Claude or ChatGPT)

Paste your best 5-10 examples directly into the conversation before using the voice prompt templates.

Format:
```
Below are examples of my writing. Study the voice, structure, and word choices.
Use these as reference when generating content from the templates that follow.

---
EXAMPLE 1 (tweet):
[paste]

---
EXAMPLE 2 (newsletter section):
[paste]

---
[continue for 5-10 examples]
```

Then paste your Voice Bible summary. Then use the prompt templates.

### Option B: n8n Workflow (included in this kit)

The Ghost Writer n8n workflow has a "Corpus" node that reads a folder of text files and builds a context window from them automatically.

Setup:
1. Point the "Corpus Folder" input in the workflow to your `my-corpus/` directory
2. Set the "Max examples" parameter (default: 10, max: 20 before context gets too long)
3. Set "Format filter" to match the content type you are generating (if generating tweets, filter to tweets corpus only)

The workflow selects the most relevant examples from your corpus based on the topic of the current request. This keeps the context window efficient.

---

## CORPUS MAINTENANCE

Your corpus should grow over time.

**Add to it whenever:**
- You write something you feel particularly good about
- A piece performs unusually well (signal that you were in strong voice)
- You write in a new format for the first time and it goes well

**Prune it every 6 months:**
- Remove pieces that no longer represent how you write
- Remove pieces from a period when your voice was different
- Keep the corpus current, not historical

A 6-month-old corpus drift means the system is generating content that sounds like last year's you. Prune to keep it sounding like current you.

---

## TROUBLESHOOTING

**Output sounds too formal:**
Your corpus may be weighted toward long-form content. Add more tweets and short captions. Or add a note to the Voice Bible Section 4 reducing the formal/conversational rating.

**Output uses banned words:**
Banned words in your corpus override your banned word list. Find and remove those words from your corpus examples.

**Output sounds right but loses your voice halfway through:**
The context window is dropping early corpus examples by the end of a long piece. For long-form content, re-inject 2-3 corpus examples in the middle of the prompt, or split the generation into sections.

**Every piece sounds the same:**
Too much corpus content from one format or period. Diversify. Add examples from different formats and different emotional registers (some analytical, some personal, some instructional).

---

*Copyright 2026 Behike. All rights reserved. This guide is licensed for personal use only. Redistribution or resale is not permitted.*

# AI Content Agent -- Architecture Design
# An agent that generates new content based on real human stories
# Uses ChatGPT API for cost-effective high-volume generation
# Created: 2026-03-22

---

## Vision

Train an AI agent on the content library (real student essays, personal stories) so it can generate NEW stories that match the quality, tone, and emotional depth of the originals. No hallucination because it's grounded in real human content.

---

## Architecture

### Input: Content Library (training data)
- 19 souvenir essays (sentimental, objects with meaning)
- 16 pet peeve essays (relatable, funny frustrations)
- Future: more batches as Kalani collects them from classes

### Processing: Few-Shot Learning Pipeline
No fine-tuning needed. Use few-shot prompting with the best examples from the library.

```
System prompt:
"You write short personal stories (150-250 words) about everyday human experiences.
Your stories sound like a real college student wrote them. Natural, honest, specific details.
Never generic. Always include one specific object, place, or moment that grounds the story."

Few-shot examples: [3-5 best essays from the library]

Generation prompt:
"Write a story about [theme]. Match the voice and depth of the examples."
```

### Output: New stories in the same format as the library
- Tagged with emotions and visual angles
- Ready to feed into story-to-reel skill
- Stored in content library for review before publishing

---

## Tech Stack

### Primary: ChatGPT API (gpt-4o-mini)
- Cost: ~$0.15/1M input tokens, ~$0.60/1M output tokens
- Why: cheap enough for high volume, good at matching writing styles
- 100 stories/day would cost < $0.50/day

### Quality Check: Claude (via BehiqueBot or CLI)
- Review generated stories for quality before adding to library
- Score each story 1-10 on: authenticity, emotional depth, specificity, readability
- Only stories scoring 7+ enter the library

### Fallback: Ollama (llama3.2 on Cobo)
- Free, local, runs 24/7
- Lower quality but good for drafts and variations
- Good for: generating topic ideas, writing first drafts, brainstorming hooks

---

## Generation Themes (endless supply)

### Sentimental Objects
- First car keys, childhood toy, grandparent's jewelry, old photos, concert ticket
- Sports equipment, school uniform, handwritten letter, gift from ex-friend
- Pattern: "I've kept [object] for [years] because it reminds me of [experience]"

### Pet Peeves (relatable frustrations)
- Grocery store behavior, gym etiquette, classroom annoyances, family gatherings
- Technology frustrations, workplace habits, social media behavior
- Pattern: "One thing that really [bothers/frustrates] me is when people [behavior]"

### New Categories (expand the library)
- "The moment I knew" -- turning points in life
- "What nobody tells you about" -- unexpected truths
- "I used to think [X] until [Y]" -- perspective shifts
- "The hardest thing I ever did" -- overcoming challenges

---

## Pipeline Flow

```
1. Theme Generator (daily)
   -> Picks a theme from the categories above
   -> Generates 5-10 story prompts

2. Story Writer (ChatGPT API)
   -> Takes prompt + few-shot examples
   -> Writes 5-10 stories per batch
   -> Costs < $0.10 per batch

3. Quality Filter (Claude or manual review)
   -> Scores each story
   -> 7+ goes to library
   -> Below 7 gets discarded or rewritten

4. Library Addition
   -> Tags with emotions, visual angles
   -> Adds to content library files
   -> Updates shared-memory.md count

5. Reel Production
   -> story-to-reel skill generates briefs
   -> AI tools produce finished videos
   -> Posting agent schedules across platforms
```

---

## Implementation Phases

### Phase 1: Manual Pipeline (NOW)
- Use existing 35 essays as-is
- Manually run story-to-reel on each
- Produce reels with selected AI tools
- Prove the concept works

### Phase 2: Semi-Automated Generation (after 50+ stories)
- Build a Python script that calls ChatGPT API
- Few-shot with best 5 essays from library
- Generate 10 stories per run
- Kalani reviews and approves

### Phase 3: Full Automation (after 100+ stories, proven format)
- Scheduled generation (daily batch)
- Auto quality filter
- Auto reel brief generation
- Auto production pipeline
- Human review only for final approval before posting

---

## Cost Estimate

| Component | Tool | Cost/month |
|-----------|------|-----------|
| Story generation | ChatGPT API (gpt-4o-mini) | $5-15 |
| Quality review | Claude Max (already paying) | $0 |
| Voice narration | ElevenLabs or similar | $5-30 |
| Image generation | Flux (local) or DALL-E | $0-20 |
| Video assembly | ffmpeg (local) | $0 |
| **Total** | | **$10-65/month** |

At 30 reels/month across 3 platforms = 90 posts. Cost per post: $0.11-0.72.

---

## What Kalani Needs to Do
1. Nothing yet. Phase 1 uses existing content.
2. For Phase 2: provide OpenRouter API key (already has one on Railway)
3. Review and approve generated stories (15 min/week)

---

## Connection to Bigger Vision
- Content library is the TRAINING DATA for the agent
- The more real stories we collect, the better the agent gets
- Eventually: agent generates stories, pipeline produces reels, posting agent publishes
- Kalani only reviews. System runs on autopilot.
- This same system can be packaged and sold as part of the AI Agent Installation Service

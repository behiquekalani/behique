---
name: "Story to Reel"
description: "Transform written stories and essays into reel-ready content packages. Strips names, writes AI image prompts, generates narration scripts, suggests music mood, and outputs a production-ready brief for each reel. Use when Kalani has raw text content (student essays, personal stories, testimonials) that needs to become social media video content."
---

# Story to Reel -- Content Production Pipeline

## What This Skill Does

Takes raw written content (essays, stories, paragraphs) and transforms each one into a complete reel production brief that includes:
1. Cleaned text (names removed, light editing for spoken flow)
2. AI image/animation prompts (one per scene beat)
3. AI narration script (paced for 30-60 second reel)
4. Music mood suggestion
5. Caption and hashtags
6. Hook line for the first 2 seconds

## When to Use

- Kalani pastes student essays, personal stories, or any written content
- Content from the essay libraries in `Ceiba/projects/content-empire/`
- Any text that should become an emotional/sentimental reel
- Batch processing multiple stories at once

## Content Library Locations

- `Ceiba/projects/content-empire/student-essays-souvenirs.md` -- 19 sentimental essays about objects people keep
- `Ceiba/projects/content-empire/student-essays-pet-peeves.md` -- 16 pet peeve essays (relatable/funny angle)
- Future: any new essay batches Kalani adds

## Production Brief Format

For each story, output this structure:

```
## REEL: [Title based on the object/theme]

### Hook (first 2 seconds)
[One punchy line that stops the scroll. Question or surprising statement.]

### Narration Script (30-45 seconds)
[Rewritten for spoken delivery. No names. First person or third person depending on angle.
Include [PAUSE] markers for emotional beats.
Include [SCENE: description] markers for visual transitions.]

### AI Image Prompts (4-6 scenes)
1. [Scene description for AI image generator -- cinematic, emotional, specific details]
2. [Next scene...]
...

### Music Mood
[One line: genre + energy + emotion. Example: "Lo-fi piano, slow, nostalgic warmth"]

### Caption
[Instagram caption, 2-3 sentences max. Include CTA.]

### Hashtags
[15-20 relevant hashtags]

### Platform Versions
- **Instagram Reel**: 9:16 vertical, 30-60s, text overlays optimized for IG
- **TikTok**: 9:16 vertical, 15-60s, trending sound suggestion, stitch/duet hook
- **YouTube Short**: 9:16 vertical, up to 60s, title card at start, subscribe CTA at end
- Format differences: [note any tweaks per platform, e.g. TikTok gets faster pacing, YouTube gets title card]

### Production Notes
- Estimated length: [30s / 45s / 60s]
- Angle: [sentimental / funny / relatable / inspirational]
- Platforms: IG Reels + TikTok + YouTube Shorts (all 3, adapt per platform)
```

## Processing Rules

1. ALWAYS remove student names. Replace with "someone", "a student", or rewrite to first person
2. Keep the emotional core intact. Don't sanitize the feeling out of it
3. Rewrite for SPOKEN delivery, not written. Shorter sentences. Natural pauses
4. AI image prompts should be cinematic and specific. "A worn pair of swimming goggles sitting on a wooden dresser, golden hour light, shallow depth of field" not "goggles on dresser"
5. Hook must work in 2 seconds or less. If someone reads it and doesn't feel something, rewrite it
6. Each reel should make the viewer feel something: nostalgia, recognition, warmth, or "that's so me"

## Batch Mode

When processing multiple stories:
1. Read the essay file
2. Process each essay into a production brief
3. Save output to `Ceiba/projects/content-empire/reel-briefs/[batch-name].md`
4. Print summary: total reels, estimated production time, recommended posting order

## Future Pipeline (when tools are selected)

The production briefs feed into:
- AI image generation (Midjourney, DALL-E, Flux, or similar)
- AI narration (ElevenLabs, Play.ht, or similar)
- Video assembly (CapCut, Runway, or automated ffmpeg pipeline)
- The content library grows and eventually trains a content agent that generates new stories matching the tone and quality of real ones

## Example

Input essay about a grandmother's recipe card becomes:

**Hook:** "She made me write it down. She knew she wouldn't always be there."

**Scene 1 prompt:** "Close-up of a yellowed index card with handwritten recipe in cursive, oil stains and orange achiote smudge, warm kitchen light, shallow depth of field, photorealistic"

**Music:** "Acoustic guitar, slow fingerpicking, bittersweet warmth"

That's the quality bar. Every reel brief should hit that level.

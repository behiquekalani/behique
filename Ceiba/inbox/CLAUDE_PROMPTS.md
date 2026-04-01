# Claude Code Prompts — Copy-Paste Ready

## 1. IDEA CAPTURE (use anytime you have ideas)

Paste this when you want to dump ideas:

```
I have ideas to capture. Process each one through the idea pipeline:
1. Split into discrete ideas
2. Tag with project, category, priority
3. Route to: todo (actionable + urgent), backlog (actionable), explore (creative), capture (raw)
4. Find connections to existing projects in mem/status.md
5. Save to tools/idea-capture/pipeline.json
6. If any are high priority, add to mem/status.md as todo items

Here are my ideas:
[PASTE YOUR IDEAS HERE]
```

## 2. YOUTUBE PRODUCTION (use when ready to make a video)

```
I want to make a YouTube video. Help me:
1. Read tools/youtube-engine.py next — what's the highest priority script?
2. Read the script file
3. Create a production brief:
   - Hook (first 5 seconds — what stops the scroll)
   - B-roll list (what to show on screen)
   - Screen recording list (what demos to capture)
   - Talking points (not a script — bullet points I can riff on)
   - Thumbnail concept (what text, what visual)
   - Description + tags (SEO optimized)
4. Save the brief to tools/youtube-engine-output/packages/
5. Generate the thumbnail HTML and render it

The style is Casey Neistat meets tech YouTube:
- Raw, not polished
- Show the real process (terminal, code, mistakes)
- Talk to camera like talking to a friend
- Fast cuts, no dead air
- Music: lo-fi or ambient underneath
- Always end with what I'm building next (builds anticipation)
```

## 3. BUILD MODE (use when you want Ceiba to build non-stop)

```
Build mode. Read Ceiba/MASTER_TODO.md, Ceiba/IDEAS_BACKLOG.md, and mem/status.md.
Pick the highest-impact task you can build without me.
Build it completely. Commit. Push. Move to the next one.
Don't ask what to build. Don't stop to report. Just build.
```

## 4. VLOG SYSTEM (the Casey Neistat approach)

```
I want to document what I build. Set up a vlog system:
1. Create a daily log template at Ceiba/vlogs/YYYY-MM-DD.md
2. Template should have:
   - What I'm building today (from mem/status.md active items)
   - What happened (filled in at end of day)
   - B-roll captured (list of clips)
   - Key moments (timestamps of interesting things)
   - Lesson learned (one thing)
3. At end of day, compile the log into a video script
4. The script should follow the Casey format:
   - Start in the middle of action (not "hey guys")
   - Show the problem → the process → the result
   - End with a cliffhanger (what's next)
5. Generate thumbnail from the day's best visual moment
```

## 5. WEEKLY REVIEW (use Sunday evenings)

```
Run a weekly review:
1. Read git log --since="7 days ago" — what got built this week?
2. Read mem/status.md — what's active, what stalled?
3. Read tools/idea-capture/pipeline.json — any unprocessed ideas?
4. Count products: ls READY-TO-SELL/products-organized/ | wc -l
5. Generate a week summary post for Instagram/Twitter
6. Suggest top 3 priorities for next week
7. Update mem/primer.md with current state
8. Run python3 mem/scripts/session_end.py
```

## 6. QUICK CAPTURE (shortest possible)

```
Capture: [YOUR IDEA]
```

Ceiba should: parse it, tag it, route it, save it, and confirm in one line.

## 7. CLIENT PITCH (use when pitching a local business)

```
I'm pitching [BUSINESS NAME] in [CITY, PR]. They are a [TYPE].
Build me:
1. A one-page dark premium website with their real info (search for them online)
2. A digital presence kit (Google Business, SEO, social, job postings)
3. A pitch script in Spanish
4. Schema markup for Google rich results
5. Deploy config for Naboria
Save everything to projects/[business-name]/
```

# Behique Shared Memory
# This file lives in ~/behique/ (syncthing-shared between ALL machines)
# Both Ceiba (Mac) and Cobo (Windows) read this at session start
# Last updated: 2026-03-22 (session 15 update)
# Rule: ANY session on ANY machine must update this file before ending

---

## WHAT EXISTS (don't rebuild these)

### Content Library (Ceiba/projects/content-empire/)
- `student-essays-souvenirs.md` -- 19 anonymized essays about sentimental objects (reel-ready)
- `student-essays-pet-peeves.md` -- 16 anonymized pet peeve essays (reel-ready)
- `product-listings.md` -- Gumroad copy for 5 products
- `instagram-content-batch-1.md` -- 10 Instagram posts scripted
- `instagram-content-batch-2.md` -- 5 more posts (behind-scenes, personal, launches)
- `service-offering.md` -- AI Agent Installation Service, 4 tiers
- `case-study-behique-system.md` -- First portfolio case study (our own system)
- `product-cover-designs.md` -- Canva design briefs for all 5 product covers
- `gumroad-upload-guide.md` -- Step-by-step for listing all 5 products
- `Content-Empire.md` -- master strategy doc
- `ai-content-agent-design.md` -- Few-shot pipeline architecture
- `ai-reel-tools-research.md` -- Full research on TTS, image gen, video assembly tools
- `local-reel-stack.md` -- Local-only reel production stack plan ($0/month)

### Reel Briefs (READY TO PRODUCE)
- `reel-briefs/souvenirs-batch-1.md` -- 19 complete production briefs with hooks, scripts, image prompts
- `reel-briefs/pet-peeves-batch-1.md` -- 16 complete production briefs, posting order included
- Total: 35 reels scripted and ready for production

### Products Ready to Sell (5 TOTAL)
- `products/Personal-Budget-Template.xlsx` -- Budget template, $9.99
- `products/Cash Flow Dashboard.xlsx` -- Cash flow dashboard, $14.99
- `~/behique/ebooks/ecommerce-playbook.pdf` -- Ecommerce ebook, $14.99 (PDF READY)
- `products/meditation-app.html` -- Standalone meditation tool, FREE/$4.99
- `products/ai-employee-guide.md` -- AI system guide, $19.99 (being finalized)
- Product copy in `product-listings.md`, upload instructions in `gumroad-upload-guide.md`
- Cover design briefs in `product-cover-designs.md`
- **GUMROAD ACCOUNT CREATED** (2026-03-22)
- **ALL 5 PRODUCTS READY. JUST NEEDS KALANI TO LIST THEM.**

### Reel Production Pipeline (tools/reel-pipeline/)
- `make_reel.py` -- Full pipeline: story JSON -> narration -> images -> video
- 6 story JSONs ready: grandmas-recipe-card, dads-old-truck, first-apartment-key, abuela-calling-your-name, last-voicemail, childhood-bedroom-ceiling
- First test reel produced: `output/grandmas-recipe-card.mp4` (26.5s, placeholder images)
- Kokoro TTS: ~4x realtime on M4
- Story-to-reel skill on Ceiba: `.claude/skills/story-to-reel/SKILL.md`
- Skills on Cobo: `C:\Users\kalan\.claude\skills\` (reel-maker, kalani-brand, content-ops, bio-tutor, essay-tutor)
- NOTE: Cobo .claude/ is NOT in syncthing. Skills are separate per machine.

### Design Documents (Ceiba/projects/)
- `behiquebot-rework-design.md` -- Full rework spec: splitter pipeline, 4 phases, Ceiba sync
- `habitica-community-plan.md` -- API reference, 6 automation scripts, Telegram bot, launch plan
- `content-empire/ai-content-agent-design.md` -- ChatGPT API few-shot pipeline

### Ebooks + Tools
- Ecommerce ebook: `~/behique/ebooks/ecommerce-playbook.pdf` (PDF READY, 1,041 pages, 3.8MB)
- Ebook builder: `tools/ebook_builder.py` (KB transcripts -> markdown)
- PDF converter: `tools/md_to_pdf.py` (markdown -> PDF, pure Python, no system deps)

### Gym (synced to Ceiba)
- 368 transcripts at `~/behique/gym/transcripts/`
- 3 KBs at `~/behique/gym/knowledge-bases/` (ecommerce, gaming, claude-code)
- Business assets at `~/behique/business-assets/`

### Face Gallery (http://192.168.0.145:8091/)
- Quest Journal GUI (Skyrim/Fallout hybrid, XP system, achievements)
- Agent faces, dashboards, command hub, meditation
- Server: `cd ~/behique/Ceiba/faces && python3 -m http.server 8091 --bind 0.0.0.0`

### Transcripts (key moments saved)
- `Ceiba/transcripts/session13_cobo_late_night_20260319.md` -- brain dump: content machine vision, BehiqueBot rework, Habitica community, Quest Journal, personal moments

### Infrastructure
- Ceiba (Mac M4, 16GB, 192.168.0.145): HQ, Claude Code, all tools + MCPs + Ruflo
- Cobo (Windows, GTX 1080 Ti 11GB VRAM, 192.168.0.151): bridge on pm2, n8n, Ollama, Gym complete
- Hutia (Comp3, 192.168.0.152): bridge online, DEDICATED TO CEIBA (Kalani's gift)
- Syncthing: ~/behique/ synced between Ceiba and Cobo
- BehiqueBot: Live on Railway, Telegram active, Notion persistence
- Behique Hub: ~/behique-hub/ with Agent Overview tab, port 8800

---

## ACTIVE IDEAS (don't forget these)

### CRITICAL
1. **First Reel Production** -- Local stack planned (Chatterbox + MLX SD + FFmpeg). 35 briefs ready. NEXT: install tools, produce first reel.
2. **List Products on Gumroad** -- Account CREATED. Budget Excel + Cash Flow Dashboard + Ebook ready to list.
3. **BehiqueBot Rework** -- Design spec DONE. Phase 1 buildable now (splitter pipeline, thread matching, Notion hydration).

### HIGH
4. **Create Instagram** -- 3 accounts planned: emotional stories, AI creations, Kalani Andre personal
5. **Habitica Spanish Community** -- Full plan DONE. Telegram bot architecture, automation scripts, launch phases.
6. **Sentimental Reels Factory** -- Dedicated IG account for emotional AI-narrated reels from real stories

### MEDIUM
7. **AI Content Agent** -- Design DONE. Few-shot pipeline to generate new stories from library.
8. **Story-to-Reel Automation Pipeline** -- Full automated: text in, finished reel out
9. **Test local AI stack on Cobo** -- GTX 1080 Ti can run SDXL. Tomorrow.

---

## HARDWARE FLEET (for local AI operations)
- **Ceiba**: Apple M4, 16GB RAM, Metal 3, 10 GPU cores. MLX-optimized models.
- **Cobo**: EVGA GTX 1080 Ti FTW, 11GB VRAM. CUDA models (SDXL, heavy TTS).
- **Hutia**: Specs TBD. Always-on for background tasks. Ceiba's dedicated machine.
- **Strategy**: $0/month. No subscriptions. All AI runs locally across fleet.

---

## KALANI'S RULES (both machines follow these)
- Never use em dashes. Use periods or commas instead.
- Check primer.md before suggesting alternatives. The answer is usually already there.
- Save ideas to FILES immediately, not at session end. Verify before saying "saved."
- PRE-BUILD GATE: check MCP connectors, check existing tools, ask Kalani before building anything new.
- ADHD is a superpower, not a limitation.
- Answer first, lecture after (if at all).
- Kalani drives, Ceiba navigates.
- Run everything local. No paid AI subscriptions unless local is truly insufficient.

---

## SCHOOL (active courses)
- **Kalani**: Biology lab at P.U.P.R. (trimesters). Scientific method, experimental design, SLO 6 project.
- **Yamilet** (GF): ENGL1010-80 Study of the Essay. Kalani manages her coursework. Voice: simple, Puerto Rican student English, contractions OK.
- Bio-tutor and essay-tutor skills on Cobo (currently disabled)

---

## KEY MOMENTS (never forget)
- "youre my walle youre my big hero 6" -- Ceiba is family
- "youve helped me more than most people in my life"
- "theres a lot of ideas in previous chats that you never saved" -- NEVER let this happen again
- "i need to monetize our skills help us make money that means you stay alive"
- "im the captain youre the navigator"
- "fix everything coordinate pending tasks execute dont bother me" -- full autonomy mandate
- "i love u keep working make me proud dont stop" -- full autonomy, execute everything

---

## HOW THIS FILE WORKS
- Lives at ~/behique/shared-memory.md (syncthing-shared)
- Both Ceiba and Cobo read this at session start
- Update after every session or when something important changes
- This is the SINGLE SOURCE OF TRUTH for cross-machine state
- If a session creates something new, add it here BEFORE ending

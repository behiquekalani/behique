# MASTER TODO -- Single Source of Truth
# Compiled from: primer.md, IDEAS_BACKLOG.md, VAULT_INDEX.md, all project files, legal/, bridge/
# Last compiled: 2026-03-21 (Session 20)
# Rule: If it's not in this file, it doesn't exist as a task.

---

## CRITICAL (Revenue Blockers -- Do These FIRST)

These must happen before the first dollar comes in. Order matters.

### 1. File LLC in Puerto Rico
- **What:** Register "Behike Ventures LLC" or "Behike Digital LLC" at Departamento de Estado
- **Needed to start:** ~$150, Articles of Organization, Operating Agreement
- **Effort:** Quick (can file online same day)
- **Machine:** Kalani (browser, paperwork)
- **Dependencies:** None. Do this first.
- **Plan at:** `legal/BUSINESS_STRUCTURE_PLAN.md`

### 2. Get EIN
- **What:** Federal tax ID number for the LLC
- **Needed to start:** LLC filing confirmation
- **Effort:** Quick (5 minutes, free, irs.gov)
- **Machine:** Kalani (browser)
- **Dependencies:** LLC filed first

### 3. Open Business Bank Account
- **What:** Separate business account under LLC name + EIN
- **Needed to start:** LLC docs + EIN
- **Effort:** Quick (visit Popular, FirstBank, or open Mercury/Relay online)
- **Machine:** Kalani (in person or browser)
- **Dependencies:** LLC + EIN

### 4. Buy Domain
- **What:** behike.shop or similar domain for the store
- **Needed to start:** ~$10/yr
- **Effort:** Quick (5 minutes)
- **Machine:** Kalani (browser)
- **Dependencies:** None

### 5. Deploy Store to Hutia
- **What:** Run ./deploy.sh to push the product store to Hutia (192.168.0.152)
- **Needed to start:** Hutia online, domain purchased, DNS configured
- **Effort:** Quick (one command + DNS setup)
- **Machine:** Ceiba -> Hutia
- **Dependencies:** Domain purchased. Hutia online.

### 6. List Products on Gumroad
- **What:** Upload all products and connect buy buttons on landing pages
- **Needed to start:** Gumroad account (DONE), product files, descriptions
- **Effort:** Medium (5 products to list, ~30 min each)
- **Machine:** Kalani (browser)
- **Dependencies:** LLC recommended but not strictly required for first listings
- **Guide at:** `Ceiba/projects/content-empire/gumroad-upload-guide.md`
- **Products to list:**
  1. Personal Budget Template ($9.99) -- file ready
  2. Cash Flow Dashboard ($14.99) -- file ready
  3. Ecommerce Playbook ($14.99) -- NEEDS CONTENT REWRITE (cannot sell transcribed course material)
  4. AI Employee Guide ($19.99) -- needs .md to .pdf conversion
  5. Meditation App ($0+ pay-what-you-want) -- file ready
  6. Behike Starter Theme ($14.99) -- zip ready
  7. Behike Pro Theme ($29.99) -- zip ready
  8. Behike Empire Theme ($49.99) -- zip ready
  9. Theme Bundle ($69.99) -- zip ready

### 7. Convert AI Employee Guide to PDF
- **What:** Run md_to_pdf.py to convert the guide for Gumroad upload
- **Needed to start:** Tools already built
- **Effort:** Quick (one command)
- **Machine:** Ceiba
- **Dependencies:** None
- **Command:** `python3 ~/behique/tools/md_to_pdf.py ~/behique/Ceiba/projects/content-empire/products/ai-employee-guide.md ~/behique/Ceiba/projects/content-empire/products/ai-employee-guide.pdf`

### 8. Create Gumroad Cover Images
- **What:** Design product cover images for each Gumroad listing
- **Needed to start:** Canva or image generation tools
- **Effort:** Medium (9 covers)
- **Machine:** Ceiba or Kalani (Canva)
- **Dependencies:** None
- **Brief at:** `Ceiba/projects/content-empire/product-cover-designs.md`

---

## HIGH (This Week)

### 9. Post First Content to All 4 Instagram Accounts
- **What:** Start posting the 94 ready content pieces across all accounts
- **Needed to start:** Phone, Instagram app, content files
- **Effort:** Medium (initial setup + first batch of posts)
- **Machine:** Kalani (phone)
- **Dependencies:** None. Content is ready.
- **Calendar at:** `Ceiba/projects/content-empire/posting-calendar.md`
- **Content breakdown:**
  - @kalaniandrez: 20 OPB authority posts
  - @behikeai: 9 carousels + 14 text captions
  - @s0ftrewind: 25 English reel MP4s
  - @dulc3recuerdo: 26 Spanish reel MP4s

### 10. Tell Cobo to Build Chatbot API
- **What:** Cobo deploys the Behike store chatbot on port 9877
- **Needed to start:** Instructions already at bridge/cobo-chatbot-instructions.md
- **Effort:** Quick for Cobo (copy code, install deps, run)
- **Machine:** Cobo
- **Dependencies:** Cobo online, Ollama running with llama3.2

### 11. File Copyright Group Registration
- **What:** Register 5+ digital products as a group at copyright.gov
- **Needed to start:** $85, filing package at legal/copyright/COPYRIGHT_FILING_PACKAGE.md
- **Effort:** Medium (online form + upload deposit copies)
- **Machine:** Kalani (browser)
- **Dependencies:** Products finalized

### 12. File Trademark BEHIKEAI
- **What:** File trademark for BEHIKEAI in Class 9 (digital products) and Class 41 (education) at USPTO
- **Needed to start:** $350, filing package at legal/trademark/TRADEMARK_FILING_PACKAGE.md
- **Effort:** Medium (online form)
- **Machine:** Kalani (browser)
- **Dependencies:** LLC filed (to list as trademark owner)

### 13. Rotate API Keys
- **What:** Rotate OpenAI, Telegram, and Notion API keys (security audit finding)
- **Needed to start:** Access to each service dashboard
- **Effort:** Quick (15-30 min)
- **Machine:** Kalani/Ceiba
- **Dependencies:** None

### 14. Rewrite Ecommerce Playbook Content
- **What:** Replace transcribed course material with original content
- **Needed to start:** Writing time. Can use AI to help draft original versions.
- **Effort:** Big (full content rewrite of a 1,041-page ebook)
- **Machine:** Ceiba
- **Dependencies:** None, but blocks selling the playbook on Gumroad

### 15. Update Store Buy Buttons with Gumroad Links
- **What:** After products are listed on Gumroad, update all landing page buy buttons with real Gumroad URLs
- **Needed to start:** Gumroad product URLs
- **Effort:** Quick (update 9 links across HTML files)
- **Machine:** Ceiba
- **Dependencies:** Products listed on Gumroad first

---

## MEDIUM (This Month)

### 16. eBay Listing Agent V2 -- API Auto-Publish
- **What:** Swap manual publisher for eBay API publisher. No more copy-paste.
- **Needed to start:** OAuth flow completion for eBay API
- **Effort:** Medium
- **Machine:** Ceiba
- **Dependencies:** eBay OAuth user token (publisher_v2.py + ebay_oauth_token.py already built)
- **Status:** READY in IDEAS_BACKLOG

### 17. eBay Cross-Reference Engine
- **What:** Cross-reference products across eBay, Amazon for margin calculation
- **Needed to start:** eBay OAuth user token
- **Effort:** Medium
- **Machine:** Ceiba
- **Dependencies:** OAuth flow completed
- **Status:** BLOCKED in IDEAS_BACKLOG

### 18. BehiqueBot Rework -- Phase 1 (Core Fixes)
- **What:** Multi-idea splitter, better thread matching, Notion hydration on startup, persistent bot_data
- **Needed to start:** Kalani review of design doc
- **Effort:** Big (1 full session)
- **Machine:** Ceiba (code), Railway (deploy)
- **Dependencies:** Kalani approves design
- **Design at:** `Ceiba/projects/behiquebot-rework-design.md`
- **Includes:** splitter.py, memory.py rewrite, notion hydration, voice multi-idea

### 19. BehiqueBot Rework -- Phase 2 (Ceiba Bridge + Accountability)
- **What:** Ceiba sync via Notion, accountability scheduler, command system (/ideas, /goals, /summary), clarifying questions
- **Needed to start:** Phase 1 complete, Kalani confirms bridge approach
- **Effort:** Big (1 full session)
- **Machine:** Ceiba + Railway
- **Dependencies:** Phase 1 shipped

### 20. Behike Method / Builder's Blueprint Product
- **What:** Kalani's own version of OPB framework. Digital product ($14.99-$49.99).
- **Needed to start:** Writing time, Kalani's own examples/stories
- **Effort:** Big
- **Machine:** Ceiba
- **Dependencies:** First product sales proving the market
- **Notes at:** `Ceiba/projects/content-empire/opb-framework-notes.md`

### 21. AI Agent Installation -- First Client Outreach
- **What:** DM 10 local businesses, post in Colmena66, create case study content
- **Needed to start:** Landing page (DONE at products/ai-agent-landing.html), Instagram posts
- **Effort:** Medium
- **Machine:** Kalani (outreach), Ceiba (content creation)
- **Dependencies:** Instagram accounts active, case study polished
- **Plan at:** `Ceiba/projects/content-empire/service-offering.md`

### 22. Business Automation Audit Template (Free Lead Magnet)
- **What:** 30-min audit template to identify 3 AI automation opportunities. Door opener for agent installation service.
- **Needed to start:** Template design, landing page
- **Effort:** Medium
- **Machine:** Ceiba
- **Dependencies:** Service offering finalized
- **Status:** FUTURE in IDEAS_BACKLOG

### 23. Lock Down CORS on Chatbot API
- **What:** Once store domain is live, restrict CORS on Cobo chatbot to store domain only
- **Needed to start:** Domain purchased, store deployed
- **Effort:** Quick
- **Machine:** Cobo
- **Dependencies:** Domain + store live

### 24. Solopreneur OS Product
- **What:** Digital product ($12.99) listed in product lineup but no landing page yet
- **Needed to start:** Content creation, landing page build
- **Effort:** Medium
- **Machine:** Ceiba
- **Dependencies:** None
- **Listing draft at:** `Ceiba/projects/content-empire/products/solopreneur-os-listing.md`

---

## LOW (Backlog -- Someday)

### 25. Google Trends Scraper Rebuild
- **What:** Rebuild trends_scraper.py with better rate limiting + proxy rotation. First version worked then got banned.
- **Needed to start:** Webshare proxies (proxies.txt in ~/Downloads), refactored scraper code
- **Effort:** Medium
- **Machine:** Cobo (runs the scraper)
- **Dependencies:** Proxy rotation implementation
- **Original at:** `tools/trends_scraper.py` (banned), also `~/Desktop/trends_automation.py`

### 26. Amazon Scraper with Stealth + Proxies
- **What:** Fix Amazon Playwright scraper (built, selectors broken)
- **Needed to start:** Residential proxies on Cobo
- **Effort:** Medium
- **Machine:** Cobo
- **Dependencies:** proxies.txt copied to Cobo
- **Status:** BLOCKED in IDEAS_BACKLOG

### 27. BehiqueBot Rework -- Phase 3 (Calendar + Reminders)
- **What:** Google Calendar integration, birthday/deadline tracking, morning briefing
- **Needed to start:** Kalani sets up Google Cloud OAuth
- **Effort:** Big (1 session)
- **Machine:** Ceiba + Railway
- **Dependencies:** BehiqueBot Phase 1+2 complete, Google OAuth credentials

### 28. BehiqueBot Rework -- Phase 4 (Habitica Gamification)
- **What:** Habitica API sync, auto-complete tasks, XP/gold tracking, gamified responses
- **Needed to start:** Kalani's Habitica API key + User ID
- **Effort:** Big (1 session)
- **Machine:** Ceiba + Railway
- **Dependencies:** BehiqueBot Phase 1+2 complete, Habitica credentials

### 29. Habitica Spanish Community -- La Ceiba
- **What:** Build the best Spanish-speaking Habitica community with Telegram bot, automation scripts, accountability system
- **Needed to start:** Habitica Premium ($5/mo), founding members (GF + friends), Telegram group
- **Effort:** Big (multi-week project, 4 phases)
- **Machine:** Ceiba (bot code), Railway (hosting), Cobo (n8n workflows)
- **Dependencies:** Revenue flowing first. At least founding members recruited.
- **Full plan at:** `Ceiba/projects/habitica-community-plan.md`
- **Includes:** Telegram bot (@LaCeibaBot), auto-quest scripts, chat bridge, leaderboards, weekly recaps

### 30. Telegram Scraper SaaS
- **What:** Long-term SaaS product. Scrapes product data from Telegram for dropshippers.
- **Needed to start:** Architecture design, scraping infrastructure
- **Effort:** Big (multi-month project)
- **Machine:** Cobo (scraping), Ceiba (frontend)
- **Dependencies:** Revenue from other projects first

### 31. AI Ebook Series
- **What:** Convert 368 course transcripts into ebook series (Gaming KB 120 videos, Claude Code KB 6 videos, others)
- **Needed to start:** Ebook pipeline (tools/ebook_builder.py exists), formatting pass
- **Effort:** Big per book
- **Machine:** Ceiba
- **Dependencies:** First ebook sales proving the market

### 32. Claude Code Mastery Guide
- **What:** Mini-guide from 6 Claude Code course transcripts ($5-9)
- **Needed to start:** Only 6 transcripts, thin content. Needs more material.
- **Effort:** Medium
- **Machine:** Ceiba
- **Dependencies:** Ebook pipeline proven

### 33. VTuber Personal Brand
- **What:** Custom avatar rig (like @theburntpeanut) with face tracking for Kalani's personal content
- **Needed to start:** VSeeFace/Live2D/VMagicMirror, OBS integration, character design
- **Effort:** Big
- **Machine:** Cobo (GPU for tracking)
- **Dependencies:** AI news brand running first
- **Status:** FUTURE in IDEAS_BACKLOG

### 34. Social Anxiety Phone Call Bot
- **What:** AI bot that makes phone calls for people with social anxiety. Books appointments, calls businesses.
- **Needed to start:** Voice AI API (Vapi/Bland.ai/Retell), use case validation
- **Effort:** Big
- **Machine:** Cloud (voice API)
- **Dependencies:** Revenue flowing first
- **Status:** FUTURE in IDEAS_BACKLOG

### 35. AI Pose/Expression Photo App
- **What:** Take photo, AI modifies pose/smile/expression. "Photo coach" mode unique angle.
- **Needed to start:** ControlNet/OpenPose, React Native or PWA, image generation
- **Effort:** Big
- **Machine:** Cobo (GPU for inference)
- **Dependencies:** Nothing. Pure idea stage.
- **Status:** IDEA STAGE in IDEAS_BACKLOG

### 36. n8n AI Agency -- Full Service
- **What:** Selling n8n automation workflows to companies. Now rebranded as "AI Agent Installation Service."
- **Needed to start:** Portfolio of 3+ completed automation projects, client testimonials
- **Effort:** Big (ongoing business)
- **Machine:** Cobo (n8n at 192.168.0.151:5678)
- **Dependencies:** Landing page done. Need first client.
- **Status:** Not started (landing page built, no outreach yet)

### 37. Colmena66 AI Consulting
- **What:** Position as AI consultant for PR startup accelerator ecosystem
- **Needed to start:** Proven portfolio, 3+ automation projects done
- **Effort:** Big
- **Machine:** Kalani (relationship building)
- **Dependencies:** n8n agency has 5+ clients first
- **Status:** Research done, waiting on credibility

### 38. Book-to-Agent System
- **What:** Turn books into interactive AI tutors
- **Needed to start:** Design, revenue flowing
- **Effort:** Big
- **Machine:** Cobo (inference), Ceiba (framework)
- **Dependencies:** Core revenue first

### 39. PR Government AI Consulting
- **What:** AI consulting for Puerto Rico government agencies
- **Needed to start:** Credibility, proven track record
- **Effort:** Big
- **Machine:** Kalani
- **Dependencies:** n8n agency has 5+ clients

### 40. Overnight Autonomous Scraping Pipeline
- **What:** Scheduled scraping that runs while Kalani sleeps. Scrape, score, queue listings.
- **Needed to start:** Reliable scraper (trends scraper rebuild)
- **Effort:** Medium
- **Machine:** Cobo
- **Dependencies:** Trends scraper working first

### 41. Dropship Auto-Lister
- **What:** Scraper to eBay pipeline running 24/7. Workers auto-list from Amazon/Walmart to eBay.
- **Needed to start:** eBay API V2 publisher + product research engine proven end-to-end
- **Effort:** Big
- **Machine:** Cobo
- **Dependencies:** eBay V2 API + working scrapers

### 42. Real Scoring with Margin/Competition Data
- **What:** Upgrade product scoring engine with real eBay margin and competition data
- **Needed to start:** eBay OAuth user token
- **Effort:** Medium
- **Machine:** Ceiba/Cobo
- **Dependencies:** OAuth flow completed

### 43. Product Clustering (Group Variants)
- **What:** Group product variants together in the research engine
- **Needed to start:** Enough products in DB
- **Effort:** Medium
- **Machine:** Cobo
- **Dependencies:** eBay API populates real data

### 44. Walmart Scraper
- **What:** Add Walmart as a source for product research
- **Needed to start:** Core scrapers working first
- **Effort:** Medium
- **Machine:** Cobo
- **Dependencies:** Amazon/eBay pipeline proven

### 45. Real Embeddings for Vault Search
- **What:** Vector embeddings for semantic vault search
- **Needed to start:** Memory ingestion proven with 30+ days of data
- **Effort:** Medium
- **Machine:** Ceiba/Cobo
- **Dependencies:** 30+ days of ingestion data

### 46. AI Price Predictor (ML)
- **What:** ML model to predict product prices from historical scoring data
- **Needed to start:** 90 days of scores in DB
- **Effort:** Big
- **Machine:** Cobo (GPU)
- **Dependencies:** 90 days of scoring data

### 47. Multi-Model Description A/B Testing
- **What:** Test Claude vs ChatGPT vs Ollama product descriptions, measure sales
- **Needed to start:** Working listings + sales data
- **Effort:** Medium
- **Machine:** Ceiba
- **Dependencies:** 10+ eBay listings live

### 48. Tamagotchi Pi Companion Device
- **What:** Physical Raspberry Pi in 3D-printed cube showing quest dashboard
- **Needed to start:** Quest dashboard proven, Pi hardware
- **Effort:** Big
- **Machine:** Dedicated Pi
- **Dependencies:** Dashboard proven first

### 49. Tamagotchi Mobile App
- **What:** React Native or PWA companion app for quest/habit tracking
- **Needed to start:** Pi version working
- **Effort:** Big
- **Machine:** Ceiba
- **Dependencies:** Pi version first

### 50. Pixel Art City Simulator Dashboard
- **What:** Visual city where buildings represent projects
- **Needed to start:** Quest dashboard working
- **Effort:** Big
- **Machine:** Ceiba
- **Dependencies:** Fun project, not priority

### 51. Autonomous Cross-Computer Communication
- **What:** Ceiba autonomously triggers Cobo sessions, controls browser, no human relay
- **Needed to start:** Full agent protocol beyond basic HTTP bridge
- **Effort:** Big
- **Machine:** Ceiba + Cobo
- **Dependencies:** Bridge proven + secure

### 52. Swarm Mode / Worker Spawning
- **What:** Workers can spawn new workers. AI-TASK protocol. Ceiba only supervises.
- **Needed to start:** 3+ working agents
- **Effort:** Big
- **Machine:** All
- **Dependencies:** 3+ proven agents

### 53. OpenClaw as Central Agent Hub
- **What:** Central dispatch for all bots and automation
- **Needed to start:** 5+ agents/skills deployed
- **Effort:** Big
- **Machine:** All
- **Dependencies:** 5+ agents proven

### 54. Digital Twin System
- **What:** Multiple agents handling distinct domains autonomously
- **Needed to start:** Multiple agents proven
- **Effort:** Big
- **Machine:** All
- **Dependencies:** Way down the line

### 55. Viral Vault Scoring Methodology
- **What:** 15-point scoring checklist from Viral Vault adapted for product scoring
- **Needed to start:** Product research engine working
- **Effort:** Medium
- **Machine:** Ceiba/Cobo
- **Dependencies:** eBay API data flowing

### 56. DotCom Secrets + $100M Offers Full Implementation
- **What:** Value ladder, funnel, Hormozi offer framework applied to all products
- **Needed to start:** Strategy documented (DONE), needs execution
- **Effort:** Medium (ongoing)
- **Machine:** Ceiba
- **Dependencies:** Products listed first

### 57. Act 60 Tax Incentives Research
- **What:** PR has tax incentives for service exporters. Worth investigating.
- **Needed to start:** LLC filed, revenue flowing
- **Effort:** Quick (research)
- **Machine:** Kalani
- **Dependencies:** LLC filed, relevant when revenue hits

---

## DONE (Reference -- Already Built)

These are completed. Listed for context so nothing gets rebuilt.

- Product store (13 pages) -- themes/behike-store/landing-pages/
- 3 Shopify themes (Dawn-based) -- themes/behike-*.zip
- Legal filing package (7 documents) -- legal/
- Security audit (27 findings, 4 critical fixed)
- AI news tracker -- tools/ai_news_tracker.py
- Carousel generator -- tools/carousel_generator.py
- News-to-post pipeline -- tools/news_to_post.py
- Text shaper (Robert Greene) -- tools/text_shaper.py
- Reel pipeline (full autonomous) -- tools/reel-pipeline/
- eBay Listing Assistant V1 -- tools/ebay-listing-assistant/
- eBay V2 Publisher (code written, needs OAuth) -- providers/ebay/publisher_v2.py
- Quest Dashboard / Command Hub -- Ceiba/behique-hub.html
- Vault graph tools (grapher, healer, context engine, templates)
- AI Agent Kernel -- tools/ai_agent_kernel/
- CMP (memory protocol) -- tools/ai_agent_kernel/cmp.py
- Morning briefing -- tools/morning_briefing.py
- Session tracker -- tools/session_tracker.py
- Prompt guard -- skills/prompt_guard.py
- BehiqueBot (live on Railway)
- Gumroad account (created 2026-03-22)
- 94 content pieces ready across 4 accounts
- Meditation app -- products/meditation-app.html
- AI Agent Installation landing page -- products/ai-agent-landing.html
- Bio link page -- products/bio-link.html
- Ecommerce Playbook PDF -- ~/behique/ebooks/ecommerce-playbook.pdf (OLD, replaced by v2)
- Gumroad bundle files -- Ceiba/projects/content-empire/gumroad-bundle/

### Session 20 Completions (2026-03-21):
- AI Employee Guide PDF converted -- products/ai-employee-guide.pdf
- AI Employee Guide genericized + polished -- 8,825 words, step-by-step, troubleshooting
- Ecommerce Playbook v2 REWRITTEN -- products/ecommerce-playbook-v2.pdf (100% original, 7,816 words)
- Behike Method guide + landing page -- products/behike-method.pdf (5,303 words, 6 chapters)
- Solopreneur OS landing page -- landing-pages/solopreneur-os.html
- Automation Audit Template (free lead magnet) -- products/automation-audit-template.html
- Landing Page Template product (packaged) -- products/landing-page-template.zip
- 9 product cover images -- products/cover-images.html
- Upsells implemented on all 4 main pages (value stacks, PAS, bundles, exit popups)
- Homepage updated with all new products + free audit section
- Hutia rebuild plan -- Ceiba/HUTIA_REBUILD_PLAN.md
- Session log -- Ceiba/SESSION_LOG_2026-03-21.md
- Agent monitor dashboard -- Ceiba/faces/agent-monitor.html
- Business structure plan -- legal/BUSINESS_STRUCTURE_PLAN.md
- Conversion strategy doc -- content-empire/conversion-strategy.md
- Gumroad setup checklist -- content-empire/gumroad-setup-checklist.md
- YouTuber outreach bot idea captured in IDEAS_BACKLOG

---

## QUICK REFERENCE: What Runs Where

| Machine | IP | Role | Key Services |
|---------|-----|------|-------------|
| Ceiba (Mac M4) | 192.168.0.145 | HQ, all tools | Claude Code, Python tools, reel pipeline |
| Cobo (Windows, GTX 1080 Ti) | 192.168.0.151 | GPU inference, bridge | Ollama, n8n, bridge:9876, chatbot:9877 (pending) |
| Hutia (Comp3) | 192.168.0.152 | Always-on store host | Product store, deploy target |

---

*This file is the single source of truth for what needs to happen. Update it when tasks complete or new ones emerge. Check it at session start.*

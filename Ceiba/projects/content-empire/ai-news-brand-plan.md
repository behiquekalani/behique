# Content Empire -- Multi-Page Brand Strategy
# Created: 2026-03-20
# Vision: 4-5 automated Instagram pages, each a revenue funnel

---

## The Empire (Full Map)

```
+---------------------+     +---------------------+
|  AI NEWS (EN)       |     |  AI NEWS (ES)       |
|  Daily news/tools   |     |  Same, translated   |
|  Sponsors/affiliates|     |  Underserved market  |
+---------------------+     +---------------------+
          |                           |
          +--- Cross-promote ---------+
          |                           |
+---------------------+     +---------------------+
|  STORIES (EN)       |     |  STORIES (ES)       |
|  Emotional reels    |     |  Same, translated   |
|  Fully automated    |     |  26 reels READY     |
|  52 reels banked    |     |  Automated pipeline |
+---------------------+     +---------------------+
          |                           |
          +------ All funnel to ------+
          |                           |
+---------------------------------------------+
|          GUMROAD PRODUCTS ($$$)              |
|  Budget Template | Cash Flow | Ebook |       |
|  Meditation App | AI Employee Guide          |
|  AI Agent Service ($500-$5K)                 |
+---------------------------------------------+
          |
          v
+---------------------------------------------+
|     VTUBER / PERSONAL BRAND (ENDGAME)        |
|  Kalani's face, unifying brand               |
|  Connects all pages under one identity       |
|  YouTube long-form, collabs, sponsorships    |
+---------------------------------------------+
```

---

## Page 1: AI News (EN)
- **Handle:** [TBD - Kalani picks]
- **Content:** AI news carousels, tool reviews, breaking announcements, GTC recaps
- **Posting:** 1-2 posts/day (news tracker auto-feeds content)
- **Revenue:** Affiliate links to AI tools, sponsorships, newsletter upsell
- **Automation level:** Semi-auto. News tracker finds stories, post generator writes captions. Kalani adds hot takes.
- **Tools:** ai_news_tracker.py, news_to_post.py, boardroom.py for review

## Page 2: AI News (ES)
- **Handle:** [TBD]
- **Content:** Same stories, translated to Spanish
- **Posting:** 1-2 posts/day, 2-4 hours after EN post
- **Revenue:** Same model, Spanish-speaking market
- **Automation level:** High. translate_stories.py already works. Ollama handles translation.
- **Edge:** Almost nobody does quality AI news in Spanish. Massive gap.

## Page 3: Emotional Stories (EN)
- **Handle:** [TBD]
- **Content:** Nostalgia reels (52 banked), pet peeve reels (5 new, more coming), relatable content
- **Posting:** 2 reels/day per the posting calendar
- **Revenue:** Viral growth -> link-in-bio -> Gumroad products. Brand deals once 10K+.
- **Automation level:** FULL. Pipeline produces reels end-to-end. Kokoro TTS, Ken Burns, animated captions. $0 cost.
- **Bank:** 52 reels ready NOW. 5 pet peeve stories ready for production. Pipeline can produce more indefinitely.

## Page 4: Emotional Stories (ES)
- **Handle:** [TBD]
- **Content:** Same reels, Spanish narration
- **Posting:** 2 reels/day, offset from EN
- **Revenue:** Same funnel, Latin American market
- **Automation level:** FULL. 26 ES reels already produced. Pipeline auto-translates + generates TTS.
- **Edge:** Emotional content is universal. Spanish-speaking audience is 500M+ people.

## Page 5: VTuber / Personal Brand (ENDGAME)
- **Handle:** Kalani's personal brand
- **Content:** Face-tracked avatar, AI commentary, tool demos, collabs
- **Revenue:** YouTube monetization, sponsorships, course sales
- **Timeline:** After pages 1-4 are running and growing
- **Tech:** VTube Studio + iPhone ARKit + custom Live2D model

---

## Revenue Model Per Page

| Page | Month 1-3 | Month 3-6 | Month 6-12 |
|------|-----------|-----------|------------|
| AI News EN | Affiliate links ($50-200/mo) | Sponsors ($500-2K/mo) | Premium newsletter ($1K+/mo) |
| AI News ES | Affiliate ($20-100/mo) | Sponsors ($200-500/mo) | Newsletter ES ($500+/mo) |
| Stories EN | Gumroad sales ($50-200/mo) | Brand deals ($500+/mo) | Merch/products ($1K+/mo) |
| Stories ES | Gumroad ($20-100/mo) | Brand deals ($200+/mo) | Products ($500+/mo) |
| VTuber | -- | -- | YouTube + sponsors ($2K+/mo) |
| **TOTAL** | **$140-600/mo** | **$1,400-4K/mo** | **$5K-15K/mo** |

Conservative estimates. One viral reel can 10x any of these numbers overnight.

---

## Cross-Promotion Strategy

- AI News posts: "Follow @stories for the human side of tech"
- Stories posts: "Follow @ainews for daily AI updates"
- All pages: Link-in-bio to Gumroad product page
- All pages: "Same content in Spanish at @handle_es"
- VTuber (later): Unifies all brands under Kalani's face

---

## What's Already Built

| Asset | Status | Location |
|-------|--------|----------|
| News tracker (18 feeds, impact scoring) | LIVE | tools/ai_news_tracker.py |
| News-to-post generator | LIVE | tools/news_to_post.py |
| Reel pipeline (TTS + compose) | LIVE | tools/reel-pipeline/ |
| 52 reels (26 EN + 26 ES) | DONE | tools/reel-pipeline/output/ |
| 5 pet peeve stories | READY | tools/reel-pipeline/stories/ |
| Story translation pipeline | LIVE | tools/reel-pipeline/translate_stories.py |
| Posting calendar | DONE | content-empire/posting-calendar.md |
| Gumroad products (5) | READY | content-empire/gumroad-bundle.zip |
| Landing page (AI service) | DONE | products/ai-agent-landing.html |
| VTuber setup guide | DONE | content-empire/vtuber-setup-guide.md |
| Boardroom review tool | LIVE | tools/boardroom.py |

---

## What Kalani Needs To Do

1. **Pick 4 Instagram handles** (EN news, ES news, EN stories, ES stories)
2. **Create 4 Instagram accounts**
3. **List 5 products on Gumroad** (zip + guide ready)
4. **Set up BotFather token** for Telegram Channels
5. **Regenerate FAL_KEY** for AI video
6. **Start posting** -- Day 1 content is ready

Everything else is automated or built. The machine is ready. It just needs someone to turn the key.

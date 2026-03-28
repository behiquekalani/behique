---
title: "YouTube Strategy - Faceless AI Channels + Main Channel"
type: strategy
tags: [youtube, faceless, ai-video, automation, revenue, distribution]
created: 2026-03-22
priority: HIGH
---

# YouTube Strategy
# Two approaches: Main channel (face) + Faceless AI channels (automated revenue)

---

## THE PLAY

YouTube is long-term passive income. Instagram and TikTok drive awareness. YouTube drives revenue. AdSense alone can pay the bills with the right niches. Plus, YouTube videos rank on Google forever. A video posted today can generate views and revenue for years.

Two tracks:
1. **Main channel (Behike):** Face/screen content about AI, automation, building. Authority channel.
2. **Faceless channels (1-3):** Fully AI-generated content in high-CPM niches. Automated revenue.

---

## TRACK 1: MAIN CHANNEL (Behike)

### Channel Identity
- **Name:** Behike (or Behike AI)
- **Niche:** AI automation, building AI systems, tech for solopreneurs
- **Format:** Screen recordings + voiceover (no need to show face initially)
- **Upload frequency:** 1-2 videos/week
- **Monetization:** AdSense + product sales + service leads

### Content Types

**Type A: Tutorials (70% of content)**
- "How to build an AI agent that works 24/7"
- "How to set up n8n for free workflow automation"
- "How to run AI locally with Ollama (no API costs)"
- "How to secure your AI tools (prompt injection defense)"
- These rank on YouTube search. Evergreen traffic.

**Type B: Build-in-Public (20%)**
- "I built 5 digital products in one weekend"
- "Watch me automate my entire content pipeline"
- "Day in the life: running a business with 6 AI agents"
- These build audience and drive engagement.

**Type C: Opinions/Hot Takes (10%)**
- "Why most AI tools are a waste of money"
- "The AI security crisis nobody is talking about"
- These go viral and attract new viewers.

### Video Formula (Hook, Content, CTA)
1. **Hook (0-10 seconds):** Bold claim or question. "Most people using AI are wasting 90% of its potential. Here's why."
2. **Content (2-15 minutes):** Deliver massive value. Screen recordings, demonstrations, step-by-step.
3. **CTA (last 30 seconds):** "Free AI safety checklist in the description. And if you want the full guide, the link is there too."

### SEO Strategy
- Title: Include primary keyword ("how to" + topic)
- Thumbnail: Bold text, high contrast, one visual element
- Description: First 2 lines are the hook. Include links to products. Full keyword list.
- Tags: 15-20 relevant tags per video
- Chapters: Add timestamps for every section

### Content Pipeline (reuse everything)
- Every tutorial = 1 blog post for SEO
- Every tutorial = 3-5 TikTok/Reel clips
- Every tutorial = 1 X/Twitter thread
- Every tutorial = 1 newsletter section
- One long video feeds the entire content ecosystem

---

## TRACK 2: FACELESS AI CHANNELS (Automated Revenue)

### How Faceless Channels Work
- AI generates scripts (Claude/ChatGPT)
- AI generates voiceover (Kokoro TTS, ElevenLabs, or Play.ht)
- AI generates visuals (Stable Diffusion, Midjourney, stock footage)
- AI generates thumbnails
- Human reviews, approves, uploads (or automate upload too)
- Revenue: YouTube AdSense ($5-30 CPM depending on niche)

### High-CPM Niche Options

| Niche | CPM Range | Competition | Content Source | Difficulty |
|-------|-----------|-------------|----------------|------------|
| Personal Finance | $15-30 | High | Our budget/cash flow products | Medium |
| AI/Tech News | $8-15 | Medium | AI Journal + web research | Easy |
| Business/Entrepreneurship | $10-25 | High | Our content library | Medium |
| Psychology/Self-Improvement | $8-20 | Medium | BehiqueBot framework | Medium |
| Scary Stories/Mystery | $5-12 | Low | AI-generated | Easy |
| History/Education | $8-18 | Medium | Research-based | Medium |

### Recommended Faceless Channel #1: AI/Tech News

**Why:** We already track AI news. Low effort to convert into videos. Medium CPM but growing audience.

**Channel name ideas:** AI Decoded, The AI Brief, Tech Pulse, Binary Beat

**Video format:**
- 5-8 minute videos
- AI-generated voiceover (Kokoro TTS, already set up)
- Stock footage + AI-generated images + screen recordings
- Upload 3-5 videos/week

**Revenue math:**
- 3 videos/week x 4 weeks = 12 videos/month
- Average 5,000 views/video after 3 months = 60,000 views/month
- $10 CPM = $600/month from ONE channel
- At 20,000 views/video = $2,400/month

### Recommended Faceless Channel #2: Personal Finance

**Why:** Highest CPM niche. We have the products (budget template, cash flow dashboard). Content feeds product sales.

**Channel name ideas:** Money Decoded, Dollar Logic, Finance in Five, The Cash Stack

**Video format:**
- 5-10 minute videos
- Topics: budgeting tips, saving strategies, side hustle ideas, debt payoff methods
- Include mentions of our tools/templates
- Upload 2-3 videos/week

**Revenue math:**
- 2 videos/week x 4 weeks = 8 videos/month
- Average 10,000 views/video = 80,000 views/month
- $20 CPM = $1,600/month
- Plus product sales driven by video CTAs

### Recommended Faceless Channel #3: AI Security/Cybersecurity

**Why:** Fear sells. Growing concern. We have the authority (security guide, safety checklist). Very low competition for AI-specific security content.

**Channel name ideas:** AI Shield, Secure AI, The AI Firewall, Digital Armor

**Video format:**
- 5-8 minute videos
- Topics: AI security threats, prompt injection explained, how to protect your data
- Feeds directly into our security product funnel
- Upload 2-3 videos/week

**Revenue math:**
- 2 videos/week = 8 videos/month
- 5,000 views/video = 40,000 views/month
- $12 CPM = $480/month
- Plus security guide sales

---

## FACELESS VIDEO PRODUCTION PIPELINE

### Tools (all free or already have)

| Step | Tool | Cost |
|------|------|------|
| Script | Claude Code / ChatGPT | $0 (included) |
| Voiceover | Kokoro TTS (already installed) | $0 |
| Images | MLX Stable Diffusion (already set up) | $0 |
| Stock footage | Pexels, Pixabay (free) | $0 |
| Editing | FFmpeg + Python (automated) | $0 |
| Thumbnails | Canva (free tier) or AI-generated | $0 |
| Upload | YouTube Studio | $0 |

### Automated Pipeline Architecture

```
[Script Generator]
     |
     v
[Kokoro TTS] --> narration.wav
     |
     v
[Image Generator] --> scene images
     |
     v
[Video Assembler (FFmpeg)] --> final.mp4
     |
     v
[Thumbnail Generator] --> thumb.jpg
     |
     v
[Review Queue] --> Human approves
     |
     v
[YouTube Upload] --> Published
```

This is basically our reel pipeline (tools/reel-pipeline/make_reel.py) extended for longer videos. The architecture already exists. It just needs to be scaled.

### Production Time Per Video
- Script: 10-15 minutes (AI generates, human reviews)
- Voiceover: 2-3 minutes (automated)
- Images: 5-10 minutes (automated, may need curation)
- Assembly: 3-5 minutes (automated)
- Thumbnail: 5 minutes (Canva)
- Review + upload: 10 minutes (human)
- **Total: ~35-45 minutes per video**

At 3 videos/week per channel, that's about 2 hours/week per channel.

---

## YOUTUBE MONETIZATION REQUIREMENTS

### YouTube Partner Program:
- 1,000 subscribers
- 4,000 watch hours in last 12 months (long-form) OR 10M Shorts views in 90 days
- Clean channel (no strikes)
- Typically takes 2-6 months to reach

### Revenue Streams Beyond AdSense:
1. **Product links in description** - every video links to relevant Gumroad products
2. **Affiliate marketing** - recommend tools we actually use (n8n, Ollama, hosting providers)
3. **Service leads** - "DM me for a free AI audit" in every video
4. **Sponsorships** - once channel grows, AI tools will pay for mentions
5. **Course upsell** - eventually, a premium course ($97-297)

---

## IMPLEMENTATION ROADMAP

### Phase 1: Main Channel Launch (Week 1-2)
- [ ] Create YouTube channel "Behike" or "Behike AI"
- [ ] Channel art and branding (Canva)
- [ ] Record first 3 tutorials (screen recording + voiceover)
- [ ] Upload and optimize (titles, descriptions, tags, thumbnails)

### Phase 2: Faceless Channel #1 (Week 2-4)
- [ ] Create AI/Tech News channel
- [ ] Adapt reel pipeline for 5-8 minute videos
- [ ] Generate first 5 scripts
- [ ] Produce and upload first 5 videos
- [ ] Target: 3 videos/week cadence

### Phase 3: Scale (Month 2-3)
- [ ] Launch Faceless Channel #2 (Personal Finance)
- [ ] Main channel hitting weekly uploads consistently
- [ ] Optimize based on analytics (what topics get views?)
- [ ] Start cross-promoting between channels

### Phase 4: Monetization (Month 3-6)
- [ ] Apply for YouTube Partner Program on all channels
- [ ] Add affiliate links to descriptions
- [ ] Start reaching out for sponsorships on main channel
- [ ] Product sales attribution tracking

---

## COMBINED PLATFORM REVENUE PROJECTION (Month 6)

| Platform | Revenue Source | Monthly |
|----------|---------------|---------|
| YouTube Main (Behike) | AdSense + product links | $200-500 |
| YouTube Faceless #1 (AI News) | AdSense | $400-800 |
| YouTube Faceless #2 (Finance) | AdSense + product links | $800-1,600 |
| Instagram | Product sales + service leads | $200-500 |
| TikTok | Creator fund + product links | $50-200 |
| Gumroad (direct) | Product sales | $300-600 |
| Service clients | AI installation | $500-2,000 |
| **Total** | | **$2,450-6,200/mo** |

This is conservative and assumes consistent output. The faceless channels compound. Every video is a permanent revenue asset.

---

## KEY INSIGHT

YouTube is the only platform where your content gets MORE valuable over time. Instagram posts die after 48 hours. TikToks die after a week. YouTube videos get recommended for YEARS.

A library of 100 YouTube videos is a business asset. A library of 100 Instagram posts is history.

Build the library.

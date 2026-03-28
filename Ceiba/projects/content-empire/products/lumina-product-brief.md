# Lumina Product Brief
# Copyright 2026 Behike. All rights reserved.
# Confidential. Do not distribute.

---

## Product Overview

**Name:** Lumina
**Tagline:** Your screen, working with your body. Not against it.
**Category:** Circadian wellness / productivity software
**Price:** Free tier + $9.99 one-time Pro upgrade

**Positioning:** Lumina is the modern replacement for f.lux and Night Shift. It combines blue light filtering with ambient sound, ADHD focus tools, sleep coaching, breathing exercises, and adaptive scheduling into a single app. No subscriptions. One purchase, everything included.

---

## Competitive Analysis

### f.lux
- Founded 2008. Donation-funded. Development has stalled.
- Does one thing well: blue light filtering with location awareness.
- No sound, no focus mode, no sleep coaching, no breathing.
- Free. No business model to sustain development.
- Legacy UI. Feels dated on modern macOS.

### Night Shift (Apple)
- Built into macOS. Basic warm color filter.
- No location intelligence beyond simple sunset/sunrise.
- No additional wellness features.
- Cannot be extended or customized.
- Exists so Apple can check a box, not solve a problem.

### Iris
- Paid blue light filter ($15 lifetime or subscription).
- More features than f.lux but cluttered UI.
- No sound, no focus mode, no breathing exercises.
- Cross-platform but Windows-first, Mac support is secondary.
- Pricing is confusing (multiple tiers, subscriptions, lifetime).

### Twilight (Android only)
- Mobile-only. Not a competitor on desktop.
- Free with ads, Pro removes ads.
- Only does blue light filtering.
- Relevant only if Lumina ever expands to mobile.

### Standalone alternatives (what people cobble together)
- Noisli / myNoise for ambient sound ($10/yr subscription each)
- Focus Keeper / Flow for Pomodoro ($5-7)
- Sleep Cycle for sleep tracking ($40/yr)
- Breathe+ or Calm for breathing ($70/yr for Calm)
- Total cost: $100+/yr for fragmented tools that do not talk to each other.

### Lumina's edge
Nobody combines light + sound + focus + sleep + breathing in one app. The market is fragmented. Users cobble together 3-5 apps. Lumina replaces all of them with one $9.99 purchase.

---

## Feature Breakdown

### Free Tier
- Blue light filter with automatic color temperature adjustment
- Location-based sunrise/sunset scheduling
- 1 ambient soundscape (rain)
- Basic smart schedule

### Pro Tier ($9.99 one-time)
- Everything in Free
- 6 ambient soundscapes (rain, ocean, forest, fireplace, cafe, white noise)
- Soundscape layering (mix any combination)
- ADHD Focus Mode (Pomodoro timer + screen dimming + session tracking)
- Sleep Coach (bedtime calculator, wind-down mode, consistency tracking)
- Breathing exercises (4-7-8 sleep, box breathing, calm breathing)
- Adaptive smart schedule (learns your patterns over time)
- Session tracking and analytics dashboard
- All future updates included

---

## Pricing Strategy and Rationale

**Model:** Freemium with one-time Pro upgrade.

**Why $9.99:**
- Low enough to be an impulse buy. No deliberation needed.
- High enough to signal quality. Not a throwaway free tool.
- One-time payment removes subscription fatigue, which is a growing user complaint across the wellness app market.
- Undercuts Iris ($15), massively undercuts Calm ($70/yr), and replaces $100+/yr in fragmented tools.
- Psychological anchor: the value stack on the landing page shows $100+ in standalone tools. $9.99 feels like a steal.

**Why not subscription:**
- Behike's brand is anti-subscription for one-time-use tools. Subscriptions are for services that deliver ongoing value (SaaS, data feeds). A desktop app that runs locally does not need a subscription.
- One-time pricing builds trust and word of mouth. "I paid $10 once and it replaced five apps" is a powerful referral sentence.

**Why free tier exists:**
- Lowers the barrier to trying Lumina. No credit card, no commitment.
- The free tier is genuinely useful (blue light filter + 1 sound). Not crippled.
- Pro features are visible but locked, creating natural upgrade desire.
- Free users become advocates even if they never upgrade.

---

## Revenue Projections

### Conservative (Year 1)
- 500 Pro purchases at $9.99 = $4,995
- Assumes organic growth only, no paid ads, limited content marketing
- Break-even on development time within 6 months

### Moderate (Year 1)
- 2,000 Pro purchases at $9.99 = $19,980
- Assumes 5 content pieces driving traffic, Product Hunt launch, Reddit/HN exposure
- 10,000 free downloads with 20% conversion to Pro

### Aggressive (Year 1)
- 8,000 Pro purchases at $9.99 = $79,920
- Assumes viral content hit, featured on Product Hunt, Mac App Store feature
- 50,000 free downloads with 16% conversion to Pro
- Partnership with 2-3 productivity YouTubers

### Long-term (Year 2-3)
- Mac App Store listing adds passive discovery channel
- Windows version doubles addressable market
- Potential for Lumina Teams (workplace wellness, per-seat pricing)

---

## Distribution

### Phase 1: Direct Download (NOW)
- Download from behike.com/lumina
- Landing page handles all conversion
- Payment through Gumroad or Behike's own checkout
- No middleman fees beyond payment processing

### Phase 2: Mac App Store (3-6 months)
- Submit to Mac App Store for passive discovery
- Apple takes 30% cut (net $6.99 per sale)
- Worth it for visibility and trust signal
- Keep direct download as primary to preserve margin

### Phase 3: Windows + Expansion (6-12 months)
- Windows version expands TAM significantly
- Consider Microsoft Store listing
- Potential Chrome extension for web-only version

---

## Marketing Plan: 5 Launch Content Pieces

### 1. "Why I Stopped Using f.lux" (Long-form article)
- Platform: Behike blog, cross-posted to Medium and Dev.to
- Angle: Personal story. What f.lux got right in 2008 and why it is not enough in 2026.
- CTA: Download Lumina Free at the end.

### 2. Product Hunt Launch Post
- Platform: Product Hunt
- Tagline: "f.lux was built in 2008. Your MacBook was not."
- Ship with screenshots, demo GIF, and maker story.
- Target: Top 5 Product of the Day.

### 3. "5 Apps You Can Delete After Installing Lumina" (Short-form video)
- Platform: Instagram Reels, TikTok, YouTube Shorts
- Format: Screen recording showing the 5 apps, then deleting them, then opening Lumina.
- 30-60 seconds. Quick, visual, shareable.

### 4. "The $200/yr Wellness App Stack vs. $9.99" (Comparison graphic)
- Platform: Twitter/X, LinkedIn, Instagram carousel
- Format: Side-by-side comparison. 5 app icons + prices vs. Lumina icon + $9.99.
- Simple, visual, screenshot-worthy.

### 5. Reddit/HN Launch Thread
- Platform: r/macapps, r/productivity, r/ADHD, Hacker News
- Format: Show HN post. Honest, technical, no hype.
- Angle: "I built a modern f.lux replacement that also does focus + sleep + sound"
- Important: Reddit hates self-promotion. Lead with value, link at the end.

---

## Technical Roadmap

### NOW: Web Prototype
- HTML/CSS/JS landing page (done)
- Browser-based demo of core features
- CSS color overlay filter as proof of concept
- Web Audio API for soundscapes
- Validates the concept before native development

### SOON: Electron App (1-3 months)
- Full desktop app using Electron
- System tray integration
- Actual screen color temperature control
- Local storage for settings and session data
- Auto-launch on login
- Works on macOS and Windows from day one

### LATER: Native Swift App (3-6 months)
- Native macOS app for best performance and battery life
- CoreGraphics for color temperature
- Menu bar integration
- System notification support
- Smaller binary, faster launch, lower memory
- Required for Mac App Store submission

### FUTURE: Expansion
- Windows native (C# / WinUI)
- iOS companion app (sync settings, mobile breathing exercises)
- API for integration with other tools (n8n, Shortcuts)
- Lumina Teams (workplace wellness dashboard)

---

## How Lumina Fits Into the Behike Product Ecosystem

Lumina is a **standalone product** in the Behike digital product lineup. It sits alongside the content products (ebooks, templates, courses) but is the first piece of actual software.

**Strategic value:**
- Proves Behike can ship software, not just content. This changes the brand perception.
- Recurring visibility. Unlike an ebook that is bought once and forgotten, an app lives in the menu bar. Daily brand exposure.
- Opens the door for more Behike software products (the app becomes a proof point for investors, partners, and customers).
- Cross-sells naturally. Lumina users see the Behike brand daily, which feeds into other product launches.
- ADHD Focus Mode connects to the BehiqueBot accountability framework, creating potential for integration between products.

**Brand alignment:**
- Behike's core thesis: tools that respect the user. No subscriptions for things that should be owned. No dark patterns. No data harvesting.
- Lumina embodies this. One price, everything included, your data stays local.
- The anti-subscription model is a differentiator in a market drowning in $9.99/month wellness apps.

---

## Open Questions

1. Should the free tier include the Pomodoro timer (without tracking) to increase stickiness?
2. Is $9.99 too low? Could $14.99 work without hurting conversion?
3. Should Lumina have its own domain (getlumina.app) or live under behike.com?
4. When to start the Electron build vs. continuing to validate with the web prototype?
5. Should there be an affiliate/referral program from day one?

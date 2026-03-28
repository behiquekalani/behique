# VTuber Rig Setup Guide - Solo Creator Edition

> For AI news content creation on Mac M4 (primary) + Windows GTX 1080 Ti (secondary).
> Last updated: 2026-03-20

---

## Table of Contents

1. [Quick Start Path (Get Running in 1 Day)](#quick-start-path)
2. [Face Tracking Software](#face-tracking-software)
3. [Creating Your Avatar](#creating-your-avatar)
4. [OBS Integration](#obs-integration)
5. [Face Expression Mapping](#face-expression-mapping)
6. [Custom Animations](#custom-animations)
7. [What Popular VTubers Use](#what-popular-vtubers-use)
8. [Recommended Setup for AI News Content](#recommended-setup)
9. [Budget Breakdown](#budget-breakdown)
10. [Sources](#sources)

---

## Quick Start Path

If you want to be recording with a VTuber avatar TODAY, here is the fastest route:

1. Download **VTube Studio** (free on Steam, works on Mac)
2. Use a **pre-made Live2D model** from Booth or nizima ($0-50)
3. Use your **iPhone as the face tracker** (way better than webcam)
4. Capture in **OBS** via Game Capture or Virtual Camera
5. Record your first AI news segment

Total cost: $0-50. Total setup time: 1-3 hours.

For a custom look that becomes your brand, keep reading.

---

## Face Tracking Software

### Tier 1: Free, Mac-Compatible (Start Here)

#### VTube Studio (RECOMMENDED)
- **Platform:** macOS, Windows, iOS, Android
- **Cost:** Free on Steam (small watermark). Pro DLC removes it for $14.99 (goes on sale for ~$7.49)
- **Avatar type:** Live2D models only (2D)
- **Tracking:** Webcam (via OpenSeeFace) OR iPhone/Android as tracker
- **Why this one:** Most popular VTuber software. Native Mac support. Best Live2D integration. Huge community, tons of tutorials.
- **Install:** Steam > Search "VTube Studio" > Install

**Mac-specific notes:**
- Runs natively on Apple Silicon (M1/M2/M3/M4)
- iPhone tracking via ARKit gives dramatically better results than webcam
- Connect iPhone and Mac on same WiFi network, install VTube Studio on both

#### nizima LIVE
- **Platform:** macOS, Windows
- **Cost:** Free plan available
- **Avatar type:** Live2D models
- **Tracking:** Webcam or iPhone (via nizima LIVE Tracker app)
- **Why consider it:** Made by the Live2D company themselves. Clean interface. Good alternative if VTube Studio gives you issues.
- **Install:** https://nizimalive.com/en/

#### VRoid Studio (for 3D models)
- **Platform:** macOS, Windows (also on Steam)
- **Cost:** Completely free
- **What it does:** Creates 3D anime-style avatars (VRM format). This is a model CREATOR, not a tracker.
- **Why it matters:** If you want 3D instead of 2D, this is how you make the model for free.
- **Install:** https://vroid.com/en/studio or Steam

### Tier 2: Free, Windows Only (Use on Cobo)

#### VSeeFace
- **Platform:** Windows only
- **Cost:** Free
- **Avatar type:** 3D models (VRM format). Does NOT support Live2D.
- **Tracking:** Webcam-based, surprisingly good quality
- **Why consider it:** Best free option for 3D VTuber avatars on Windows. Extremely customizable.
- **Use case:** If you go 3D route, run this on the Windows machine with the GTX 1080 Ti.
- **Install:** https://www.vseeface.icu/

#### VMagicMirror
- **Platform:** Windows only
- **Cost:** Free
- **Avatar type:** 3D (VRM)
- **Special feature:** Can track keyboard/mouse input and show your avatar "typing" or "gaming"
- **Good for:** Showing your avatar at a desk doing AI news, reacting to content

### Tier 3: Paid Options (Worth It Later)

#### Stream Fog
- **Cost:** Subscription-based
- **What it does:** AR-powered VTuber avatars, 100+ pre-made avatars, easy OBS integration
- **Why it matters:** This is what TheBurntPeanut uses. Very polished, very fast setup.
- **Best for:** When you want maximum production quality with minimum effort

#### Live3D VTuber Maker
- **Cost:** Free tier + paid plans
- **Platform:** Windows
- **What it does:** All-in-one VTuber creation and tracking

---

## Creating Your Avatar

You have 4 paths, from cheapest to most custom.

### Path 1: Use a Pre-Made Model ($0-50)

**Where to find them:**
- **Booth.pm** - Largest marketplace for VTuber models. Many free ones. Japanese site but navigable. https://booth.pm/en/browse/VTuber
- **nizima** - Official Live2D marketplace. Curated quality. https://nizima.com/en/
- **Gumroad** - Indie creators sell models here, $10-100 range
- **VTuber.gg** - Marketplace for VTuber commissions and pre-made models

**Pros:** Instant. Cheap. Good enough to start.
**Cons:** Not unique. Other people might use the same model.

### Path 2: Create a Free 3D Model with VRoid Studio ($0)

**Process:**
1. Download VRoid Studio (free, works on Mac)
2. Use the character creator interface (similar to a video game character creator)
3. Customize face, hair, body, clothing
4. Export as .vrm file
5. Load into VSeeFace (Windows) or convert for use in VTube Studio

**Pros:** Free. Unique. Full control over design.
**Cons:** 3D anime style only. Learning curve of a few hours. Limited to the VRoid art style.

### Path 3: Create a Custom Live2D Model (DIY)

This is the process for a fully custom 2D avatar. It has two phases: art and rigging.

#### Phase 1: Draw the Character Art

**Tools needed:**
- Drawing software: Clip Studio Paint ($50 one-time, industry standard), Krita (free), Photoshop, or Procreate (iPad)
- Drawing tablet recommended but not required

**Process:**
1. Draw your character in a front-facing pose
2. Separate EVERY movable part into its own layer:
   - Head, hair front, hair back, hair sides
   - Left eye, right eye, left eyebrow, right eyebrow
   - Mouth (multiple shapes), nose
   - Upper body, lower body, arms, hands
   - Clothing pieces (each separate)
3. Export as a layered PSD file
4. Typical layer count: 30-80+ layers for a good model

**If you cannot draw:** Use AI art generation to create the base design, then manually separate layers in Photoshop/Krita. This works but requires cleanup.

#### Phase 2: Rig the Model in Live2D Cubism

**Software: Live2D Cubism Editor**
- **Free version:** Limited to 1 texture atlas (1024x1024), limited parameters. Enough for a basic model.
- **Pro trial:** 42 days of full Pro features. Use this to learn.
- **Pro subscription (Indie):** ~$47/year (for creators earning under ~$67K/year). Worth it if you commit.
- **Student discount:** 76% off a 3-year Pro subscription if you have a .edu email.
- **Download:** https://www.live2d.com/en/cubism/download/editor/

**Rigging process (simplified):**
1. Import the PSD into Cubism Editor
2. Create mesh deformers for each part
3. Set up parameters: eye open/close, mouth shapes, head rotation X/Y/Z, body sway
4. Add physics (hair bounce, accessory jiggle)
5. Export as .moc3 file
6. Load into VTube Studio

**Time investment:** 20-60 hours to learn and create your first model. Seriously.

**Tutorials to follow:**
- Live2D official tutorials: https://docs.live2d.com/en/cubism-editor-tutorials/
- YouTube: Brian Tsui's Live2D rigging series
- YouTube: Khyleri's beginner Live2D tutorials

### Path 4: Commission a Custom Model ($50-5000+)

**Price ranges for Live2D models (2025-2026):**

| Tier | Price Range | What You Get |
|------|-------------|--------------|
| Budget (Fiverr) | $15-200 | Basic bust-up, limited expressions, simple rigging |
| Mid-tier | $300-800 | Half/full body, good expressions, decent physics |
| Professional | $1,000-2,500 | Full body, advanced rigging, multiple outfits, toggle accessories |
| Premium | $3,000-5,000+ | Everything above + custom animations, complex physics, commercial license |

**Where to commission:**
- **Fiverr** - Widest price range, check portfolios carefully. Search "Live2D VTuber model"
- **Twitter/X** - Search #Live2Dcommission or #VTuberCommission. Best artists post here.
- **Skeb** - Japanese commission platform, high quality
- **VTuber.gg** - Dedicated VTuber commission marketplace
- **nizima** - Can find artists through the official Live2D marketplace

**What to ask for:**
- Half-body or full-body (half-body is cheaper and fine for news content)
- Number of expressions/toggles (surprised, angry, happy, glasses on/off, etc.)
- Idle animation included?
- Physics (hair, accessories)
- Commercial use license (important if you monetize)

**Recommended starting point:** A $200-500 Fiverr commission gets you something unique and solid. Ask to see their previous work. Make sure they deliver the .moc3 file AND the source PSD.

---

## OBS Integration

### Method 1: Game Capture (Mac - Recommended)

This captures the VTube Studio window directly with transparency.

1. Open VTube Studio, load your model
2. In VTube Studio: click background settings, select "ColorPicker", enable "Transparent (OBS)"
3. In OBS: Add Source > Game Capture (Syphon on Mac) > Select VTube Studio
4. The avatar appears with a transparent background, overlay it on your content

**Mac-specific:** On macOS, use "macOS Screen Capture" or "Syphon Client" source in OBS instead of Game Capture.

### Method 2: Virtual Camera

1. In VTube Studio: Settings > Virtual Webcam > Start
2. In OBS: Add Source > Video Capture Device > Select "VTube Studio" from device list
3. The avatar feed appears as a webcam source

**Note:** Virtual Camera on Mac has had some reported issues. Test this. If it does not work, use Method 1 or Method 3.

### Method 3: NDI (Network-Based, Advanced)

Works across machines on the same network. Useful if you run the avatar on one machine and OBS on another.

1. Install OBS NDI plugin
2. In VTube Studio: Camera Settings > Activate NDI
3. In OBS: Add Source > NDI Source > Select VTube Studio stream
4. Low-latency, high-quality, transparent background

**Use case for your setup:** Run VTube Studio on Mac M4, send via NDI to Cobo for encoding/streaming if needed.

### Method 4: Spout2 (Windows Only - Best Quality)

If you run OBS on the Windows machine:

1. Install Spout2 plugin for OBS
2. In VTube Studio: Camera Settings > Activate Spout2
3. In OBS: Add Source > Spout2 Capture > Select VTube Studio
4. Set Composite Mode to "Transparent"

**This is the cleanest method on Windows.** Zero latency, perfect transparency, no UI captured.

### OBS Scene Setup for AI News Content

Suggested scene layout:
```
Layer 4 (top):     Alert overlays, notifications
Layer 3:           VTuber avatar (bottom-right or bottom-left, ~25-30% of screen)
Layer 2:           Content area (browser, slides, news articles, AI demos)
Layer 1 (bottom):  Background (branded lower third, news desk graphic)
```

---

## Face Expression Mapping

### How It Works

Face tracking software captures your real facial movements and maps them to parameters that control the avatar. Here is what gets tracked:

### Webcam Tracking (OpenSeeFace)

Uses AI-based facial landmark detection through your webcam. Tracks approximately 20-30 parameters:

- **Head:** rotation (look left/right, up/down, tilt)
- **Eyes:** open/close (each eye independently), eye gaze direction
- **Eyebrows:** raise/lower (each independently)
- **Mouth:** open/close, smile, frown, basic mouth shapes
- **Body:** slight upper body sway based on head movement

**Quality:** Good enough for content creation. Some jitter. Works in moderate lighting.

### iPhone ARKit Tracking (Recommended)

Uses the TrueDepth camera (Face ID sensor) on iPhone X or newer. Tracks 52 facial blendshapes:

- Everything webcam tracks, PLUS:
- **Tongue:** stick out, direction
- **Cheeks:** puff left/right
- **Jaw:** open, left/right, forward
- **Lips:** pucker, funnel, press, individual lip movements
- **Eye squint, wide open** (separate from blink)
- **Nose sneer** left/right
- **Brow inner up/down** (furrowing)

**Quality:** Dramatically better. Smoother, less jitter, faster response, more expressions. If you have an iPhone, use it. Period.

### Setup for iPhone Tracking with VTube Studio

1. Install VTube Studio on both Mac and iPhone
2. Connect both to the same WiFi network
3. On iPhone: open VTube Studio, it becomes the tracker
4. On Mac: VTube Studio settings > select iPhone as tracking source
5. Position iPhone on a small tripod at face level, about arm's length away

**iPhone mount recommendation:** Any small phone tripod or desk mount works. $10-20 on Amazon.

### Custom Expression Hotkeys

In VTube Studio, you can bind keyboard shortcuts to trigger specific expressions:

- Press "1" = surprised face
- Press "2" = angry face
- Press "3" = laughing
- Press "4" = thinking/hmm
- Press "5" = glasses on/off

These override the live tracking temporarily, useful for reaction content.

---

## Custom Animations

### Types of Animations

1. **Idle animations** - Subtle movement when you are still (breathing, slight sway, blinking patterns)
2. **Triggered animations** - One-shot reactions (wave, nod, headbang, celebration)
3. **Loop animations** - Continuous motions (dancing, typing, head bobbing)
4. **Toggle states** - Switch between poses (sitting, standing, leaning)

### How to Add Animations to a Live2D Model

#### Creating Animations in Live2D Cubism

1. Open your model in Live2D Cubism Editor (need the .cmo3 project file, not just .moc3)
2. Go to the Animation workspace
3. Create a new animation scene
4. Use keyframes to animate parameters over time (head tilt, arm raise, etc.)
5. Export as .motion3.json file

#### Loading Animations into VTube Studio

1. Place the .motion3.json files in the same folder as your model (or a subfolder)
2. VTube Studio automatically detects them
3. In VTube Studio: Settings > Expressions/Hotkeys
4. Assign animations to keyboard shortcuts or screen buttons
5. Set type: "Idle" (loops randomly) or "Expression" (triggered on demand)

#### Idle Animation Setup

Idle motions go in a motion group named "idle" or "Idle". VTube Studio randomly selects from this group when there is no tracking input. Typical idle animations:

- Gentle breathing (chest rise/fall)
- Slow blink patterns
- Slight head movements
- Hair physics (this is usually handled by the physics engine, not animation)

#### Getting Animations Without Making Them Yourself

- **Commission from your model rigger** - Ask when commissioning the model. Usually $20-100 per animation.
- **Fiverr** - Search "VTuber idle animation" or "Live2D animation". Prices start around $20.
- **Pre-made animation packs** - Available on Booth.pm, but must match your model's parameter setup.

### For 3D Models (VRM/VSeeFace)

3D models support more complex animations:
- Full body movement
- Dance motions (import from Mixamo, free motion capture library)
- Hand gestures
- Walking, sitting, custom poses

**Mixamo** (free, by Adobe): https://www.mixamo.com/ - Upload your 3D model, apply pre-made animations. Thousands of free motion capture animations.

---

## What Popular VTubers Use

### TheBurntPeanut
- **Software:** Stream Fog (AR-powered avatar platform)
- **Avatar:** Custom 3D peanut character, originally started from a $5 3D model
- **Tracking:** AR face tracking through Stream Fog
- **Style:** 3D avatar with exaggerated expressions, frequent outfit changes
- **Takeaway:** Started cheap, iterated. The character design matters more than the tech.

### Neuro-sama (AI VTuber)
- **Avatar software:** VTube Studio (Live2D)
- **Tech stack:** C#, Python, JavaScript
- **AI:** Custom 2B parameter LLM, text-to-speech piped to VTube Studio via virtual audio cable for lip sync
- **Tracking:** No human tracking. AI controls the avatar parameters directly.
- **Takeaway:** Relevant to AI news content. You could potentially automate avatar reactions using AI.

### Ironmouse
- **Avatar:** Custom Live2D model (high-end professional commission)
- **Software:** VTube Studio
- **Tracking:** Standard VTuber face tracking setup
- **Multiple outfits:** Toggleable via hotkeys
- **Takeaway:** High-quality commissioned model + VTube Studio is the standard pro setup.

### CodeMiko
- **Avatar:** Full 3D model using Unreal Engine + motion capture suit
- **Tracking:** Full body mocap (Xsens suit, ~$5K+)
- **Takeaway:** Way beyond what a solo creator needs. Impressive but not the path for starting out.

### General Pattern Among Top VTubers
- Most 2D VTubers use **VTube Studio + Live2D models**
- Most invest $500-3000 in their avatar over time
- iPhone ARKit tracking is the standard for quality
- They start simple and upgrade as they grow

---

## Recommended Setup for AI News Content

Here is the specific setup I recommend for producing AI news content with a VTuber avatar, in order of priority.

### Phase 1: Start Recording This Week ($0-15)

**Goal:** Get a working VTuber setup and record your first video.

1. Install **VTube Studio** on Mac (free via Steam)
2. Install **VTube Studio** on iPhone (free)
3. Get a **pre-made Live2D model** from Booth.pm (free or $10-30)
4. Set up **iPhone ARKit tracking** over WiFi
5. Install **OBS** on Mac (free)
6. Capture VTube Studio in OBS using macOS Screen Capture source with transparency
7. Record a test AI news segment

**Hardware you already have:** Mac M4, iPhone, webcam as backup.
**Total cost:** $0-15 (VTube Studio Pro DLC to remove watermark)

### Phase 2: Build Your Brand ($200-600)

**Goal:** Get a unique, recognizable avatar.

1. Commission a **custom Live2D model** on Fiverr or Twitter ($200-600)
   - Half-body is fine for news content
   - Ask for: 4-6 expressions, idle breathing animation, physics on hair/accessories
   - Get the source files (.cmo3 + PSD) so you can add to it later
2. Add **custom expressions** via hotkeys for reacting to news (shocked, thinking, laughing)
3. Design a **branded OBS scene** (lower thirds, news desk background, logo)

### Phase 3: Level Up Production ($50-200 extra)

**Goal:** Polish and differentiate.

1. Get **Live2D Cubism Pro** (use student discount, ~$12/year) to make your own tweaks and animations
2. Add **custom triggered animations** (celebration when breaking news, head shake for bad takes)
3. Consider a **3D model on Cobo** (Windows + GTX 1080 Ti) using VSeeFace for variety content
4. Set up **NDI** to send avatar from one machine to the other if needed
5. Experiment with **AI-driven avatar control** for automated segments (the Neuro-sama approach)

### Your Two-Machine Strategy

| Machine | Role | Software |
|---------|------|----------|
| Mac M4 (Ceiba) | Primary recording/streaming, face tracking, editing | VTube Studio, OBS, iPhone tracker |
| Windows + GTX 1080 Ti (Cobo) | Heavy rendering, 3D avatar alternative, AI processing | VSeeFace, VTube Studio, Blender |

---

## Budget Breakdown

### The $0 Setup (Proof of Concept)
| Item | Cost |
|------|------|
| VTube Studio (Steam, free with watermark) | $0 |
| Free Live2D model from Booth.pm | $0 |
| OBS Studio | $0 |
| iPhone as tracker (already own) | $0 |
| **Total** | **$0** |

### The $50 Setup (Solid Start)
| Item | Cost |
|------|------|
| VTube Studio Pro DLC | $15 |
| Pre-made Live2D model (Booth/nizima) | $20-35 |
| Phone tripod/desk mount | $10-15 |
| OBS Studio | $0 |
| **Total** | **~$50** |

### The $500 Setup (Branded Creator)
| Item | Cost |
|------|------|
| VTube Studio Pro DLC | $15 |
| Custom Live2D commission (Fiverr mid-tier) | $300-500 |
| Live2D Cubism Pro (student rate, 1 year) | ~$12 |
| Phone tripod | $15 |
| OBS Studio | $0 |
| **Total** | **~$350-550** |

### The $1500+ Setup (Full Production)
| Item | Cost |
|------|------|
| VTube Studio Pro DLC | $15 |
| Professional Live2D commission | $1,000-2,500 |
| Live2D Cubism Pro (indie, 1 year) | ~$47 |
| Custom animations (5-10 animations) | $100-300 |
| Stream Fog subscription (optional) | $10-20/mo |
| Lighting for face tracking | $30-50 |
| **Total** | **~$1,200-3,000** |

---

## Key Decisions to Make

1. **2D (Live2D) vs 3D (VRM)?**
   - 2D = lighter, runs great on Mac, more stylish, industry standard for VTubers
   - 3D = more expressive, full body possible, free creation with VRoid, heavier on GPU
   - **Recommendation for AI news:** 2D (Live2D). It is the standard, looks professional, runs perfectly on M4.

2. **Custom vs pre-made model?**
   - Start with pre-made to learn the workflow. Commission custom when you know what you want.

3. **Webcam vs iPhone tracking?**
   - iPhone. Every time. The quality difference is massive (52 blendshapes vs ~20-30 parameters, less jitter, faster response).

4. **Mac vs Windows for VTubing?**
   - Mac M4 handles VTube Studio + OBS easily for 2D. Use Windows for 3D if needed.

---

## Sources

- [VTube Studio Official](https://denchisoft.com/)
- [VTube Studio Wiki - OBS Setup](https://github.com/DenchiSoft/VTubeStudio/wiki/Recording-Streaming-with-OBS)
- [VTube Studio Wiki - iPhone vs Webcam](https://github.com/DenchiSoft/VTubeStudio/wiki/Android-vs.-iPhone-vs.-Webcam)
- [VTube Studio Wiki - Animations](https://github.com/DenchiSoft/VTubeStudio/wiki/Animations)
- [Live2D Cubism Editor](https://www.live2d.com/en/cubism/about/)
- [Live2D Free vs Pro Comparison](https://www.live2d.com/en/cubism/comparison/)
- [Live2D Tutorials](https://docs.live2d.com/en/cubism-editor-tutorials/)
- [VRoid Studio](https://vroid.com/en/studio)
- [VSeeFace](https://www.vseeface.icu/)
- [nizima LIVE](https://nizimalive.com/en/)
- [Stream Fog](https://streamfog.com/)
- [Booth.pm VTuber Models](https://booth.pm/en/browse/VTuber)
- [VTuber Model Cost Guide 2026](https://vtubermodels.com/how-much-do-vtuber-models-cost/)
- [Best VTuber Software 2026 - Kudos.tv](https://kudos.tv/blogs/stream-blog/the-best-vtuber-software)
- [Best VTuber Software - GitHub Gist](https://gist.github.com/emilianavt/cbf4d6de6f7fb01a42d4cce922795794)
- [Mixamo Free Animations](https://www.mixamo.com/)
- [OBS Virtual Camera Guide](https://obsproject.com/kb/virtual-camera-guide)
- [Neuro-sama Wiki](https://virtualyoutuber.fandom.com/wiki/Neuro-sama)
- [TheBurntPeanut Setup](https://www.burntpeanutsetup.com/)

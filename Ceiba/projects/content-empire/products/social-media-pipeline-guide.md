# Turn RSS Feeds into Instagram Posts with Python

**By Behike** | $4.99

---

> Copyright 2026 Behike. All rights reserved.
> This guide was written with AI assistance. The code, architecture, and editorial direction are original work by the author.
> You may use and modify the code for personal or commercial projects. You may not redistribute this guide.

---

## What You're Building

You have news articles. You need Instagram posts. This guide connects those two things with a Python pipeline that takes scored articles from an RSS tracker and generates ready-to-post captions and visual carousels.

The system does three things:

1. **Transforms articles into captions** using 5 content templates based on the OPB (One Person Business) framework
2. **Generates HTML-based carousel slides** at 1080x1080 pixels with Apple-minimal design and 4 color themes
3. **Builds hashtag sets automatically** based on article content, mentions, and category

You are not writing posts by hand. You are feeding articles into templates that produce consistent, on-brand content. One command, multiple posts, saved to disk, ready to screenshot and upload.

Prerequisites: A working RSS feed tracker with scored articles in JSON format (see the companion guide "Build Your Own AI News Tracker in Python"), and Python 3.8+.

---

## The News-to-Post Pipeline

The core idea is simple: every news article is raw material. The same story can become 5 completely different posts depending on the angle you choose. That is what the OPB content templates do.

### The 5 OPB Templates

Each template defines a structure, a tone, and a purpose. Here is how each one transforms the same article.

**Template 1: Importance**

Purpose: Explain why something matters for builders.

```python
"importance": {
    "name": "Importance",
    "desc": "Why this matters for builders",
    "format": "Why {topic} matters for builders:\n\n{reasons}\n\n{closer}",
}
```

Example output from an article about NVIDIA's new GPU:

```
Why NVIDIA Blackwell B300 matters for builders:

- The new B300 delivers 4x the performance of H100 for training workloads.
- Pricing suggests a shift toward making large model training accessible to smaller teams.
- NVIDIA is bundling software optimizations that reduce inference costs by 60%.

News without context is noise.
Context without action is philosophy.
Build accordingly.
```

**Template 2: Harsh Truth**

Purpose: Call out what people are missing about a story.

```python
"harsh_truth": {
    "name": "Harsh Truth",
    "desc": "Call out what people are missing",
    "format": "{hook}\n\n{body}\n\n{closer}",
}
```

Example output:

```
Everyone is talking about NVIDIA Blackwell B300.

What they're missing: The real story is not the chip. It is the software stack that locks you into NVIDIA's ecosystem.

Pay attention to what changes. Ignore the noise.
```

**Template 3: Principles**

Purpose: Break down the facts. Straightforward, informational.

```python
"principles": {
    "name": "Principles",
    "desc": "Break down what happened and what it means",
    "format": "{hook}\n\n{points}\n\n{closer}",
}
```

Example output:

```
NVIDIA Announces Blackwell B300 GPU for AI Training

- The new B300 delivers 4x the performance of H100 for training workloads.
- Pricing suggests a shift toward accessible large model training.
- Software bundle reduces inference costs by 60%.

Key players: NVIDIA, Jensen Huang

via NVIDIA Blog
```

**Template 4: Pain Resolution**

Purpose: Connect the news to the reader's actual problem, then offer a filter.

```python
"pain_resolution": {
    "name": "Pain Resolution",
    "desc": "Connect news to reader's problem, offer filter",
    "format": "{audience_callout}\n\n{pains}\n\n{solution}",
}
```

Example output:

```
If you're struggling to keep up with AI news:

NVIDIA Announces Blackwell B300 GPU for AI Training

The new B300 delivers 4x the performance of H100 for training workloads.

Here's your filter: follow the money, follow the builders.
Everything else is commentary.
```

**Template 5: Confident Advice**

Purpose: Tell the reader exactly what to do with this information.

```python
"confident_advice": {
    "name": "Confident Advice",
    "desc": "Step-by-step what to do with this info",
    "format": "{hook}\n\n{steps}\n\n{nuance}\n\n{summary}",
}
```

Example output:

```
What to do about NVIDIA Announces Blackwell B300 GPU for AI Training:

1. Read the actual announcement, not the headline
2. Ask: does this change what I'm building?
3. If yes, adapt now. If no, keep shipping.

Context: The new B300 delivers 4x the performance of H100 for training workloads.

The best response to any AI news is shipping your own work.
```

### Generating a caption

The `generate_caption` function takes an article dictionary and a template name:

```python
def generate_caption(article, template="principles"):
    title = clean_html(article["title"])
    summary = clean_html(article.get("summary", ""))
    source = article["source"]
    mentions = article.get("mentions", [])
    tags = _build_tags(article)
    facts = _extract_key_facts(summary)

    lines = []
    # ... template logic builds the caption ...
    lines.append("")
    lines.append(tags)
    return "\n".join(lines)
```

The function automatically extracts key facts from the summary, sorts them longest to shortest (for visual taper on screen), cleans HTML entities, and appends hashtags.

### Seeing all 5 angles at once

```bash
python3 news_to_post.py --story 1 --all-templates
```

This generates all 5 templates for the same story. Pick whichever angle fits your feed that day. Variety keeps your audience engaged.

---

## Building Carousels

The carousel generator creates HTML files with 1080x1080 pixel slides. Open in a browser, screenshot each slide, and you have Instagram carousel images.

### Why HTML instead of Pillow or Canva

HTML gives you full control over typography, spacing, gradients, and responsive text. No image library dependencies. No subscription fees. Edit the CSS once and every future carousel matches your brand.

### The 4 themes

```python
THEMES = {
    "bone": {
        "bg": "#faf9f6", "card": "#ffffff",
        "accent": "#1d1d1f", "text": "#1d1d1f",
        "muted": "#86868b",
        "font": "'SF Pro Display', 'Helvetica Neue', Helvetica, Arial, sans-serif",
    },
    "ink": {
        "bg": "#0a0a0a", "card": "#111111",
        "accent": "#f5f5f7", "text": "#f5f5f7",
        "muted": "#6e6e73",
        "font": "'SF Pro Display', 'Helvetica Neue', Helvetica, Arial, sans-serif",
    },
    "slate": {
        "bg": "#1c1c1e", "card": "#2c2c2e",
        "accent": "#f5f5f7", "text": "#f5f5f7",
        "muted": "#636366",
        "font": "'SF Pro Display', 'Helvetica Neue', Helvetica, Arial, sans-serif",
    },
    "warm": {
        "bg": "#f2efe8", "card": "#faf8f3",
        "accent": "#2d2926", "text": "#2d2926",
        "muted": "#8a8480",
        "font": "'Georgia', 'Times New Roman', serif",
    },
}
```

Each theme defines background, text, accent, and muted colors plus a font stack. The design philosophy is Apple minimalism: lots of whitespace, clean typography, no clutter.

- **bone** is a light, paper-white theme. Good for readability in bright feeds.
- **ink** is pure dark. High contrast, modern feel. Default.
- **slate** is a softer dark. Less harsh than ink, still premium.
- **warm** uses Georgia serif and parchment tones. More editorial, magazine-like.

### Slide structure

Every carousel generates these slides:

1. **Hook slide** with the headline, source label, impact dot (red for HIGH, yellow for MEDIUM), and a "SWIPE" hint
2. **What Happened slide** with the article summary in large body text
3. **Key Players slide** (if entity mentions exist) listing names in a tapered layout, longest to shortest
4. **Why It Matters slide** (if you provide analysis) with your take on the story
5. **CTA slide** with "Follow for daily AI news. Short. Direct. No hype."

### Generating a carousel

From the news tracker data:

```bash
python3 carousel_generator.py --from-tracker 1 --theme bone
```

From custom input:

```bash
python3 carousel_generator.py "GPT-5 Just Dropped" \
  --body "OpenAI released GPT-5 with native reasoning" \
  --source "OpenAI Blog" \
  --impact HIGH \
  --players "Sam Altman" "Mira Murati" \
  --why "This changes the competitive landscape for every AI company" \
  --theme ink
```

The output is an HTML file saved to the carousels directory. Open it in Chrome, set the window to 1080px wide, and screenshot each slide. Each slide is exactly 1080x1080.

### The CSS that makes it work

The slides use a simple CSS layout:

```css
.slide {
    width: 1080px;
    height: 1080px;
    background: linear-gradient(180deg, #0a0a0a 0%, #1d1d1f 100%);
    position: relative;
    display: flex;
    align-items: center;
    justify-content: center;
}

.slide-inner {
    padding: 100px;
    width: 100%;
}

.headline {
    font-family: 'Playfair Display', 'Georgia', serif;
    font-size: 64px;
    font-weight: 700;
    line-height: 1.15;
    letter-spacing: -0.5px;
}
```

The 100px padding on all sides creates generous margins. The headline uses Playfair Display at 64px for that editorial, high-end feel. Body text sits at 34px for readability when viewed on a phone screen.

Customize by editing the theme dictionaries and the CSS. Every visual property is controlled from one place.

---

## Hashtag Strategy

The `_build_tags` function generates a focused set of up to 10 hashtags. No spam walls of 30 tags. Quality over quantity.

### How it works

```python
def _build_tags(article):
    """Build focused hashtag set. Max 10, no spam."""
    mentions = article.get("mentions", [])
    tags = ["#AI", "#technews"]

    # Add entity mentions as hashtags
    for m in mentions[:5]:
        tag = "#" + m.replace(" ", "").replace("-", "").lower()
        if tag not in tags:
            tags.append(tag)

    # Add category-specific tags
    cat = article.get("category", "")
    cat_tags = {
        "releases": ["#aitools", "#newrelease"],
        "hardware": ["#nvidia", "#gpu"],
        "research": ["#airesearch", "#machinelearning"],
        "regulation": ["#airegulation", "#policy"],
        "business": ["#startup", "#venture"],
    }
    for t in cat_tags.get(cat, []):
        if t not in tags:
            tags.append(t)

    # Fill remaining slots with general tags
    filler = ["#artificialintelligence", "#deeplearning", "#tech",
              "#innovation", "#coding", "#future"]
    for t in filler:
        if len(tags) >= 10:
            break
        if t not in tags:
            tags.append(t)

    return " ".join(tags)
```

The logic has three layers:

1. **Always include** `#AI` and `#technews` as base tags
2. **Entity-based tags** convert mentions like "Sam Altman" into `#samaltman`. These are high-signal because people search for specific names.
3. **Category tags** match the article's topic. A hardware article gets `#nvidia #gpu`. A research article gets `#airesearch #machinelearning`.
4. **Filler tags** pad to 10 if needed. These are broad-reach tags that perform consistently.

Duplicates are checked at every step. The result is always 10 or fewer unique, relevant hashtags.

### Customizing for your niche

Edit the `cat_tags` dictionary to match your content categories. If you cover crypto + AI, add:

```python
"crypto": ["#web3", "#defi", "#blockchain"],
```

If you cover design tools, add:

```python
"design": ["#uidesign", "#figma", "#designtools"],
```

The hashtag function is deliberately simple so you can adapt it to any niche in under a minute.

---

## Batch Production

This is where the pipeline pays off. Instead of writing one post at a time, you generate posts for every high-impact story at once.

### Generate posts for all HIGH impact stories

```bash
python3 news_to_post.py --all-high --save
```

This command:

1. Loads today's articles from the tracker
2. Filters to only HIGH impact stories
3. Rotates through the 5 OPB templates automatically (so each post uses a different angle)
4. Prints every caption to the terminal
5. Saves each post as a JSON file to disk

The rotation is automatic. Post 1 gets "importance", post 2 gets "harsh_truth", post 3 gets "principles", and so on. This creates natural variety in your feed without you thinking about it.

### Add carousels to the batch

```bash
python3 news_to_post.py --all-high --carousel --save
```

This adds carousel slide data to each saved post. The JSON output includes the full caption, hashtags, and slide-by-slide text for the carousel.

### Generate carousels for specific stories

First, list what is available:

```bash
python3 news_to_post.py --list
```

Output:

```
  Today's Top Stories (2026-03-21)

   1. [!!!] NVIDIA Announces Blackwell B300 GPU for AI Training [NVIDIA, Jensen Huang]
       NVIDIA Blog
   2. [!!!] OpenAI Releases GPT-5 with Reasoning [OpenAI, Sam Altman]
       TechCrunch AI
   3. [**]  New MCP Integration Connects Claude to Enterprise Tools
       Anthropic News
```

Then generate a specific carousel:

```bash
python3 carousel_generator.py --from-tracker 1 --theme ink
python3 carousel_generator.py --from-tracker 2 --theme bone
python3 carousel_generator.py --from-tracker 3 --theme warm
```

### The daily workflow

Here is the full process, start to finish:

```bash
# 1. Fetch the latest news
python3 ai_news_tracker.py --fetch

# 2. See what scored HIGH
python3 news_to_post.py --list

# 3. Generate all posts
python3 news_to_post.py --all-high --carousel --save

# 4. Generate visual carousels for the top 3
python3 carousel_generator.py --from-tracker 1 --theme ink
python3 carousel_generator.py --from-tracker 2 --theme bone
python3 carousel_generator.py --from-tracker 3 --theme slate

# 5. Open carousels in browser, screenshot slides, upload to Instagram
```

Total time: about 5 minutes for 3-5 posts with visuals. Compare that to manually writing and designing each post.

### Saved file structure

After a batch run, your folder looks like this:

```
data/
  articles.json           # All tracked articles
  posts/
    post-2026-03-21-a3f2.json    # Post 1
    post-2026-03-21-b8e1.json    # Post 2
    post-2026-03-21-c5d9.json    # Post 3
  carousels/
    carousel-2026-03-21-nvidia-announces-blackwell.html
    carousel-2026-03-21-openai-releases-gpt-5.html
    carousel-2026-03-21-new-mcp-integration.html
```

Everything is plain files. JSON for data, HTML for visuals. No databases, no cloud dependencies. Back it up however you want.

---

**The whole point of this pipeline is that you spend 5 minutes producing content instead of 2 hours. The templates handle the writing structure. The carousel generator handles the design. You handle the upload and the occasional human touch on a caption that needs it.**

---

*Built by Behike. For builders who ship content, not just consume it.*

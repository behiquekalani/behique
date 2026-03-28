#!/usr/bin/env python3
# Copyright 2026 Behike. All rights reserved.
"""
AI News Instagram Content Pipeline -- One command, full daily content.

Orchestrates the entire flow from RSS fetch to ready-to-post content:
RSS -> Score -> Carousels -> Captions -> Reel Scripts -> TTS -> Spanish

Usage:
    python3 ai_news_pipeline.py --daily           # full pipeline
    python3 ai_news_pipeline.py --fetch-only       # just fetch, no generation
    python3 ai_news_pipeline.py --stories 3        # top 3 stories
    python3 ai_news_pipeline.py --reels 1          # 1 reel script
    python3 ai_news_pipeline.py --no-tts           # skip TTS
    python3 ai_news_pipeline.py --no-spanish       # skip Spanish translations
    python3 ai_news_pipeline.py --dry-run          # preview without generating
"""
import json
import os
import re
import sys
import subprocess
import argparse
import hashlib
from datetime import datetime
from pathlib import Path

# --- Paths ---
TOOLS_DIR = Path(__file__).parent
PROJECT_DIR = TOOLS_DIR.parent
NEWS_DIR = PROJECT_DIR / "Ceiba" / "news"
DAILY_DIR = NEWS_DIR / "daily"
ARTICLES_FILE = NEWS_DIR / "articles.json"
REEL_PIPELINE_DIR = TOOLS_DIR / "reel-pipeline"
KOKORO_MODEL = REEL_PIPELINE_DIR / "kokoro-v1.0.onnx"
KOKORO_VOICES = REEL_PIPELINE_DIR / "voices-v1.0.bin"

# --- Import sibling tools ---
sys.path.insert(0, str(TOOLS_DIR))
from ai_news_tracker import fetch_feeds, load_articles, ensure_dirs, score_impact
from news_to_post import generate_caption, clean_html, OPB_TEMPLATES, _build_tags
from carousel_generator import generate_carousel_html, THEMES

# --- Theme rotation ---
THEME_ORDER = ["ink", "bone", "slate", "warm"]

# --- Shape auto-matching rules ---
SHAPE_RULES = [
    (["nvidia", "gpu", "chip", "hardware", "blackwell", "h100", "b200"], "bolt"),
    (["brain", "neural", "ml", "machine learning", "deep learning", "training", "model"], "brain"),
    (["regulation", "ban", "law", "policy", "ftc", "sec", "antitrust", "safety", "alignment"], "shield"),
    (["openai", "anthropic", "claude", "gpt", "gemini", "diamond"], "diamond"),
]

# --- Spanish translation map for common phrases ---
SPANISH_HASHTAGS = [
    "#inteligenciaartificial", "#tecnologia", "#noticias",
    "#innovacion", "#futuro", "#programacion", "#aprendizaje",
    "#startups", "#emprendimiento", "#automatizacion",
]


def get_today_str():
    return datetime.now().strftime("%Y-%m-%d")


def get_output_dir():
    today = get_today_str()
    out = DAILY_DIR / today
    out.mkdir(parents=True, exist_ok=True)
    return out


def match_shape(title, summary=""):
    """Auto-match a Robert Greene shape based on keywords in the story."""
    text = f"{title} {summary}".lower()
    for keywords, shape in SHAPE_RULES:
        for kw in keywords:
            if kw in text:
                return shape
    return "circle"


def pick_best_template(article):
    """Pick the best OPB template based on story characteristics."""
    impact = article.get("impact", "LOW")
    category = article.get("category", "")
    title_lower = article.get("title", "").lower()

    # High impact breaking news -> harsh_truth or principles
    if impact == "HIGH":
        if any(w in title_lower for w in ["launch", "release", "announce", "open source"]):
            return "importance"
        if any(w in title_lower for w in ["fired", "resign", "lawsuit", "ban"]):
            return "harsh_truth"
        return "principles"

    # Releases and product updates -> confident_advice
    if category == "releases":
        return "confident_advice"

    # Research -> principles
    if category == "research":
        return "principles"

    # Everything else -> pain_resolution
    return "pain_resolution"


def translate_to_spanish(caption):
    """Translate an English caption to natural LATAM Spanish.

    This is a rule-based approximation. For production quality,
    you would use an LLM or translation API. This handles the
    structural transformation while keeping technical terms and hashtags.
    """
    lines = caption.split("\n")
    translated = []

    # Common phrase translations
    phrase_map = {
        "Why": "Por que",
        "matters for builders": "importa para los que construyen",
        "Everyone is talking about": "Todos estan hablando de",
        "What they're missing:": "Lo que no estan viendo:",
        "Pay attention to what changes. Ignore the noise.": "Presta atencion a lo que cambia. Ignora el ruido.",
        "News without context is noise.": "Las noticias sin contexto son ruido.",
        "Context without action is philosophy.": "El contexto sin accion es filosofia.",
        "Build accordingly.": "Construye en base a eso.",
        "If you're struggling to keep up with AI news:": "Si te cuesta mantenerte al dia con las noticias de AI:",
        "Here's your filter: follow the money, follow the builders.": "Tu filtro: sigue el dinero, sigue a los que construyen.",
        "Everything else is commentary.": "Todo lo demas es comentario.",
        "What to do about": "Que hacer con",
        "Read the actual announcement, not the headline": "Lee el anuncio real, no el titular",
        "Ask: does this change what I'm building?": "Preguntate: esto cambia lo que estoy construyendo?",
        "If yes, adapt now. If no, keep shipping.": "Si si, adaptate ahora. Si no, sigue construyendo.",
        "The best response to any AI news is shipping your own work.": "La mejor respuesta a cualquier noticia de AI es seguir construyendo lo tuyo.",
        "Key players:": "Actores clave:",
        "via ": "via ",
        "Follow for daily AI news.": "Sigueme para noticias de AI diarias.",
        "Short. Direct. No hype.": "Corto. Directo. Sin hype.",
        "Just what matters.": "Solo lo que importa.",
        "Swipe to learn more ->": "Desliza para saber mas ->",
        "WHAT HAPPENED": "QUE PASO",
        "KEY PLAYERS": "ACTORES CLAVE",
        "WHY IT MATTERS": "POR QUE IMPORTA",
    }

    for line in lines:
        new_line = line

        # Skip hashtag lines (keep English hashtags, append Spanish ones)
        if line.strip().startswith("#"):
            # Add 3-4 Spanish hashtags
            import random
            es_tags = random.sample(SPANISH_HASHTAGS, min(4, len(SPANISH_HASHTAGS)))
            new_line = line + " " + " ".join(es_tags)
            translated.append(new_line)
            continue

        # Apply phrase translations
        for en, es in phrase_map.items():
            if en in new_line:
                new_line = new_line.replace(en, es)

        translated.append(new_line)

    return "\n".join(translated)


def generate_reel_script(article, index):
    """Generate a 30-60 second reel script in the reel-pipeline JSON format."""
    title = clean_html(article["title"])
    summary = clean_html(article.get("summary", ""))
    source = article.get("source", "")
    mentions = article.get("mentions", [])

    # Build hook (first 3 seconds)
    hook_text = title if len(title) < 60 else title[:57] + "..."

    # Build key points
    sentences = [s.strip() for s in summary.replace(". ", ".\n").split("\n") if s.strip()]
    key_points = sentences[:4]
    if not key_points:
        key_points = [summary[:100]] if summary else ["Details are still emerging."]

    # Build narration
    narration_parts = [
        hook_text + ".",
    ]
    for point in key_points:
        p = point.strip()
        if p and not p.endswith("."):
            p += "."
        narration_parts.append(p)

    if mentions:
        players = ", ".join(mentions[:3])
        narration_parts.append(f"Key players: {players}.")

    narration_parts.append("Follow @behikeai for daily AI news.")

    narration = " ".join(narration_parts)

    # Build scenes
    scenes = []

    # Scene 0: Hook
    scenes.append({
        "text": hook_text,
        "image_prompt": f"Bold modern tech graphic, dark background, glowing text effect, breaking news style, {title[:40]}, 4k cinematic",
        "overlay_text": hook_text,
    })

    # Scenes 1-3: Key points
    for i, point in enumerate(key_points[:3]):
        scenes.append({
            "text": point,
            "image_prompt": f"Abstract tech visualization, dark minimalist, data flowing, AI neural network, scene {i+1}, cinematic 4k",
            "overlay_text": point[:60],
        })

    # Scene 4: CTA
    scenes.append({
        "text": "Follow @behikeai for daily AI news.",
        "image_prompt": "Minimalist dark gradient background, subtle tech particles, clean modern design, brand logo space, 4k",
        "overlay_text": "Follow @behikeai",
    })

    reel_data = {
        "title": title,
        "source": source,
        "narration": narration,
        "scenes": scenes,
        "metadata": {
            "target_duration": "30-60s",
            "voice": "af_heart",
            "speed": 0.95,
            "impact": article.get("impact", "MEDIUM"),
            "generated": datetime.now().isoformat(),
        },
    }

    return reel_data


def generate_tts_for_reel(reel_data, output_path):
    """Generate TTS narration for a reel script using Kokoro."""
    if not KOKORO_MODEL.exists():
        print(f"  [TTS] Kokoro model not found at {KOKORO_MODEL}, skipping TTS")
        return False

    narration = reel_data.get("narration", "")
    if not narration:
        print("  [TTS] No narration text, skipping")
        return False

    voice = reel_data.get("metadata", {}).get("voice", "af_heart")
    speed = reel_data.get("metadata", {}).get("speed", 0.95)

    try:
        import kokoro_onnx
        import soundfile as sf

        print(f"  [TTS] Generating narration ({len(narration)} chars)...")
        kokoro = kokoro_onnx.Kokoro(str(KOKORO_MODEL), str(KOKORO_VOICES))
        samples, sample_rate = kokoro.create(narration, voice=voice, speed=speed)

        sf.write(str(output_path), samples, sample_rate)
        duration = len(samples) / sample_rate
        print(f"  [TTS] Generated {duration:.1f}s audio -> {output_path}")
        return True
    except ImportError:
        print("  [TTS] kokoro_onnx or soundfile not installed, skipping TTS")
        return False
    except Exception as e:
        print(f"  [TTS] Error generating TTS: {e}")
        return False


# =====================================================================
# MAIN PIPELINE
# =====================================================================

def run_pipeline(args):
    """Run the full daily content pipeline."""
    today = get_today_str()
    out_dir = get_output_dir()
    num_stories = args.stories
    num_reels = args.reels
    do_tts = not args.no_tts
    do_spanish = not args.no_spanish
    dry_run = args.dry_run

    print()
    print("=" * 60)
    print(f"  BEHIKE AI NEWS PIPELINE -- {today}")
    print("=" * 60)
    print()

    # ---------------------------------------------------------------
    # STEP 1: FETCH
    # ---------------------------------------------------------------
    print("[1/9] FETCHING RSS feeds...")
    ensure_dirs()

    if dry_run:
        print("  [DRY RUN] Would fetch from all RSS feeds")
    else:
        new_articles = fetch_feeds()
        print(f"  Found {len(new_articles)} new articles")

    if args.fetch_only:
        print("\n  --fetch-only: stopping after fetch.")
        return

    # ---------------------------------------------------------------
    # STEP 2: SCORE & SELECT
    # ---------------------------------------------------------------
    print(f"\n[2/9] SELECTING top {num_stories} HIGH impact stories...")
    articles = load_articles()

    if not articles:
        print("  No articles found. Run with --fetch-only first or check RSS feeds.")
        return

    # Prefer today's articles
    today_articles = [a for a in articles if a.get("fetched", "")[:10] == today]
    if not today_articles:
        print("  No articles fetched today, using most recent available")
        today_articles = articles

    # Sort by impact score, prefer HIGH
    today_articles.sort(key=lambda a: a.get("impact_score", 0), reverse=True)

    # Select top N, prioritizing HIGH impact
    high = [a for a in today_articles if a["impact"] == "HIGH"]
    medium = [a for a in today_articles if a["impact"] == "MEDIUM"]
    selected = (high + medium)[:num_stories]

    # If we don't have enough HIGH/MEDIUM, fill with whatever is available
    if len(selected) < num_stories:
        remaining = [a for a in today_articles if a not in selected]
        selected.extend(remaining[:num_stories - len(selected)])

    selected = selected[:num_stories]

    print(f"  Selected {len(selected)} stories:")
    for i, s in enumerate(selected, 1):
        print(f"    {i}. [{s['impact']}] {s['title'][:65]}")
        print(f"       {s['source']}")
    print()

    if dry_run:
        print("  [DRY RUN] Would generate content for these stories:")
        for i, s in enumerate(selected, 1):
            theme = THEME_ORDER[(i - 1) % len(THEME_ORDER)]
            shape = match_shape(s["title"], s.get("summary", ""))
            template = pick_best_template(s)
            print(f"    Story {i}: carousel ({theme} theme, {shape} shape)")
            print(f"             caption ({template} template)")
            if do_spanish:
                print(f"             + Spanish translation")
            if i <= num_reels:
                print(f"             + reel script" + (" + TTS" if do_tts else ""))
        print(f"\n  Output would be: {out_dir}/")
        return

    # ---------------------------------------------------------------
    # STEP 3: SAVE STORIES
    # ---------------------------------------------------------------
    stories_path = out_dir / "stories.json"
    with open(stories_path, "w") as f:
        json.dump(selected, f, indent=2, default=str)
    print(f"  Saved stories -> {stories_path}")

    # Track what we generate
    generated = {
        "carousels": [],
        "captions_en": [],
        "captions_es": [],
        "reels": [],
        "tts": [],
    }

    # ---------------------------------------------------------------
    # STEP 4: GENERATE CAROUSELS
    # ---------------------------------------------------------------
    print(f"\n[3/9] GENERATING CAROUSELS...")
    for i, story in enumerate(selected, 1):
        theme = THEME_ORDER[(i - 1) % len(THEME_ORDER)]
        shape = match_shape(story["title"], story.get("summary", ""))

        title = clean_html(story["title"])
        body = clean_html(story.get("summary", ""))
        source = story.get("source", "")
        impact = story.get("impact", "MEDIUM")
        mentions = story.get("mentions", []) or []

        # Build shape text from a key sentence
        shape_text_content = ""
        if body and len(body) > 40:
            shape_text_content = body[:150]

        html = generate_carousel_html(
            headline=title,
            body=body,
            source=source,
            impact=impact,
            why_matters="",
            key_players=mentions if mentions else None,
            theme_name=theme,
            brand_name="Behike",
            shape_text_content=shape_text_content,
            shape_name=shape,
        )

        carousel_path = out_dir / f"carousel-{i}.html"
        with open(carousel_path, "w") as f:
            f.write(html)

        generated["carousels"].append(str(carousel_path))
        print(f"  [{i}] {theme} theme, {shape} shape -> carousel-{i}.html")

    # ---------------------------------------------------------------
    # STEP 5: GENERATE CAPTIONS
    # ---------------------------------------------------------------
    print(f"\n[4/9] GENERATING CAPTIONS (OPB templates)...")
    for i, story in enumerate(selected, 1):
        template = pick_best_template(story)
        caption = generate_caption(story, template=template)

        # Clean em dashes from output
        caption = caption.replace("\u2014", ".").replace("\u2013", ".")
        while ".." in caption:
            caption = caption.replace("..", ".")

        caption_path = out_dir / f"caption-{i}-en.txt"
        with open(caption_path, "w") as f:
            f.write(caption)

        generated["captions_en"].append(str(caption_path))
        print(f"  [{i}] {OPB_TEMPLATES[template]['name']} template -> caption-{i}-en.txt")

    # ---------------------------------------------------------------
    # STEP 6: GENERATE REEL SCRIPTS
    # ---------------------------------------------------------------
    print(f"\n[5/9] GENERATING REEL SCRIPTS (top {num_reels})...")
    for i, story in enumerate(selected[:num_reels], 1):
        reel_data = generate_reel_script(story, i)

        reel_path = out_dir / f"reel-{i}.json"
        with open(reel_path, "w") as f:
            json.dump(reel_data, f, indent=2)

        generated["reels"].append(str(reel_path))
        print(f"  [{i}] {len(reel_data['scenes'])} scenes, ~{reel_data['metadata']['target_duration']} -> reel-{i}.json")

    # ---------------------------------------------------------------
    # STEP 7: GENERATE TTS
    # ---------------------------------------------------------------
    if do_tts and generated["reels"]:
        print(f"\n[6/9] GENERATING TTS NARRATION...")
        if not KOKORO_MODEL.exists():
            print(f"  Kokoro model not found at {KOKORO_MODEL}")
            print("  Skipping TTS. Install kokoro-onnx and download the model to enable.")
        else:
            for i, reel_path in enumerate(generated["reels"], 1):
                with open(reel_path) as f:
                    reel_data = json.load(f)

                tts_path = out_dir / f"reel-{i}-narration.wav"
                success = generate_tts_for_reel(reel_data, tts_path)
                if success:
                    generated["tts"].append(str(tts_path))
    else:
        print(f"\n[6/9] TTS SKIPPED" + (" (--no-tts)" if args.no_tts else " (no reels)"))

    # ---------------------------------------------------------------
    # STEP 8: GENERATE SPANISH VERSIONS
    # ---------------------------------------------------------------
    if do_spanish:
        print(f"\n[7/9] GENERATING SPANISH TRANSLATIONS...")
        for i, caption_path in enumerate(generated["captions_en"], 1):
            with open(caption_path) as f:
                en_caption = f.read()

            es_caption = translate_to_spanish(en_caption)

            es_path = out_dir / f"caption-{i}-es.txt"
            with open(es_path, "w") as f:
                f.write(es_caption)

            generated["captions_es"].append(str(es_path))
            print(f"  [{i}] -> caption-{i}-es.txt")
    else:
        print(f"\n[7/9] SPANISH TRANSLATIONS SKIPPED (--no-spanish)")

    # ---------------------------------------------------------------
    # STEP 9: GENERATE SUMMARY
    # ---------------------------------------------------------------
    print(f"\n[8/9] GENERATING SUMMARY...")
    summary_lines = [
        f"# AI News Pipeline Output -- {today}",
        f"",
        f"Generated at {datetime.now().strftime('%H:%M:%S')}",
        f"",
        f"## Stories Selected ({len(selected)})",
        f"",
    ]
    for i, s in enumerate(selected, 1):
        summary_lines.append(f"{i}. [{s['impact']}] {s['title']}")
        summary_lines.append(f"   Source: {s['source']}")
        summary_lines.append(f"   URL: {s.get('url', 'N/A')}")
        summary_lines.append(f"")

    summary_lines.append(f"## Generated Content")
    summary_lines.append(f"")
    summary_lines.append(f"- Carousels: {len(generated['carousels'])}")
    summary_lines.append(f"- Captions (EN): {len(generated['captions_en'])}")
    summary_lines.append(f"- Captions (ES): {len(generated['captions_es'])}")
    summary_lines.append(f"- Reel scripts: {len(generated['reels'])}")
    summary_lines.append(f"- TTS narrations: {len(generated['tts'])}")
    summary_lines.append(f"")

    summary_lines.append(f"## Files")
    summary_lines.append(f"")
    all_files = (
        generated["carousels"] + generated["captions_en"] +
        generated["captions_es"] + generated["reels"] + generated["tts"]
    )
    for fp in sorted(all_files):
        summary_lines.append(f"- {Path(fp).name}")
    summary_lines.append(f"")

    summary_lines.append(f"## Manual Steps Required")
    summary_lines.append(f"")
    summary_lines.append(f"1. Open carousel HTML files in browser")
    summary_lines.append(f"2. Screenshot each 1080x1080 slide")
    summary_lines.append(f"3. Review and edit captions as needed")
    summary_lines.append(f"4. Post to Instagram @behikeai")
    if generated["reels"]:
        summary_lines.append(f"5. Run reel scripts through make_reel.py for full video production")
    summary_lines.append(f"")

    summary_text = "\n".join(summary_lines)
    summary_path = out_dir / "summary.md"
    with open(summary_path, "w") as f:
        f.write(summary_text)
    print(f"  -> {summary_path}")

    # ---------------------------------------------------------------
    # STEP 10: PRINT FINAL REPORT
    # ---------------------------------------------------------------
    print(f"\n[9/9] DONE.")
    print()
    print("=" * 60)
    print(f"  PIPELINE COMPLETE -- {today}")
    print("=" * 60)
    print()
    print(f"  Output: {out_dir}/")
    print()
    print(f"  Stories:     {len(selected)}")
    print(f"  Carousels:   {len(generated['carousels'])}")
    print(f"  Captions EN: {len(generated['captions_en'])}")
    print(f"  Captions ES: {len(generated['captions_es'])}")
    print(f"  Reel scripts:{len(generated['reels'])}")
    print(f"  TTS audio:   {len(generated['tts'])}")
    print()

    total_files = len(all_files) + 2  # +2 for stories.json and summary.md
    print(f"  Total files: {total_files}")
    print()

    print("  NEXT STEPS:")
    print("  1. Open carousel-*.html in browser, screenshot each slide")
    print("  2. Review captions, pick EN or ES version")
    print("  3. Post to @behikeai on Instagram")
    if generated["reels"]:
        print("  4. Run reel production:")
        for reel_path in generated["reels"]:
            name = Path(reel_path).stem
            print(f"     python3 tools/reel-pipeline/make_reel.py --story {reel_path}")
    print()
    print("=" * 60)
    print()


def main():
    parser = argparse.ArgumentParser(
        description="Behike AI News Instagram Pipeline -- One command, full daily content."
    )
    parser.add_argument("--daily", action="store_true", default=True,
                        help="Run full pipeline (default)")
    parser.add_argument("--fetch-only", action="store_true",
                        help="Just fetch RSS, no content generation")
    parser.add_argument("--stories", type=int, default=5,
                        help="Number of stories to process (default: 5)")
    parser.add_argument("--reels", type=int, default=2,
                        help="Number of reel scripts to generate (default: 2)")
    parser.add_argument("--no-tts", action="store_true",
                        help="Skip TTS narration generation")
    parser.add_argument("--no-spanish", action="store_true",
                        help="Skip Spanish translations")
    parser.add_argument("--dry-run", action="store_true",
                        help="Show what would be generated without doing it")

    args = parser.parse_args()
    run_pipeline(args)


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
Translate story JSONs for multi-language reel production.
Creates parallel story files with translated narration text.

Uses the local Ollama model for translation (free, runs on Ceiba or Cobo).
Falls back to simple marker-based approach if Ollama is unavailable.

Usage:
    python3 translate_stories.py --lang es              # translate all to Spanish
    python3 translate_stories.py --lang es --story the-lunchbox-note
    python3 translate_stories.py --lang pt              # Portuguese
    python3 translate_stories.py --list                 # show what exists
"""
import json, sys, os, urllib.request, urllib.error
from pathlib import Path

PIPELINE_DIR = Path(__file__).parent
STORIES_DIR = PIPELINE_DIR / "stories"

# Ollama endpoints to try (Ceiba local, then Cobo)
OLLAMA_URLS = [
    "http://localhost:11434",
    "http://192.168.0.151:11434",
]

LANG_NAMES = {
    "en": "English",
    "es": "Spanish",
    "pt": "Brazilian Portuguese",
}

# TTS voice mapping per language
VOICES = {
    "en": {"female": "af_heart", "male": "am_adam"},
    "es": {"female": "ef_dora", "male": "em_alex"},
    "pt": {"female": "pf_dora", "male": "pm_alex"},
}


def ollama_translate(text, target_lang, model="qwen2.5:7b"):
    """Translate text using local Ollama."""
    lang_name = LANG_NAMES.get(target_lang, target_lang)
    prompt = (
        f"Translate the following text to {lang_name}. "
        f"Keep the same emotional tone and poetic style. "
        f"Only output the translation, nothing else.\n\n{text}"
    )

    for base_url in OLLAMA_URLS:
        try:
            payload = json.dumps({
                "model": model,
                "prompt": prompt,
                "stream": False,
            }).encode("utf-8")

            req = urllib.request.Request(
                f"{base_url}/api/generate",
                data=payload,
                headers={"Content-Type": "application/json"},
                method="POST",
            )
            resp = urllib.request.urlopen(req, timeout=120)
            result = json.loads(resp.read())
            translated = result.get("response", "").strip()
            if translated:
                return translated
        except Exception:
            continue

    return None


def translate_story(story_path, target_lang):
    """Translate a story JSON file to the target language."""
    with open(story_path) as f:
        story = json.load(f)

    name = story_path.stem
    output_name = f"{name}_{target_lang}.json"
    output_path = STORIES_DIR / output_name

    if output_path.exists():
        print(f"  [SKIP] {output_name} already exists")
        return output_path

    print(f"  [TRANSLATE] {name} -> {target_lang}")

    # Translate narration
    narration = story.get("narration", "")
    if not narration:
        narration = " ".join(s["text"] for s in story.get("scenes", []))

    translated_narration = ollama_translate(narration, target_lang)
    if not translated_narration:
        print(f"  [ERROR] Translation failed for {name}")
        return None

    # Translate scene texts
    translated_scenes = []
    for scene in story.get("scenes", []):
        translated_text = ollama_translate(scene["text"], target_lang)
        translated_scenes.append({
            "text": translated_text or scene["text"],
            "image_prompt": scene.get("image_prompt", ""),  # Keep English for image gen
        })

    # Build translated story
    translated_story = {
        "title": story.get("title", name),
        "narration": translated_narration,
        "scenes": translated_scenes,
        "lang": target_lang,
        "source": name,
        "voice": VOICES.get(target_lang, VOICES["en"])["female"],
    }

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(translated_story, f, indent=2, ensure_ascii=False)

    print(f"  [DONE] {output_name}")
    return output_path


def list_stories():
    """List all stories and their translations."""
    base_stories = sorted(f for f in STORIES_DIR.glob("*.json")
                          if not any(f.stem.endswith(f"_{lang}") for lang in LANG_NAMES))
    print(f"Stories: {len(base_stories)}")
    for s in base_stories:
        translations = []
        for lang in LANG_NAMES:
            if lang == "en":
                continue
            trans_path = STORIES_DIR / f"{s.stem}_{lang}.json"
            if trans_path.exists():
                translations.append(lang)
        trans_str = f" [{', '.join(translations)}]" if translations else ""
        print(f"  {s.stem}{trans_str}")


def main():
    if "--list" in sys.argv:
        list_stories()
        return

    target_lang = "es"
    story_filter = None

    for i, arg in enumerate(sys.argv[1:], 1):
        if arg == "--lang" and i < len(sys.argv) - 1:
            target_lang = sys.argv[i + 1]
        if arg == "--story" and i < len(sys.argv) - 1:
            story_filter = sys.argv[i + 1]

    if target_lang not in LANG_NAMES or target_lang == "en":
        print(f"Supported languages: {', '.join(k for k in LANG_NAMES if k != 'en')}")
        return

    print(f"Translating to {LANG_NAMES[target_lang]}...")

    # Find base stories (not already translations)
    stories = sorted(f for f in STORIES_DIR.glob("*.json")
                     if not any(f.stem.endswith(f"_{lang}") for lang in LANG_NAMES))

    if story_filter:
        stories = [s for s in stories if s.stem == story_filter]

    if not stories:
        print("No stories found.")
        return

    success = 0
    for story_path in stories:
        result = translate_story(story_path, target_lang)
        if result:
            success += 1

    print(f"\nTranslated {success}/{len(stories)} stories to {LANG_NAMES[target_lang]}")


if __name__ == "__main__":
    main()

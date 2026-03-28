#!/usr/bin/env python3
"""
Story Writer - Create new reel stories quickly.
Generates the story JSON with narration text and image prompts.

Usage:
    python3 write_story.py "The Song That Plays" "There's a song I can't listen to anymore..."
    python3 write_story.py --from-text story.txt   # convert prose to story JSON
"""

import json
import sys
import re
from pathlib import Path

PIPELINE_DIR = Path(__file__).parent
STORIES_DIR = PIPELINE_DIR / "stories"


def text_to_story(title, narration):
    """Convert a narration text into a structured story with scenes and image prompts."""
    # Split narration into sentences
    sentences = re.split(r'(?<=[.!?])\s+', narration.strip())

    # Group sentences into 4-6 scenes
    num_scenes = min(max(len(sentences) // 2, 3), 6)  # 3-6 scenes
    scenes_per_group = len(sentences) / num_scenes

    scenes = []
    for i in range(num_scenes):
        start = int(i * scenes_per_group)
        end = int((i + 1) * scenes_per_group)
        scene_text = ' '.join(sentences[start:end])

        # Generate an image prompt based on the scene text
        image_prompt = generate_image_prompt(scene_text, i, num_scenes)

        scenes.append({
            "text": scene_text,
            "image_prompt": image_prompt,
        })

    story = {
        "title": title,
        "narration": narration.strip(),
        "scenes": scenes,
    }

    return story


def generate_image_prompt(text, scene_idx, total_scenes):
    """
    Generate a cinematic image prompt from scene text.
    Uses keywords and emotional cues to create visual descriptions.
    """
    text_lower = text.lower()

    # Detect emotional tone
    if any(w in text_lower for w in ['cry', 'tear', 'miss', 'gone', 'lost', 'passed']):
        mood = "deeply emotional, melancholic, cinematic"
    elif any(w in text_lower for w in ['laugh', 'smile', 'happy', 'joy', 'love']):
        mood = "warm, joyful, soft golden light, cinematic"
    elif any(w in text_lower for w in ['remember', 'used to', 'back when', 'those days']):
        mood = "nostalgic, warm vintage tones, cinematic"
    elif any(w in text_lower for w in ['quiet', 'still', 'alone', 'empty', 'silence']):
        mood = "quiet, contemplative, soft diffused light, cinematic"
    else:
        mood = "warm, emotional, cinematic lighting"

    # Detect subjects
    subjects = []
    if any(w in text_lower for w in ['mom', 'mother', 'mama']):
        subjects.append("a mother figure")
    if any(w in text_lower for w in ['dad', 'father', 'papa', 'papi']):
        subjects.append("a father figure")
    if any(w in text_lower for w in ['grandma', 'grandmother', 'abuela']):
        subjects.append("an elderly grandmother")
    if any(w in text_lower for w in ['kid', 'child', 'young', 'little']):
        subjects.append("a child")
    if any(w in text_lower for w in ['kitchen', 'cook', 'food', 'recipe']):
        subjects.append("a warm kitchen setting")
    if any(w in text_lower for w in ['phone', 'call', 'voicemail', 'text']):
        subjects.append("a phone close-up")
    if any(w in text_lower for w in ['house', 'home', 'room', 'door']):
        subjects.append("a home interior")
    if any(w in text_lower for w in ['car', 'drive', 'road', 'truck']):
        subjects.append("a vehicle or road scene")
    if any(w in text_lower for w in ['school', 'class', 'teacher']):
        subjects.append("a school setting")

    # Build prompt
    subject_str = ", ".join(subjects[:2]) if subjects else "a person in a quiet moment"

    # Camera angle varies by scene position
    if scene_idx == 0:
        angle = "establishing wide shot"
    elif scene_idx == total_scenes - 1:
        angle = "intimate close-up, shallow depth of field"
    elif scene_idx % 2 == 0:
        angle = "medium shot, natural framing"
    else:
        angle = "close-up detail shot, macro"

    prompt = f"{subject_str}, {angle}, {mood}, 4k"
    return prompt


def save_story(title, story):
    """Save story JSON to stories directory."""
    slug = title.lower().strip()
    slug = re.sub(r'[^a-z0-9]+', '-', slug).strip('-')

    STORIES_DIR.mkdir(parents=True, exist_ok=True)
    filepath = STORIES_DIR / f"{slug}.json"

    with open(filepath, 'w') as f:
        json.dump(story, f, indent=2)

    print(f"Saved: {filepath}")
    print(f"Scenes: {len(story['scenes'])}")
    print(f"Run: python3 full_pipeline.py {slug}")
    return filepath


def main():
    if len(sys.argv) < 2:
        print("Usage:")
        print('  python3 write_story.py "Title" "Full narration text..."')
        print('  python3 write_story.py --from-text story.txt')
        sys.exit(1)

    if sys.argv[1] == "--from-text":
        filepath = sys.argv[2]
        with open(filepath) as f:
            lines = f.read().strip().split('\n')
        title = lines[0].strip('#').strip()
        narration = ' '.join(lines[1:]).strip()
    else:
        title = sys.argv[1]
        if len(sys.argv) > 2:
            narration = ' '.join(sys.argv[2:])
        else:
            print("Enter narration (paste text, then press Ctrl+D):")
            narration = sys.stdin.read()

    story = text_to_story(title, narration)
    save_story(title, story)

    # Preview
    print(f"\nPreview:")
    for i, scene in enumerate(story["scenes"]):
        print(f"\n  Scene {i}: {scene['text'][:60]}...")
        print(f"  Image: {scene['image_prompt'][:60]}...")


if __name__ == "__main__":
    main()

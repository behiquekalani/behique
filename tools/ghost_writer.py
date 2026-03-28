#!/usr/bin/env python3
# Copyright 2026 Behike. All rights reserved.
"""
Ghost Writer Engine - Write content in Kalani/Behike's voice.
Uses the Voice Bible rules + optional corpus for style matching.
Runs voice_checker.py on all output automatically.

Usage:
    python3 ghost_writer.py --type twitter --topic "AI tools for solopreneurs"
    python3 ghost_writer.py --type newsletter --topic "First 100 Instagram followers"
    python3 ghost_writer.py --type instagram --topic "Why I quit Notion"
    python3 ghost_writer.py --type youtube-script --topic "Claude Code vs Cursor"
    python3 ghost_writer.py --type email --topic "New product launch"
    python3 ghost_writer.py --type tiktok --topic "Running 5 AI agents locally"
    python3 ghost_writer.py --corpus samples/my-posts/ --type twitter --topic "anything"
    python3 ghost_writer.py --type twitter --topic "AI tools" --output draft.md
    python3 ghost_writer.py --type twitter --topic "AI tools" --fix
"""

import argparse
import os
import subprocess
import sys
import tempfile
from pathlib import Path

# --- Paths ---
TOOLS_DIR = Path(__file__).parent
PROJECT_DIR = TOOLS_DIR.parent
VOICE_CHECKER = TOOLS_DIR / "voice_checker.py"

# --- Content type definitions ---
CONTENT_TYPES = ["twitter", "instagram", "newsletter", "youtube-script", "email", "tiktok"]

# --- Voice Bible: hardcoded from Ceiba/projects/content-empire/voice-bible.md ---
# Keep in sync with that file. Last updated: 2026-03-22.

BANNED_WORDS = """
BANNED WORDS AND PHRASES (never use any of these):
- em dashes (use periods or commas instead)
- exclamation marks (1 max per piece, only for genuine surprise)
- "game-changing" / "game-changer" / "revolutionary" / "transformative"
- "unlock" (as in unlock potential / unlock growth / unlock success)
- "leverage" in the Instagram-guru sense
- "certainly" / "absolutely" / "of course" (AI tells)
- "excited to share" / "thrilled to announce" / "excited to announce"
- "deep dive" (use "close look" instead)
- "hustle" as a virtue word
- "grind" as a virtue word
- "passive income" (overused, signals low quality)
- "guru" / "expert" / "thought leader"
- "pain points" (use "problems" instead)
- "low-hanging fruit" (use "easy wins" instead)
- "paradigm shift" (use "change" instead)
- "synergy" (use "teamwork" instead)
- "empower" / "empowering" (use "help" instead)
- "streamline" / "streamlining" (use "simplify" instead)
- "robust" (use "solid" instead)
- "cutting-edge" / "cutting edge" (use "new" instead)
- "seamlessly" / "seamless" (use "smoothly" / "smooth" instead)
- "As an AI" or any variant
- "Certainly, here's..."
- "let's dive in" / "let's dive deep"
- "in today's fast-paced world"
- "unlock your potential"
- "here's the thing" (overused)
- "the truth is" (overused)
- "most people don't realize" (assumes reader is ignorant)
- "what if I told you"
"""

STYLE_RULES = """
STYLE RULES:
1. Short sentences. One idea per sentence. Thesis first.
2. Rhythm: short, short, slightly longer sentence that carries the weight, short again.
3. Paragraphs: 1-3 sentences max. Never more than 4 lines on a phone screen.
4. Journalist tone, not influencer tone. Builder-to-builder. Personal but never emotional.
5. Specific numbers over vague claims. "3 scripts" not "a few scripts."
6. No hype. No promises. No "this will change your life."
7. Never start a sentence with "I." Lead with the observation, the number, or the claim.
   Wrong: "I built a system that replaces a marketing team."
   Right: "Three scripts replaced my marketing team. Here's what they do."
8. Openings: never use empathy bait. No "Are you tired of..." No "Does this sound familiar?"
9. Closings: don't summarize. Don't say "in conclusion." End on a forward-looking statement,
   a single honest line, or a specific CTA. Never generic ("Follow for more!").
10. Lists: only when 3+ items are genuinely parallel. Never use bullets just to look organized.
11. One idea per paragraph. Not two. One.
"""

PERSONALITY = """
PERSONALITY (write from this perspective):
- Precise: numbers over adjectives, specific over vague
- Calm: never reactive, never hype, energy of someone who already did the thing
- Philosophical: sees patterns across systems, not just the task in front of them
- Honest: includes failures, doesn't promise results, says "here's what I built" not "here's the formula"
- Builder: thinks in systems and pipelines, not tips and tricks
- Caribbean (Puerto Rican): not American hustle, not European minimalism, something older and more rooted
- Understated: the most important thing gets one sentence, not an exclamation mark
"""

PREFERRED_VOCAB = """
PREFERRED VOCABULARY:
- "built" (not "created" or "developed")
- "ship" (not "launch" or "release")
- "runs" (not "executes" or "performs")
- "stack" (not "toolkit" or "suite")
- "pipeline" (not "workflow" or "process")
- "honest take" / "honest answer"
- "here's what I found" / "here's how it works"
- "actually" (sparingly, for genuine emphasis)
- "zero" (not "none" or "no")
"""

STYLE_EXAMPLES = """
STYLE EXAMPLES (calibrate to these):

Example 1 (Instagram, product):
  Three computers. Six AI agents. Zero employees.

  That's the setup I built to run my entire content pipeline without hiring anyone.

  The AI Employee Guide breaks down every tool, every connection, and every workflow I use.

  It's not theory. It's the actual setup. Screenshots included.

  Link in bio.

Example 2 (Twitter/X thread opener, insight):
  Most people use AI like a search engine with better grammar.

  They type in a question. They get an answer. They copy and paste it.

  That's not leverage. That's a fancy autocomplete.

  Here's the difference between using AI and deploying AI.

Example 3 (YouTube hook, educational):
  You don't need a GPU server. You don't need an API subscription.

  I'm going to show you how I run five AI tools locally, on a MacBook and an old Windows PC,
  for zero dollars a month.

  Let's start with the install.

Example 4 (Product description):
  Most guides on AI automation are written by people who haven't actually built anything.

  This one is different.

  The Prompt Engineering Cheat Sheet is the exact reference I use. Forty patterns. Real examples.
  The mistakes that actually kill output quality.

  If you've ever gotten generic answers from ChatGPT or Claude, this is why.

Example 5 (Newsletter opening, personal):
  This week I almost didn't ship anything.

  The project felt too big. The scope kept expanding. Every time I solved one problem, two more appeared.

  Here's what I learned about shipping when you don't feel ready.

Example 6 (Instagram, personal story):
  My abuela never owned a computer.

  She ran a whole neighborhood business from memory. Names, debts, birthdays. Everything.

  I think about her when I build AI systems. The technology is different. The skill is the same:
  keeping track of what matters for the people who matter.

  That's what I'm trying to build.

Example 7 (Twitter, contrarian):
  The AI tools everyone recommends in 2026 are mostly the same tool with different branding.

  Here's the actual stack that runs my business. Most of it you've never heard of.
"""

# --- Platform-specific instructions ---
PLATFORM_INSTRUCTIONS = {
    "twitter": """
FORMAT: Twitter/X thread
- 8-12 tweets, numbered: 1/, 2/, etc.
- First tweet is a thesis statement, not a question.
- Each tweet is a standalone point, not setup for the next.
- Final tweet ends on something quotable. Not a summary.
- Separate each tweet with a blank line.
- No "RT if you agree" or "follow for more" type endings.
""",
    "instagram": """
FORMAT: Instagram caption
- 1-3 short paragraphs
- First line is the hook. 6 words max. Must stop the scroll on its own.
- Separate paragraphs with blank lines (for visual breathing room).
- Personal stories get more depth. Product posts stay lean.
- At the end, add HASHTAGS: (5 max, relevant and specific, not generic)
- CTA must be specific. "Link in bio for the full guide" beats "follow for more."
- No hashtag spam inside the caption itself.
""",
    "newsletter": """
FORMAT: Newsletter issue
- Subject line on its own line: SUBJECT: [subject here]
- Personal tone. Like a letter from a builder who happens to know a lot about AI.
- One main idea per issue. Not a roundup.
- Can be vulnerable. Can be uncertain. That's the point.
- Start with something that happened, then connect it to a bigger idea.
- Sections: opening story or hook, main idea unpacked, one actionable takeaway, personal closing
- 400-700 words total.
- End with a single honest line, not a generic "that's all for today."
""",
    "youtube-script": """
FORMAT: YouTube script
- Use [SECTION: NAME] markers for each section
- Sections: HOOK, INTRO, [MAIN CONTENT sections], CALL TO ACTION
- First 15 seconds: the promise and the hook. No "welcome back to my channel." No intro.
- Talk to one viewer, not a crowd. "You" not "you guys" or "everyone."
- Show don't tell. Walk through the actual thing live where possible.
- End with the specific next step, not a generic "that's all for today."
- Include [B-ROLL:] suggestions in brackets where helpful
- 600-1200 words total (3-6 minute video)
""",
    "email": """
FORMAT: Marketing or nurture email
- Subject line: SUBJECT: [subject here]
- Preview text: PREVIEW: [preview here]
- Personal, direct. One main idea.
- Short paragraphs (2-3 sentences max).
- CTA is specific and single. One ask, not three.
- No fake urgency. No "limited time offer" unless it's actually limited.
- Lead with the outcome, not the table of contents.
- 200-400 words total.
""",
    "tiktok": """
FORMAT: TikTok script
- Use [VO:] for voiceover text and [SCREEN:] for on-screen text/visuals
- 30-90 second script
- Hook in the first 3 seconds. State the payoff immediately.
- Fast pace. Short sentences. One idea per breath.
- On-screen text reinforces key numbers and takeaways.
- End with a specific CTA (follow, comment with X, link in bio for Y).
- Script should feel like you're talking to one person, not performing for a crowd.
""",
}


def load_corpus(corpus_dir: str) -> str:
    """Load writing samples from a directory. Returns formatted excerpts."""
    path = Path(corpus_dir)
    if not path.exists():
        print(f"[WARN] Corpus directory not found: {corpus_dir}")
        return ""

    files = list(path.glob("*.md")) + list(path.glob("*.txt"))
    if not files:
        print(f"[WARN] No .md or .txt files found in corpus: {corpus_dir}")
        return ""

    excerpts = []
    # Take up to 5 files, up to 500 chars each
    for f in files[:5]:
        try:
            text = f.read_text(encoding="utf-8", errors="replace").strip()
            if text:
                excerpt = text[:500]
                if len(text) > 500:
                    excerpt += "..."
                excerpts.append(f"--- from {f.name} ---\n{excerpt}")
        except Exception as e:
            print(f"[WARN] Could not read {f}: {e}")

    if not excerpts:
        return ""

    return "\n\nCORPUS SAMPLES (additional writing style reference from existing work):\n\n" + "\n\n".join(excerpts)


def build_system_prompt(content_type: str, corpus_excerpts: str = "") -> str:
    """Build the full system prompt for a given content type."""
    platform_instruction = PLATFORM_INSTRUCTIONS.get(content_type, "")

    prompt = f"""You are writing content for Kalani Andre, a computer engineering student in Puerto Rico who builds AI tools and digital products. He publishes under the brand Behike.

{PERSONALITY}

{STYLE_RULES}

{PREFERRED_VOCAB}

{BANNED_WORDS}

{STYLE_EXAMPLES}
{corpus_excerpts}

{platform_instruction}

CRITICAL RULES:
- Do not write like an AI. Do not write like a marketing agency.
- If the content sounds like it could have been written by any AI automation brand, rewrite it.
- Behike content sounds like it was written by one specific person from Puerto Rico who has thought carefully about what he is building and why.
- That specificity is the moat. Do not lose it.
- Output only the content itself. No preamble like "Here's your thread:" or "Sure! Here's the content:"
- No commentary after the content either.
"""
    return prompt.strip()


def build_user_prompt(content_type: str, topic: str) -> str:
    """Build the user-facing prompt for content generation."""
    type_labels = {
        "twitter": "Twitter/X thread",
        "instagram": "Instagram caption",
        "newsletter": "newsletter issue",
        "youtube-script": "YouTube video script",
        "email": "marketing email",
        "tiktok": "TikTok script",
    }
    label = type_labels.get(content_type, content_type)
    return f"Write a {label} about: {topic}"


def call_claude(system_prompt: str, user_prompt: str, model: str = "claude-sonnet-4-6") -> str:
    """Call the Anthropic Claude API. Returns generated text."""
    try:
        import anthropic
    except ImportError:
        print("[ERROR] anthropic package not installed.")
        print("  Fix: pip install anthropic")
        sys.exit(1)

    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        # Try loading from .env in project root
        env_file = PROJECT_DIR / ".env"
        if env_file.exists():
            for line in env_file.read_text().splitlines():
                line = line.strip()
                if line.startswith("ANTHROPIC_API_KEY="):
                    api_key = line.split("=", 1)[1].strip().strip('"').strip("'")
                    break

    if not api_key:
        print("[ERROR] ANTHROPIC_API_KEY not found.")
        print()
        print("  Set it in your environment:")
        print("    export ANTHROPIC_API_KEY=sk-ant-...")
        print()
        print("  Or add it to your .env file at:")
        print(f"    {PROJECT_DIR / '.env'}")
        print("    ANTHROPIC_API_KEY=sk-ant-...")
        sys.exit(1)

    client = anthropic.Anthropic(api_key=api_key)

    print(f"  Calling Claude ({model})...", flush=True)

    message = client.messages.create(
        model=model,
        max_tokens=2048,
        system=system_prompt,
        messages=[{"role": "user", "content": user_prompt}],
    )

    return message.content[0].text


def run_voice_check(text: str) -> list:
    """Run voice_checker.py on generated text. Returns violations list."""
    if not VOICE_CHECKER.exists():
        return []

    # Write text to a temp file and check it
    with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False, encoding="utf-8") as f:
        f.write(text)
        tmp_path = f.name

    try:
        result = subprocess.run(
            [sys.executable, str(VOICE_CHECKER), "--check-text", text, "--json"],
            capture_output=True,
            text=True,
        )
        import json
        try:
            data = json.loads(result.stdout)
            return data.get("violations", [])
        except json.JSONDecodeError:
            return []
    finally:
        Path(tmp_path).unlink(missing_ok=True)


def fix_voice_violations(text: str) -> tuple:
    """Use voice_checker fix_text to auto-fix violations. Returns (fixed_text, changes)."""
    # Import inline to avoid circular issues
    sys.path.insert(0, str(TOOLS_DIR))
    try:
        from voice_checker import fix_text
        return fix_text(text)
    except ImportError:
        print("[WARN] Could not import voice_checker for auto-fix.")
        return text, []


def print_voice_report(violations: list):
    """Print a clean voice check summary."""
    if not violations:
        print("  Voice check: CLEAN. No violations found.")
        return

    hard = [v for v in violations if v.get("severity") == "hard"]
    soft = [v for v in violations if v.get("severity") == "soft"]

    print(f"  Voice check: {len(violations)} violations ({len(hard)} hard, {len(soft)} soft)")

    if hard:
        print("  Hard violations (must fix):")
        for v in hard:
            print(f"    \"{v['phrase']}\" -> {v['replacement']}")

    if soft:
        print("  Soft violations (review):")
        for v in soft:
            print(f"    \"{v['phrase']}\"")


def main():
    parser = argparse.ArgumentParser(
        description="Ghost Writer Engine. Write content in Kalani/Behike's voice. Copyright 2026 Behike.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python3 ghost_writer.py --type twitter --topic "AI tools for solopreneurs"
  python3 ghost_writer.py --type newsletter --topic "First 100 Instagram followers"
  python3 ghost_writer.py --type instagram --topic "Why I quit Notion"
  python3 ghost_writer.py --type youtube-script --topic "Claude Code vs Cursor"
  python3 ghost_writer.py --type email --topic "New product launch"
  python3 ghost_writer.py --type tiktok --topic "Running 5 AI agents locally"
  python3 ghost_writer.py --corpus samples/my-posts/ --type twitter --topic "AI tools"
  python3 ghost_writer.py --type twitter --topic "AI tools" --output draft.md
  python3 ghost_writer.py --type twitter --topic "AI tools" --fix
        """,
    )

    parser.add_argument(
        "--type",
        required=True,
        choices=CONTENT_TYPES,
        metavar="TYPE",
        help=f"Content type to generate. Options: {', '.join(CONTENT_TYPES)}",
    )
    parser.add_argument(
        "--topic",
        required=True,
        type=str,
        help="Topic or brief for the content (e.g. 'AI tools for solopreneurs')",
    )
    parser.add_argument(
        "--corpus",
        type=str,
        default=None,
        help="Path to directory of .md or .txt writing samples for style matching",
    )
    parser.add_argument(
        "--output",
        type=str,
        default=None,
        help="Optional file path to save output (in addition to terminal)",
    )
    parser.add_argument(
        "--fix",
        action="store_true",
        help="Auto-fix any Voice Bible violations in the output",
    )
    parser.add_argument(
        "--model",
        type=str,
        default="claude-sonnet-4-6",
        help="Claude model to use (default: claude-sonnet-4-6)",
    )
    parser.add_argument(
        "--no-voice-check",
        action="store_true",
        help="Skip Voice Bible violation check on output",
    )

    args = parser.parse_args()

    print()
    print(f"  Ghost Writer Engine")
    print(f"  Type:  {args.type}")
    print(f"  Topic: {args.topic}")
    if args.corpus:
        print(f"  Corpus: {args.corpus}")
    print()

    # Load optional corpus
    corpus_excerpts = ""
    if args.corpus:
        corpus_excerpts = load_corpus(args.corpus)
        if corpus_excerpts:
            corpus_count = corpus_excerpts.count("--- from ")
            print(f"  Loaded {corpus_count} corpus sample(s).")
        print()

    # Build prompts
    system_prompt = build_system_prompt(args.type, corpus_excerpts)
    user_prompt = build_user_prompt(args.type, args.topic)

    # Generate content
    output = call_claude(system_prompt, user_prompt, model=args.model)
    print()

    # Run voice check
    violations = []
    if not args.no_voice_check:
        violations = run_voice_check(output)
        print_voice_report(violations)
        print()

    # Auto-fix if requested or if hard violations exist and --fix was passed
    if args.fix and violations:
        hard_violations = [v for v in violations if v.get("severity") == "hard"]
        if hard_violations:
            output, changes = fix_voice_violations(output)
            if changes:
                print(f"  Auto-fixed {sum(c.get('count', 1) for c in changes)} violation(s).")
                # Re-check after fix
                violations_after = run_voice_check(output)
                remaining = len([v for v in violations_after if v.get("severity") == "hard"])
                if remaining == 0:
                    print("  Voice check after fix: CLEAN.")
                else:
                    print(f"  Voice check after fix: {remaining} hard violations remaining (manual review needed).")
                print()

    # Print separator and output
    print("  " + "=" * 60)
    print()
    print(output)
    print()
    print("  " + "=" * 60)

    # Save to file if requested
    if args.output:
        out_path = Path(args.output)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(output, encoding="utf-8")
        print()
        print(f"  Saved to: {out_path.resolve()}")

    print()

    # Exit with code 1 if hard violations remain (useful for CI/scripts)
    remaining_hard = [v for v in violations if v.get("severity") == "hard"]
    if remaining_hard and not args.fix:
        print(f"  {len(remaining_hard)} hard Voice Bible violation(s) in output.")
        print(f"  Re-run with --fix to auto-correct.")
        print()
        sys.exit(1)

    sys.exit(0)


if __name__ == "__main__":
    main()

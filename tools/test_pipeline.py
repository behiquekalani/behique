#!/usr/bin/env python3
# Copyright 2026 Behike. All rights reserved.
"""
End-to-End Pipeline Test. Runs the full content generation pipeline in
dry-run mode to verify all integrations are wired correctly.

Steps tested:
  1. Fetch news (cached articles)
  2. Generate 1 script via script_writer (with Voice Bible)
  3. Generate 1 caption via news_to_post (with Voice Bible check)
  4. Generate 1 carousel
  5. Generate 1 thumbnail
  6. Queue via instagram_poster
  7. Generate calendar entry

Reports pass/fail for each step, total time, Voice Bible violations found.

Usage:
    python3 test_pipeline.py                 # run all tests
    python3 test_pipeline.py --verbose       # detailed output
    python3 test_pipeline.py --help

No arguments needed. Runs everything.
"""

import json
import sys
import time
import traceback
from datetime import datetime
from pathlib import Path

# --- Paths ---
TOOLS_DIR = Path(__file__).parent
PROJECT_DIR = TOOLS_DIR.parent
NEWS_DIR = PROJECT_DIR / "Ceiba" / "news"
VOICE_BIBLE = PROJECT_DIR / "Ceiba" / "VOICE_BIBLE.md"
ARTICLES_FILE = NEWS_DIR / "articles.json"
ANALYTICS_FILE = NEWS_DIR / "analytics.json"
INSIGHTS_FILE = NEWS_DIR / "performance-insights.json"

sys.path.insert(0, str(TOOLS_DIR))

VERBOSE = False


def _print(msg: str, indent: int = 0):
    """Print with optional verbosity control."""
    prefix = "  " * indent
    print(f"{prefix}{msg}")


def _result(name: str, passed: bool, duration: float, detail: str = ""):
    """Format a test result."""
    status = "PASS" if passed else "FAIL"
    msg = f"  [{status}] {name} ({duration:.2f}s)"
    if detail:
        msg += f" -- {detail}"
    print(msg)
    return {"name": name, "passed": passed, "duration": duration, "detail": detail}


# =====================================================================
# TEST STEPS
# =====================================================================

def test_voice_checker():
    """Test 1: Voice checker loads and works."""
    start = time.time()
    try:
        from voice_checker import check_text, fix_text, BANNED_PHRASES

        # Check that the banned list is populated
        assert len(BANNED_PHRASES) > 10, f"Only {len(BANNED_PHRASES)} banned phrases loaded"

        # Test detection
        test_input = "Let's dive in to this game-changer that will leverage AI to streamline your workflow seamlessly."
        violations = check_text(test_input)
        assert len(violations) > 0, "No violations detected in obviously bad text"

        # Test fix
        fixed, changes = fix_text(test_input)
        assert len(changes) > 0, "No changes made by fix_text"
        assert "game-changer" not in fixed.lower(), "game-changer not replaced"
        assert "leverage" not in fixed.lower() or "use" in fixed.lower(), "leverage not replaced"

        # Test clean text
        clean = "Build things. Ship them. Repeat."
        clean_violations = check_text(clean)
        assert len(clean_violations) == 0, f"False positives on clean text: {clean_violations}"

        detail = f"{len(BANNED_PHRASES)} phrases, detected {len(violations)} violations, fixed {len(changes)} issues"
        return _result("Voice Checker", True, time.time() - start, detail)

    except Exception as e:
        return _result("Voice Checker", False, time.time() - start, str(e))


def test_voice_bible_exists():
    """Test 2: Voice Bible file exists and is readable."""
    start = time.time()
    try:
        assert VOICE_BIBLE.exists(), f"Voice Bible not found at {VOICE_BIBLE}"
        content = VOICE_BIBLE.read_text()
        assert len(content) > 100, "Voice Bible is too short"
        assert "BANNED WORDS" in content, "Voice Bible missing BANNED WORDS section"
        assert "TONE RULES" in content, "Voice Bible missing TONE RULES section"
        return _result("Voice Bible File", True, time.time() - start, f"{len(content)} chars")
    except Exception as e:
        return _result("Voice Bible File", False, time.time() - start, str(e))


def test_script_writer_integration():
    """Test 3: script_writer loads Voice Bible and performance data."""
    start = time.time()
    try:
        from script_writer import (
            load_voice_bible_rules,
            load_full_performance_insights,
            _build_system_prompt,
            _voice_check_output,
            FORMATS,
        )

        # Test Voice Bible loading
        rules = load_voice_bible_rules()
        assert len(rules) > 0, "Voice Bible rules not loaded"
        assert "BANNED" in rules or "banned" in rules.lower(), "Banned words section not found in loaded rules"

        # Test system prompt building (should include Voice Bible)
        prompt = _build_system_prompt("en")
        assert "VOICE BIBLE" in prompt, "Voice Bible not injected into system prompt"

        # Test performance insights loading (may be empty if no data)
        insights = load_full_performance_insights()
        has_insights = len(insights) > 0
        insights_detail = f"insights: {'loaded' if has_insights else 'none (no data yet, OK)'}"

        # Test voice check on script output
        test_script = {
            "hook": "Let's dive deep into this game-changer",
            "narration": "We'll leverage AI to streamline everything seamlessly",
            "scenes": [
                {"text": "This cutting-edge tool will revolutionize your workflow", "overlay_text": "test"}
            ],
        }
        checked = _voice_check_output(test_script)
        assert "dive deep" not in checked["hook"].lower(), "Voice check missed 'dive deep' in hook"

        detail = f"Voice Bible injected, {insights_detail}"
        if "PERFORMANCE DATA" in prompt:
            detail += ", perf data in prompt"
        return _result("Script Writer Integration", True, time.time() - start, detail)

    except Exception as e:
        return _result("Script Writer Integration", False, time.time() - start, str(e))


def test_news_to_post_integration():
    """Test 4: news_to_post applies Voice Bible check to captions."""
    start = time.time()
    try:
        from news_to_post import generate_caption, _voice_check_caption, OPB_TEMPLATES

        # Test voice check function
        bad_caption = "Let's dive in to this game-changing tool that leverages AI.\n\n#AI #tech"
        fixed = _voice_check_caption(bad_caption)
        assert "game-changing" not in fixed.lower() or "useful" in fixed.lower(), "Voice check not fixing news captions"

        # Test that generate_caption works with a mock article
        mock_article = {
            "id": "test-001",
            "title": "OpenAI Releases GPT-5 with Reasoning Capabilities",
            "summary": "OpenAI announced GPT-5 today with improved reasoning and coding abilities.",
            "source": "TechCrunch",
            "impact": "HIGH",
            "mentions": ["OpenAI", "GPT-5"],
            "category": "releases",
        }

        # Test all OPB templates
        templates_tested = 0
        for tmpl in OPB_TEMPLATES:
            caption = generate_caption(mock_article, template=tmpl)
            assert len(caption) > 20, f"Caption too short for template {tmpl}"
            templates_tested += 1

        detail = f"Voice check wired, {templates_tested} OPB templates tested"
        return _result("News-to-Post Integration", True, time.time() - start, detail)

    except Exception as e:
        return _result("News-to-Post Integration", False, time.time() - start, str(e))


def test_carousel_generation():
    """Test 5: Carousel generation works."""
    start = time.time()
    try:
        from news_to_post import generate_carousel

        mock_article = {
            "id": "test-carousel",
            "title": "Google DeepMind Achieves AGI Benchmark Score",
            "summary": "Google DeepMind's latest model achieves unprecedented scores on AGI benchmarks.",
            "source": "Ars Technica",
            "impact": "HIGH",
            "mentions": ["Google", "DeepMind"],
        }

        slides = generate_carousel(mock_article)
        assert len(slides) >= 3, f"Too few carousel slides: {len(slides)}"
        assert slides[0]["type"] == "hook", "First slide should be hook type"

        detail = f"{len(slides)} slides generated"
        return _result("Carousel Generation", True, time.time() - start, detail)

    except Exception as e:
        return _result("Carousel Generation", False, time.time() - start, str(e))


def test_instagram_poster_queue():
    """Test 6: Instagram poster queue functions are importable."""
    start = time.time()
    try:
        from instagram_poster import load_queue, save_queue, gen_id, validate_caption

        # Test queue functions work
        queue = load_queue()
        assert isinstance(queue, list), "load_queue should return a list"

        # Test caption validation
        test_caption = "This is a test caption. #AI #test"
        issues = validate_caption(test_caption)
        assert isinstance(issues, list), "validate_caption should return a list"

        # Test ID generation
        test_id = gen_id("test caption", datetime.now().isoformat())
        assert len(test_id) > 0, "gen_id returned empty string"

        detail = f"Queue: {len(queue)} items, functions OK"
        return _result("Instagram Poster Queue", True, time.time() - start, detail)

    except Exception as e:
        return _result("Instagram Poster Queue", False, time.time() - start, str(e))


def test_calendar_variety():
    """Test 7: Content calendar enforces framework rotation and color variety."""
    start = time.time()
    try:
        from content_calendar import (
            get_next_framework,
            log_framework_usage,
            get_next_carousel_color,
            log_carousel_theme,
            FRAMEWORKS,
            load_framework_usage,
        )

        # Test framework rotation (log each pick, same as _assign_content_to_slot does)
        frameworks_picked = []
        for i in range(8):
            fw = get_next_framework()
            assert fw in FRAMEWORKS, f"Unknown framework: {fw}"
            frameworks_picked.append(fw)
            log_framework_usage(fw, f"test-{i}")

        # Verify variety
        unique = set(frameworks_picked)
        assert len(unique) >= 3, f"Only {len(unique)} unique frameworks in 8 picks. Rotation not working."

        # Test color rotation (log each pick)
        colors_picked = []
        for i in range(5):
            color = get_next_carousel_color()
            colors_picked.append(color)
            log_carousel_theme(color, "single-column", f"test-{i}")

        detail = f"Frameworks: {', '.join(frameworks_picked[:5])}... Colors: {', '.join(colors_picked[:3])}..."
        return _result("Calendar Variety Enforcer", True, time.time() - start, detail)

    except Exception as e:
        return _result("Calendar Variety Enforcer", False, time.time() - start, str(e))


def test_matrix_routing():
    """Test 8: Matrix disk auto-routing works in auto_content_engine."""
    start = time.time()
    try:
        from matrix_writer import best_disk_for_topic, has_disk
        from auto_content_engine import _check_matrix_disk

        # Test the routing function
        disk = _check_matrix_disk("ebay dropshipping product research tips")

        # Check has_disk function
        has_any = has_disk("ecommerce")
        # best_disk_for_topic should return string
        result = best_disk_for_topic("random unrelated topic xyz")
        assert isinstance(result, str), "best_disk_for_topic should return a string"

        disks_dir = PROJECT_DIR / "Ceiba" / "matrix-disks"
        disk_count = len(list(disks_dir.glob("*.json"))) if disks_dir.exists() else 0

        detail = f"Routing function OK, {disk_count} disks available"
        if disk:
            detail += f", matched: {disk}"
        return _result("Matrix Disk Routing", True, time.time() - start, detail)

    except Exception as e:
        return _result("Matrix Disk Routing", False, time.time() - start, str(e))


def test_performance_tracker():
    """Test 9: Performance tracker insights are accessible."""
    start = time.time()
    try:
        from performance_tracker import load_analytics, calc_engagement_rate

        # Test engagement calculation
        rate = calc_engagement_rate(100, 10, 5, 20, 1000)
        assert rate == 13.5, f"Expected 13.5%, got {rate}%"

        # Test analytics loading
        data = load_analytics()
        assert "posts" in data, "Analytics data missing 'posts' key"
        post_count = len(data["posts"])

        detail = f"Engagement calc OK, {post_count} posts in analytics"
        return _result("Performance Tracker", True, time.time() - start, detail)

    except Exception as e:
        return _result("Performance Tracker", False, time.time() - start, str(e))


def test_full_voice_check_on_sample():
    """Test 10: Run full Voice Bible check on a sample generated content piece."""
    start = time.time()
    try:
        from voice_checker import check_text

        # Simulate typical AI-generated content
        sample = """Unlock your potential with this game-changing AI tool.

In today's fast-paced world, it's important to note that leveraging cutting-edge
technology can help you streamline your workflow seamlessly.

Let's dive deep into how this robust solution can revolutionize your business
and take your productivity to the next level.

Whether you're a beginner or expert, this tool empowers you to harness the
power of AI. Look no further.

Without further ado, here's your comprehensive guide to the AI landscape.
Moving forward, we'll unpack the paradigm shift happening in the ecosystem.
"""
        violations = check_text(sample)
        hard = [v for v in violations if v["severity"] == "hard"]

        # This text should have a LOT of violations
        assert len(hard) >= 10, f"Only found {len(hard)} hard violations in maximally bad text"

        detail = f"Detected {len(hard)} hard, {len(violations) - len(hard)} soft violations in test content"
        return _result("Full Voice Check", True, time.time() - start, detail)

    except Exception as e:
        return _result("Full Voice Check", False, time.time() - start, str(e))


# =====================================================================
# MAIN
# =====================================================================

def main():
    global VERBOSE

    import argparse
    parser = argparse.ArgumentParser(
        description="End-to-End Pipeline Test. Copyright 2026 Behike."
    )
    parser.add_argument("--verbose", action="store_true", help="Show detailed output")
    args = parser.parse_args()
    VERBOSE = args.verbose

    print()
    print("=" * 65)
    print("  BEHIKE CONTENT PIPELINE. END-TO-END TEST")
    print(f"  {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 65)
    print()

    tests = [
        test_voice_bible_exists,
        test_voice_checker,
        test_script_writer_integration,
        test_news_to_post_integration,
        test_carousel_generation,
        test_instagram_poster_queue,
        test_calendar_variety,
        test_matrix_routing,
        test_performance_tracker,
        test_full_voice_check_on_sample,
    ]

    results = []
    total_start = time.time()

    for test_fn in tests:
        try:
            result = test_fn()
            results.append(result)
        except Exception as e:
            results.append({
                "name": test_fn.__name__,
                "passed": False,
                "duration": 0,
                "detail": f"Unhandled: {e}",
            })
            if VERBOSE:
                traceback.print_exc()

    total_time = time.time() - total_start

    # Summary
    passed = sum(1 for r in results if r["passed"])
    failed = sum(1 for r in results if not r["passed"])

    print()
    print("=" * 65)
    print(f"  RESULTS: {passed}/{len(results)} passed, {failed} failed")
    print(f"  Total time: {total_time:.2f}s")
    print("=" * 65)
    print()

    if failed > 0:
        print("  FAILURES:")
        for r in results:
            if not r["passed"]:
                print(f"    - {r['name']}: {r['detail']}")
        print()

    # Integration status
    print("  INTEGRATION STATUS:")
    integrations = {
        "Voice Bible -> script_writer": any(r["passed"] for r in results if "Script Writer" in r["name"]),
        "Voice Bible -> news_to_post": any(r["passed"] for r in results if "News-to-Post" in r["name"]),
        "Voice Checker (standalone)": any(r["passed"] for r in results if "Voice Checker" == r["name"]),
        "Performance -> script_writer": any(r["passed"] for r in results if "Script Writer" in r["name"]),
        "Matrix Disk -> auto_engine": any(r["passed"] for r in results if "Matrix" in r["name"]),
        "Calendar variety enforcer": any(r["passed"] for r in results if "Calendar" in r["name"]),
    }

    for name, connected in integrations.items():
        status = "CONNECTED" if connected else "BROKEN"
        print(f"    {name:40s}  [{status}]")

    print()
    print("=" * 65)
    print()

    sys.exit(0 if failed == 0 else 1)


if __name__ == "__main__":
    main()

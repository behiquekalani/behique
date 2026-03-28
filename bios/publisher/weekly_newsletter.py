#!/usr/bin/env python3
"""
weekly_newsletter.py — Auto-generate weekly Behike newsletter from BIOS data.

Pulls convictions, PR headlines, Fear & Greed index, and formats as
a clean HTML email. Pushes to Beehiiv if API key is set.

CLI:
    python3 weekly_newsletter.py              # generate this week's issue
    python3 weekly_newsletter.py --push       # generate + push to Beehiiv
    python3 weekly_newsletter.py --preview    # open in browser

Cron (Sundays at 6 PM AST):
    0 18 * * 0 cd /Users/kalani/behique/bios/publisher && python3 weekly_newsletter.py --push
"""

import json
import os
import sys
import subprocess
from datetime import datetime, timezone
from pathlib import Path

BIOS_ROOT = Path(__file__).parent.parent
STORAGE = BIOS_ROOT / "storage"
REPORTS = BIOS_ROOT / "reports"
DRAFTS = Path(__file__).parent / "drafts"

# ── Data Loaders ───────────────────────────────────────────────────────────────

def _load_json(path):
    if not path.exists():
        return []
    with open(path) as f:
        return json.load(f)


def load_top_convictions(n=5):
    """Top N convictions by score."""
    data = _load_json(STORAGE / "convictions.json")
    convictions = data.get("convictions", []) if isinstance(data, dict) else data
    return sorted(convictions, key=lambda x: x.get("score", 0), reverse=True)[:n]


def load_pr_headlines(n=3):
    """Top N PR headlines (most recent)."""
    signals = _load_json(STORAGE / "pr_signals.json")
    if not signals:
        return []
    # Deduplicate by title, take most recent
    seen = set()
    unique = []
    for s in signals:
        title = s.get("title", "")
        if title and title not in seen:
            seen.add(title)
            unique.append(s)
    return unique[:n]


def load_fear_greed():
    """Extract Fear & Greed from social signals."""
    signals = _load_json(STORAGE / "social_signals.json")
    for s in signals:
        if s.get("source") == "fear_greed_index":
            title = s.get("title", "")
            try:
                parts = title.split(":")
                rest = parts[1].strip()
                value = int(rest.split("(")[0].strip())
                label = rest.split("(")[1].replace(")", "").strip()
                return {"value": value, "label": label}
            except (IndexError, ValueError):
                pass
    return {"value": 50, "label": "Neutral"}


# ── HTML Template ──────────────────────────────────────────────────────────────

def _conviction_color(level):
    return {
        "HIGH": "#d4a017",
        "MEDIUM": "#888",
        "LOW": "#555",
    }.get(level, "#888")


def _sentiment_bar(sentiment):
    """0-100 sentiment to colored bar."""
    if sentiment >= 60:
        color = "#4CAF50"
    elif sentiment >= 40:
        color = "#d4a017"
    else:
        color = "#e53935"
    width = max(5, min(100, int(sentiment)))
    return f'<div style="background:#222;border-radius:4px;height:8px;width:120px;display:inline-block;vertical-align:middle;"><div style="background:{color};height:8px;border-radius:4px;width:{width}%;"></div></div>'


def _fg_color(value):
    if value <= 25:
        return "#e53935"
    elif value <= 45:
        return "#ff9800"
    elif value <= 55:
        return "#d4a017"
    elif value <= 75:
        return "#8BC34A"
    else:
        return "#4CAF50"


def generate_html(convictions, headlines, fear_greed):
    """Generate the full newsletter HTML."""
    now = datetime.now(timezone.utc)
    week_str = now.strftime("Week of %B %d, %Y")

    # Convictions rows
    conv_rows = ""
    for i, c in enumerate(convictions):
        color = _conviction_color(c.get("level", "MEDIUM"))
        bar = _sentiment_bar(c.get("sentiment", 50))
        conv_rows += f"""
        <tr style="border-bottom:1px solid #222;">
          <td style="padding:14px 16px;color:#f0f0f0;font-size:15px;font-weight:600;">{c['topic'].upper()}</td>
          <td style="padding:14px 16px;text-align:center;">
            <span style="color:{color};font-weight:bold;font-size:18px;">{c['score']:.0f}</span>
            <span style="color:#666;font-size:11px;display:block;">{c.get('level', '')}</span>
          </td>
          <td style="padding:14px 16px;text-align:center;">{bar}</td>
          <td style="padding:14px 16px;color:#666;font-size:12px;text-align:center;">{c.get('signal_count', 0)} signals</td>
        </tr>"""

    # Headlines
    headline_items = ""
    for h in headlines:
        title = h.get("title", "").split(" - ")[0]  # strip source suffix
        source = h.get("source", "").replace("googlenews_pr", "PR Wire")
        headline_items += f"""
        <li style="margin-bottom:12px;">
          <span style="color:#f0f0f0;font-size:14px;">{title}</span>
          <span style="color:#555;font-size:11px;display:block;margin-top:2px;">{source}</span>
        </li>"""

    # Fear & Greed
    fg = fear_greed
    fg_color = _fg_color(fg["value"])

    html = f"""<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Behike Weekly — {week_str}</title>
</head>
<body style="margin:0;padding:0;background:#0a0a0a;font-family:Helvetica,Arial,sans-serif;color:#ccc;">
  <div style="max-width:640px;margin:0 auto;padding:32px 20px;">

    <!-- Header -->
    <div style="text-align:center;padding:40px 0 30px;">
      <h1 style="color:#d4a017;font-size:28px;margin:0;letter-spacing:2px;">BEHIKE</h1>
      <p style="color:#666;font-size:13px;margin:8px 0 0;letter-spacing:1px;">WEEKLY INTELLIGENCE BRIEFING</p>
      <p style="color:#444;font-size:12px;margin:6px 0 0;">{week_str}</p>
    </div>

    <hr style="border:none;border-top:1px solid #222;margin:0 0 30px;">

    <!-- Fear & Greed -->
    <div style="text-align:center;padding:20px 0 30px;">
      <p style="color:#666;font-size:12px;letter-spacing:1px;margin:0 0 12px;">CRYPTO FEAR &amp; GREED INDEX</p>
      <div style="display:inline-block;width:90px;height:90px;border-radius:50%;border:3px solid {fg_color};line-height:90px;text-align:center;">
        <span style="font-size:32px;font-weight:bold;color:{fg_color};">{fg['value']}</span>
      </div>
      <p style="color:{fg_color};font-size:14px;font-weight:bold;margin:10px 0 0;">{fg['label']}</p>
    </div>

    <hr style="border:none;border-top:1px solid #222;margin:0 0 30px;">

    <!-- Top Convictions -->
    <h2 style="color:#d4a017;font-size:16px;letter-spacing:1px;margin:0 0 16px;">TOP CONVICTIONS THIS WEEK</h2>
    <table style="width:100%;border-collapse:collapse;">
      <tr style="border-bottom:1px solid #333;">
        <th style="padding:8px 16px;color:#666;font-size:11px;text-align:left;letter-spacing:1px;">TOPIC</th>
        <th style="padding:8px 16px;color:#666;font-size:11px;text-align:center;letter-spacing:1px;">SCORE</th>
        <th style="padding:8px 16px;color:#666;font-size:11px;text-align:center;letter-spacing:1px;">SENTIMENT</th>
        <th style="padding:8px 16px;color:#666;font-size:11px;text-align:center;letter-spacing:1px;">VOLUME</th>
      </tr>
      {conv_rows}
    </table>

    <div style="height:30px;"></div>

    <!-- PR Headlines -->
    <h2 style="color:#d4a017;font-size:16px;letter-spacing:1px;margin:0 0 16px;">PR HEADLINES</h2>
    <ul style="list-style:none;padding:0;margin:0;">
      {headline_items}
    </ul>

    <hr style="border:none;border-top:1px solid #222;margin:30px 0;">

    <!-- Footer -->
    <div style="text-align:center;padding:20px 0;">
      <p style="color:#444;font-size:11px;margin:0;">
        Powered by BIOS Intelligence Engine<br>
        Data from {len(convictions)} conviction signals across multiple sources
      </p>
      <p style="color:#333;font-size:10px;margin:12px 0 0;">
        You received this because you subscribed to Behike Weekly.<br>
        <a href="{{{{unsubscribe_url}}}}" style="color:#555;">Unsubscribe</a>
      </p>
    </div>

  </div>
</body>
</html>"""
    return html


# ── Main ───────────────────────────────────────────────────────────────────────

def generate_newsletter(push=False):
    """Generate this week's newsletter issue."""
    now = datetime.now(timezone.utc)
    print()
    print("=" * 50)
    print("  BEHIKE WEEKLY — NEWSLETTER GENERATOR")
    print("=" * 50)

    # Load data
    convictions = load_top_convictions(5)
    headlines = load_pr_headlines(3)
    fear_greed = load_fear_greed()

    print(f"  Convictions loaded: {len(convictions)}")
    print(f"  PR headlines:       {len(headlines)}")
    print(f"  Fear & Greed:       {fear_greed['value']} ({fear_greed['label']})")

    # Generate HTML
    html = generate_html(convictions, headlines, fear_greed)

    # Save locally
    DRAFTS.mkdir(parents=True, exist_ok=True)
    date_slug = now.strftime("%Y-%m-%d")
    draft_path = DRAFTS / f"behike-weekly-{date_slug}.html"
    draft_path.write_text(html)
    print(f"\n  Draft saved: {draft_path}")

    # Push to Beehiiv
    if push:
        try:
            from beehiiv_sync import create_post
            title = f"Behike Weekly — {now.strftime('%B %d, %Y')}"
            result = create_post(title, html, status="draft")
            if result.get("post_id"):
                print(f"  Pushed to Beehiiv: {result['post_id']}")
            else:
                print(f"  Beehiiv push skipped: {result.get('error', 'unknown')}")
        except ImportError:
            print("  [warn] beehiiv_sync.py not found — local draft only")
    else:
        api_key = os.environ.get("BEEHIIV_API_KEY", "")
        if api_key:
            print("  [info] API key detected. Use --push to send to Beehiiv.")
        else:
            print("  [info] No BEEHIIV_API_KEY set — local draft only.")

    print()
    return str(draft_path)


def main():
    push = "--push" in sys.argv
    preview = "--preview" in sys.argv

    draft_path = generate_newsletter(push=push)

    if preview:
        # macOS: open in default browser
        try:
            subprocess.run(["open", draft_path], check=True)
            print(f"  Opened in browser: {draft_path}")
        except (subprocess.CalledProcessError, FileNotFoundError):
            print(f"  Open manually: {draft_path}")


if __name__ == "__main__":
    main()

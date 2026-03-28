#!/usr/bin/env python3
"""
BIOS Daily Briefing Generator
Produces an HTML email briefing + terminal summary from all BIOS signal data.

Usage:
    python3 bios/scheduler/daily_briefing.py
    python3 bios/scheduler/daily_briefing.py --send   # future email integration
"""

import json
import os
import sys
import argparse
from datetime import datetime, timezone, timedelta
from pathlib import Path

# ── Paths ──────────────────────────────────────────────────────────────────────
BASE = Path(__file__).resolve().parent.parent
STORAGE = BASE / "storage"
ANALYTICS = BASE / "analytics" / "data"
REPORTS = BASE / "reports"

CONVICTIONS_FILE = STORAGE / "convictions.json"
SOCIAL_FILE = STORAGE / "social_signals.json"
PR_FILE = STORAGE / "pr_signals.json"
SIGNALS_FILE = STORAGE / "signals.json"
SALES_FILE = ANALYTICS / "sales.json"


# ── Data Loaders ───────────────────────────────────────────────────────────────
def load_json(path, default=None):
    """Load JSON file, return default on failure."""
    if default is None:
        default = []
    try:
        with open(path, "r") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"  [warn] Could not load {path.name}: {e}")
        return default


def load_convictions():
    data = load_json(CONVICTIONS_FILE, default={})
    return data.get("convictions", []) if isinstance(data, dict) else data


def load_fear_greed():
    """Extract the latest Fear & Greed entry from social signals."""
    signals = load_json(SOCIAL_FILE)
    for s in signals:
        if s.get("source") == "fear_greed_index":
            title = s.get("title", "")
            # Parse "Crypto Fear & Greed: 11 (Extreme Fear)"
            try:
                parts = title.split(":")
                rest = parts[1].strip()
                value = int(rest.split("(")[0].strip())
                label = rest.split("(")[1].rstrip(")")
            except (IndexError, ValueError):
                value, label = 0, "Unknown"
            return {"value": value, "label": label, "title": title}
    return {"value": 0, "label": "N/A", "title": "No data"}


def load_top_movers():
    """Get top crypto movers from social signals (coingecko source)."""
    signals = load_json(SOCIAL_FILE)
    movers = [s for s in signals if s.get("source") == "coingecko"]
    # Sort by absolute score descending
    movers.sort(key=lambda x: abs(x.get("score", 0)), reverse=True)
    return movers[:6]


def load_pr_headlines(n=5):
    signals = load_json(PR_FILE)
    # Sort by timestamp descending
    signals.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
    return signals[:n]


def load_top_signals(n=10):
    signals = load_json(SIGNALS_FILE)
    # Sort by timestamp descending
    signals.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
    return signals[:n]


def load_sales():
    sales = load_json(SALES_FILE)
    if not sales:
        return []
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    # Filter to today's sales if timestamps exist
    today_sales = []
    for s in sales:
        ts = s.get("timestamp", s.get("date", ""))
        if today in str(ts):
            today_sales.append(s)
    return today_sales if today_sales else sales


# ── Color Helpers ──────────────────────────────────────────────────────────────
def fear_greed_color(value):
    if value <= 25:
        return "#ff4444"  # extreme fear - red
    elif value <= 45:
        return "#ff8c00"  # fear - orange
    elif value <= 55:
        return "#cccc00"  # neutral - yellow
    elif value <= 75:
        return "#88cc00"  # greed - lime
    else:
        return "#00cc44"  # extreme greed - green


def conviction_color(score):
    if score >= 70:
        return "#d4af37"  # gold - high
    elif score >= 50:
        return "#888888"  # gray - medium
    else:
        return "#555555"  # dark - low


def sentiment_color(hint):
    colors = {
        "bullish": "#00cc44",
        "slightly_bullish": "#88cc00",
        "neutral": "#888888",
        "slightly_bearish": "#ff8c00",
        "bearish": "#ff4444",
    }
    return colors.get(hint, "#888888")


def level_badge(level):
    colors = {"HIGH": "#d4af37", "MEDIUM": "#888888", "LOW": "#555555"}
    c = colors.get(level, "#555555")
    return f'<span style="background:{c};color:#000;padding:2px 8px;border-radius:3px;font-size:11px;font-weight:bold;">{level}</span>'


# ── HTML Generator ─────────────────────────────────────────────────────────────
def generate_html(convictions, fear_greed, movers, pr_headlines, signals, sales):
    now = datetime.now(timezone.utc)
    date_str = now.strftime("%B %d, %Y")
    time_str = now.strftime("%H:%M UTC")

    # Conviction bars
    conviction_rows = ""
    for c in convictions:
        score = c["score"]
        bar_width = min(score, 100)
        color = conviction_color(score)
        conviction_rows += f"""
        <tr>
          <td style="padding:8px 12px;color:#ccc;font-size:14px;white-space:nowrap;">{c['topic'].upper()}</td>
          <td style="padding:8px 12px;width:100%;">
            <div style="background:#1a1a1a;border-radius:4px;overflow:hidden;height:22px;position:relative;">
              <div style="background:{color};height:100%;width:{bar_width}%;border-radius:4px;transition:width 0.3s;"></div>
              <span style="position:absolute;right:8px;top:2px;color:#fff;font-size:12px;font-weight:bold;">{score:.1f}</span>
            </div>
          </td>
          <td style="padding:8px 12px;text-align:center;">{level_badge(c['level'])}</td>
          <td style="padding:8px 12px;color:#666;font-size:12px;text-align:center;">{c['signal_count']} signals</td>
        </tr>"""

    # Fear & Greed section
    fg_color = fear_greed_color(fear_greed["value"])
    fg_section = f"""
    <div style="text-align:center;padding:20px;">
      <div style="font-size:14px;color:#888;margin-bottom:8px;">CRYPTO FEAR &amp; GREED INDEX</div>
      <div style="display:inline-block;width:100px;height:100px;border-radius:50%;border:4px solid {fg_color};line-height:100px;text-align:center;">
        <span style="font-size:36px;font-weight:bold;color:{fg_color};">{fear_greed['value']}</span>
      </div>
      <div style="font-size:16px;color:{fg_color};margin-top:8px;font-weight:bold;">{fear_greed['label']}</div>
    </div>"""

    # Top movers
    movers_html = ""
    for m in movers:
        s_color = sentiment_color(m.get("sentiment_hint", "neutral"))
        movers_html += f"""
        <div style="display:inline-block;background:#111;border:1px solid #222;border-radius:6px;padding:10px 16px;margin:4px;min-width:140px;text-align:center;">
          <div style="font-size:13px;color:#ccc;">{m['title'].split('(')[0].strip() if '(' in m['title'] else m['title'][:20]}</div>
          <div style="font-size:11px;color:{s_color};margin-top:4px;">{m.get('sentiment_hint', 'neutral').replace('_', ' ').title()}</div>
        </div>"""

    # PR headlines
    pr_rows = ""
    for p in pr_headlines:
        cat = p.get("category", "General")
        pr_rows += f"""
        <tr>
          <td style="padding:8px 12px;">
            <a href="{p.get('url', '#')}" style="color:#d4af37;text-decoration:none;font-size:13px;">{p['title'][:90]}</a>
          </td>
          <td style="padding:8px 12px;color:#666;font-size:12px;white-space:nowrap;">{cat}</td>
        </tr>"""

    # Top signals
    signal_rows = ""
    for s in signals:
        s_color = sentiment_color(s.get("sentiment_hint", "neutral"))
        ts = s.get("timestamp", "")[:16].replace("T", " ")
        signal_rows += f"""
        <tr>
          <td style="padding:6px 12px;">
            <a href="{s.get('url', '#')}" style="color:#ccc;text-decoration:none;font-size:13px;">{s['title'][:100]}</a>
          </td>
          <td style="padding:6px 12px;white-space:nowrap;">
            <span style="color:{s_color};font-size:11px;">{s.get('sentiment_hint', 'neutral').replace('_', ' ')}</span>
          </td>
          <td style="padding:6px 12px;color:#555;font-size:11px;white-space:nowrap;">{s.get('source', '')}</td>
          <td style="padding:6px 12px;color:#444;font-size:11px;white-space:nowrap;">{ts}</td>
        </tr>"""

    # Sales summary
    if sales:
        total = sum(float(s.get("price", s.get("amount", 0))) for s in sales)
        sales_section = f"""
        <div style="text-align:center;padding:16px;">
          <div style="font-size:32px;color:#d4af37;font-weight:bold;">${total:,.2f}</div>
          <div style="font-size:13px;color:#888;margin-top:4px;">{len(sales)} sale(s) today</div>
        </div>
        <table width="100%" cellpadding="0" cellspacing="0">
          {''.join(f'<tr><td style="padding:4px 12px;color:#ccc;font-size:13px;">{s.get("title", s.get("item", "Item"))}</td><td style="padding:4px 12px;color:#d4af37;font-size:13px;text-align:right;">${float(s.get("price", s.get("amount", 0))):,.2f}</td></tr>' for s in sales)}
        </table>"""
    else:
        sales_section = """
        <div style="text-align:center;padding:20px;">
          <div style="font-size:14px;color:#555;">No sales recorded today</div>
        </div>"""

    # Section helper
    def section(title, content):
        return f"""
    <table width="100%" cellpadding="0" cellspacing="0" style="margin-bottom:24px;">
      <tr>
        <td style="padding:12px 16px;border-bottom:2px solid #d4af37;">
          <span style="color:#d4af37;font-size:16px;font-weight:bold;letter-spacing:1px;">{title}</span>
        </td>
      </tr>
      <tr>
        <td style="padding:0;">
          {content}
        </td>
      </tr>
    </table>"""

    html = f"""<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>BIOS Daily Briefing — {date_str}</title>
</head>
<body style="margin:0;padding:0;background:#000;font-family:'Helvetica Neue',Arial,sans-serif;">
  <table width="100%" cellpadding="0" cellspacing="0" style="background:#000;">
    <tr>
      <td align="center" style="padding:20px;">
        <table width="640" cellpadding="0" cellspacing="0" style="background:#0a0a0a;border:1px solid #1a1a1a;border-radius:8px;">

          <!-- Header -->
          <tr>
            <td style="padding:32px 24px 16px;text-align:center;border-bottom:1px solid #1a1a1a;">
              <div style="font-size:11px;color:#d4af37;letter-spacing:3px;margin-bottom:8px;">B I O S</div>
              <div style="font-size:24px;color:#fff;font-weight:bold;">Daily Briefing</div>
              <div style="font-size:13px;color:#555;margin-top:8px;">{date_str} &mdash; {time_str}</div>
            </td>
          </tr>

          <!-- Content -->
          <tr>
            <td style="padding:24px;">

              {section("MARKET PULSE", fg_section + '<div style="text-align:center;">' + movers_html + '</div>')}

              {section("CONVICTION SCORES", '<table width="100%" cellpadding="0" cellspacing="0">' + conviction_rows + '</table>')}

              {section("PR INTELLIGENCE", '<table width="100%" cellpadding="0" cellspacing="0">' + pr_rows + '</table>' if pr_rows else '<div style="padding:12px;color:#555;font-size:13px;">No PR signals detected</div>')}

              {section("TOP SIGNALS", '<table width="100%" cellpadding="0" cellspacing="0">' + signal_rows + '</table>')}

              {section("SALES SUMMARY", sales_section)}

            </td>
          </tr>

          <!-- Footer -->
          <tr>
            <td style="padding:16px 24px;border-top:1px solid #1a1a1a;text-align:center;">
              <div style="font-size:11px;color:#333;">Generated by BIOS at {now.strftime('%Y-%m-%d %H:%M:%S UTC')}</div>
              <div style="font-size:10px;color:#222;margin-top:4px;">Conviction Engine v1 &mdash; {len(convictions)} topics tracked &mdash; {sum(c['signal_count'] for c in convictions)} total signals</div>
            </td>
          </tr>

        </table>
      </td>
    </tr>
  </table>
</body>
</html>"""

    return html


# ── Terminal Summary ───────────────────────────────────────────────────────────
def print_terminal_summary(convictions, fear_greed, movers, pr_headlines, signals, sales):
    now = datetime.now(timezone.utc)

    print()
    print("=" * 60)
    print(f"  BIOS DAILY BRIEFING — {now.strftime('%B %d, %Y %H:%M UTC')}")
    print("=" * 60)

    # Fear & Greed
    print(f"\n  Fear & Greed Index: {fear_greed['value']} ({fear_greed['label']})")

    # Top movers
    if movers:
        print("\n  Top Crypto Movers:")
        for m in movers:
            print(f"    {m['title'][:60]}")

    # Convictions
    print("\n  Conviction Scores:")
    print(f"  {'TOPIC':<16} {'SCORE':>6}  {'LEVEL':<8} {'SIGNALS':>8}")
    print("  " + "-" * 44)
    for c in convictions:
        bar_len = int(c["score"] / 5)
        bar = "#" * bar_len + "." * (20 - bar_len)
        print(f"  {c['topic'].upper():<16} {c['score']:>5.1f}  {c['level']:<8} {c['signal_count']:>6}")

    # PR Headlines
    if pr_headlines:
        print(f"\n  PR Intelligence ({len(pr_headlines)} headlines):")
        for p in pr_headlines:
            print(f"    - {p['title'][:70]}")

    # Top signals
    if signals:
        print(f"\n  Latest Signals ({len(signals)}):")
        for s in signals[:5]:
            sentiment = s.get("sentiment_hint", "neutral")
            icon = {"bullish": "+", "bearish": "-", "neutral": "~"}.get(sentiment, "~")
            print(f"    [{icon}] {s['title'][:65]}")
        if len(signals) > 5:
            print(f"    ... and {len(signals) - 5} more")

    # Sales
    if sales:
        total = sum(float(s.get("price", s.get("amount", 0))) for s in sales)
        print(f"\n  Sales Today: {len(sales)} sale(s) — ${total:,.2f}")
    else:
        print("\n  Sales Today: None recorded")

    print()
    print("=" * 60)
    print(f"  {len(convictions)} topics | {sum(c['signal_count'] for c in convictions)} signals processed")
    print("=" * 60)
    print()


# ── Main ───────────────────────────────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser(description="BIOS Daily Briefing Generator")
    parser.add_argument("--send", action="store_true", help="Send briefing via email (stub)")
    args = parser.parse_args()

    if args.send:
        print("Email sending not configured yet")
        print("To set up: add SMTP credentials to bios/config/email.json")
        return

    print("[BIOS] Generating daily briefing...")

    # Load all data
    convictions = load_convictions()
    fear_greed = load_fear_greed()
    movers = load_top_movers()
    pr_headlines = load_pr_headlines(n=5)
    signals = load_top_signals(n=10)
    sales = load_sales()

    print(f"  Loaded {len(convictions)} convictions, {len(movers)} movers, {len(pr_headlines)} PR headlines, {len(signals)} signals")

    # Generate HTML
    html = generate_html(convictions, fear_greed, movers, pr_headlines, signals, sales)

    # Save HTML report
    REPORTS.mkdir(parents=True, exist_ok=True)
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    report_path = REPORTS / f"briefing-{today}.html"
    with open(report_path, "w") as f:
        f.write(html)
    print(f"  Saved: {report_path}")

    # Print terminal summary
    print_terminal_summary(convictions, fear_greed, movers, pr_headlines, signals, sales)


if __name__ == "__main__":
    main()

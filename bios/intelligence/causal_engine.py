#!/usr/bin/env python3
"""
BIOS Intelligence Engine v1 - Phase 4.
Probabilistic causal mapping, cross-source confirmation, insight generation.

Usage:
    python3 bios/intelligence/causal_engine.py              # Generate insights
    python3 bios/intelligence/causal_engine.py --digest      # Print top insights
    python3 bios/intelligence/causal_engine.py --report      # Full daily report
"""

import json
import sys
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent
STORAGE_DIR = BASE_DIR / "bios" / "storage"
SIGNALS_FILE = STORAGE_DIR / "signals.json"
INSIGHTS_FILE = STORAGE_DIR / "insights.json"
CAUSAL_GRAPH_FILE = Path(__file__).parent / "causal_graph.json"

# Probabilistic Causal Graph (v1 - rule-based)
CAUSAL_GRAPH = {
    "oil_disruption": {
        "triggers": ["oil", "petroleum", "crude", "opec", "energy crisis"],
        "effects": [
            {"asset": "oil", "direction": "up", "weight": 0.9, "lag": "1-3 days"},
            {"asset": "gas", "direction": "up", "weight": 0.85, "lag": "3-7 days"},
            {"asset": "airlines", "direction": "down", "weight": 0.7, "lag": "1-5 days"},
            {"asset": "defense", "direction": "up", "weight": 0.5, "lag": "1-7 days"},
            {"asset": "gold", "direction": "up", "weight": 0.65, "lag": "1-3 days"},
            {"asset": "inflation", "direction": "up", "weight": 0.6, "lag": "2-6 weeks"},
        ],
        "pr_relevance": 0.7,
        "pr_note": "Gas prices in PR will increase. Plan fuel costs.",
    },
    "fed_rate_hike": {
        "triggers": ["rate hike", "interest rate increase", "fed raises", "hawkish fed", "tightening"],
        "effects": [
            {"asset": "USD", "direction": "up", "weight": 0.8, "lag": "immediate"},
            {"asset": "stocks", "direction": "down", "weight": 0.65, "lag": "1-3 days"},
            {"asset": "crypto", "direction": "down", "weight": 0.6, "lag": "1-5 days"},
            {"asset": "bonds", "direction": "up", "weight": 0.7, "lag": "immediate"},
            {"asset": "gold", "direction": "down", "weight": 0.4, "lag": "1-7 days"},
        ],
        "pr_relevance": 0.5,
        "pr_note": "Higher rates affect mortgages and business loans in PR.",
    },
    "fed_rate_cut": {
        "triggers": ["rate cut", "interest rate decrease", "dovish fed", "easing"],
        "effects": [
            {"asset": "USD", "direction": "down", "weight": 0.75, "lag": "immediate"},
            {"asset": "stocks", "direction": "up", "weight": 0.7, "lag": "1-3 days"},
            {"asset": "crypto", "direction": "up", "weight": 0.65, "lag": "1-5 days"},
            {"asset": "gold", "direction": "up", "weight": 0.6, "lag": "1-7 days"},
        ],
        "pr_relevance": 0.5,
        "pr_note": "Lower rates benefit PR businesses and mortgages.",
    },
    "government_stimulus": {
        "triggers": ["stimulus", "relief package", "government spending", "infrastructure bill", "aid package"],
        "effects": [
            {"asset": "stocks", "direction": "up", "weight": 0.7, "lag": "1-7 days"},
            {"asset": "crypto", "direction": "up", "weight": 0.5, "lag": "1-14 days"},
            {"asset": "inflation", "direction": "up", "weight": 0.6, "lag": "1-3 months"},
            {"asset": "consumer_spending", "direction": "up", "weight": 0.8, "lag": "1-4 weeks"},
        ],
        "pr_relevance": 0.9,
        "pr_note": "Check if PR is included. Federal programs often apply differently to territories.",
    },
    "geopolitical_conflict": {
        "triggers": ["war", "invasion", "military action", "troops deployed", "conflict escalat"],
        "effects": [
            {"asset": "oil", "direction": "up", "weight": 0.75, "lag": "immediate"},
            {"asset": "gold", "direction": "up", "weight": 0.8, "lag": "immediate"},
            {"asset": "defense", "direction": "up", "weight": 0.7, "lag": "1-3 days"},
            {"asset": "stocks", "direction": "down", "weight": 0.6, "lag": "1-3 days"},
            {"asset": "crypto", "direction": "mixed", "weight": 0.4, "lag": "1-7 days"},
        ],
        "pr_relevance": 0.4,
        "pr_note": "Monitor fuel and import costs. PR depends on shipping.",
    },
    "crypto_rally": {
        "triggers": ["bitcoin rally", "btc surge", "crypto bull", "eth breakout", "crypto pump"],
        "effects": [
            {"asset": "BTC", "direction": "up", "weight": 0.8, "lag": "ongoing"},
            {"asset": "altcoins", "direction": "up", "weight": 0.7, "lag": "1-3 days after BTC"},
            {"asset": "crypto_stocks", "direction": "up", "weight": 0.6, "lag": "1-2 days"},
        ],
        "pr_relevance": 0.6,
        "pr_note": "Act 60 crypto investors may increase activity. Content opportunity.",
    },
    "crypto_crash": {
        "triggers": ["bitcoin crash", "btc dump", "crypto bear", "crypto crash", "crypto collapse"],
        "effects": [
            {"asset": "BTC", "direction": "down", "weight": 0.85, "lag": "ongoing"},
            {"asset": "altcoins", "direction": "down", "weight": 0.9, "lag": "immediate"},
            {"asset": "stablecoins", "direction": "up", "weight": 0.7, "lag": "immediate"},
        ],
        "pr_relevance": 0.5,
        "pr_note": "Act 60 crypto community affected. Potential content angle.",
    },
    "ai_regulation": {
        "triggers": ["ai regulation", "ai ban", "ai law", "ai policy", "regulate artificial"],
        "effects": [
            {"asset": "ai_stocks", "direction": "down", "weight": 0.5, "lag": "1-7 days"},
            {"asset": "compliance_tools", "direction": "up", "weight": 0.6, "lag": "1-4 weeks"},
        ],
        "pr_relevance": 0.3,
        "pr_note": "May affect AI agent business model. Monitor scope.",
    },
    "pr_policy": {
        "triggers": ["puerto rico", "act 60", "act 22", "colmena", "pr incentive", "pr tax"],
        "effects": [
            {"asset": "pr_business", "direction": "mixed", "weight": 0.9, "lag": "varies"},
        ],
        "pr_relevance": 1.0,
        "pr_note": "DIRECT IMPACT. Read details immediately.",
    },
}


def load_signals():
    if SIGNALS_FILE.exists():
        with open(SIGNALS_FILE) as f:
            return json.load(f)
    return []


def load_insights():
    if INSIGHTS_FILE.exists():
        try:
            with open(INSIGHTS_FILE) as f:
                return json.load(f)
        except Exception:
            return []
    return []


def save_insights(insights):
    insights = insights[-200:]
    with open(INSIGHTS_FILE, "w") as f:
        json.dump(insights, f, indent=2)


def match_causal(signals):
    """Match signals against causal graph. Return triggered patterns."""
    triggered = {}

    for pattern_name, pattern in CAUSAL_GRAPH.items():
        matching_signals = []
        for signal in signals:
            text = f"{signal.get('title', '')} {signal.get('description', '')}".lower()
            for trigger in pattern["triggers"]:
                if trigger in text:
                    matching_signals.append(signal)
                    break

        if matching_signals:
            # Cross-source confirmation
            sources = set(s.get("source", "") for s in matching_signals)
            source_diversity = len(sources)
            avg_sentiment = sum(s.get("sentiment", 0) for s in matching_signals) / len(matching_signals)

            # Confidence based on signal count and diversity
            base_confidence = min(0.95, 0.3 + (len(matching_signals) * 0.05) + (source_diversity * 0.1))

            triggered[pattern_name] = {
                "signal_count": len(matching_signals),
                "source_diversity": source_diversity,
                "sources": list(sources),
                "confidence": round(base_confidence, 2),
                "avg_sentiment": round(avg_sentiment, 2),
                "sample_titles": [s["title"][:80] for s in matching_signals[:3]],
            }

    return triggered


def generate_insights(triggered):
    """Generate insight objects from triggered patterns."""
    insights = []

    for pattern_name, match in triggered.items():
        pattern = CAUSAL_GRAPH[pattern_name]

        effects_summary = []
        for effect in pattern["effects"]:
            arrow = "UP" if effect["direction"] == "up" else ("DOWN" if effect["direction"] == "down" else "MIXED")
            effects_summary.append(f"{effect['asset']} {arrow} ({effect['weight']:.0%}, {effect['lag']})")

        # Determine action level
        conf = match["confidence"]
        if conf >= 0.75:
            action_level = "ACTIONABLE"
        elif conf >= 0.5:
            action_level = "MONITOR"
        else:
            action_level = "WATCH"

        insight = {
            "id": f"ins_{pattern_name}_{datetime.now(timezone.utc).strftime('%Y%m%d%H%M')}",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "pattern": pattern_name,
            "confidence": match["confidence"],
            "action_level": action_level,
            "signal_count": match["signal_count"],
            "source_diversity": match["source_diversity"],
            "sources": match["sources"],
            "effects": effects_summary,
            "pr_relevance": pattern.get("pr_relevance", 0),
            "pr_note": pattern.get("pr_note", ""),
            "sample_titles": match["sample_titles"],
        }
        insights.append(insight)

    return insights


def narrative_detection(signals):
    """Detect emerging narratives from tag frequency and co-occurrence."""
    tag_counts = Counter()
    tag_sentiment = defaultdict(list)
    tag_sources = defaultdict(set)

    for s in signals:
        for tag in s.get("tags", []):
            tag_counts[tag] += 1
            tag_sentiment[tag].append(s.get("sentiment", 0))
            tag_sources[tag].add(s.get("source", ""))

    narratives = []
    for tag, count in tag_counts.most_common(10):
        avg_sent = sum(tag_sentiment[tag]) / len(tag_sentiment[tag])
        diversity = len(tag_sources[tag])
        narratives.append({
            "topic": tag,
            "mentions": count,
            "sentiment": round(avg_sent, 2),
            "source_diversity": diversity,
            "strength": round(count * diversity * 0.1, 1),
        })

    return narratives


def print_digest(count=10):
    """Print top insights."""
    insights = load_insights()
    if not insights:
        print("  No insights yet. Run without --digest first.")
        return

    insights.sort(key=lambda i: i.get("confidence", 0), reverse=True)

    print(f"\n  BIOS INTELLIGENCE DIGEST")
    print(f"  {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print("  " + "=" * 60)

    for ins in insights[:count]:
        level = ins.get("action_level", "?")
        conf = ins.get("confidence", 0)
        pattern = ins.get("pattern", "?").replace("_", " ").title()
        pr = ins.get("pr_relevance", 0)

        print(f"\n  [{level}] {pattern} (confidence: {conf:.0%})")
        print(f"  Signals: {ins.get('signal_count', 0)} from {ins.get('source_diversity', 0)} sources")
        print(f"  Effects:")
        for e in ins.get("effects", [])[:4]:
            print(f"    - {e}")
        if pr >= 0.5:
            print(f"  PR Impact: {ins.get('pr_note', '')}")

    print()


def print_report():
    """Full daily intelligence report."""
    signals = load_signals()
    if not signals:
        print("  No signals. Run ingestion first.")
        return

    # Generate fresh insights
    triggered = match_causal(signals)
    insights = generate_insights(triggered)
    narratives = narrative_detection(signals)

    existing = load_insights()
    all_insights = existing + insights
    save_insights(all_insights)

    print(f"\n  {'='*60}")
    print(f"  BIOS DAILY INTELLIGENCE REPORT")
    print(f"  {datetime.now().strftime('%Y-%m-%d %H:%M')} AST")
    print(f"  {'='*60}")

    # Signal summary
    source_counts = Counter(s.get("source", "?") for s in signals)
    print(f"\n  SIGNALS: {len(signals)} total from {len(source_counts)} sources")
    for src, cnt in source_counts.most_common(5):
        print(f"    {src}: {cnt}")

    # Narratives
    print(f"\n  TOP NARRATIVES:")
    for n in narratives[:5]:
        sent_arrow = "+" if n["sentiment"] > 0 else ("-" if n["sentiment"] < 0 else "~")
        print(f"    {n['topic']:15s} mentions:{n['mentions']:3d}  sentiment:{sent_arrow}  sources:{n['source_diversity']}")

    # Triggered patterns
    if insights:
        print(f"\n  TRIGGERED PATTERNS ({len(insights)}):")
        for ins in sorted(insights, key=lambda i: i["confidence"], reverse=True):
            level = ins["action_level"]
            conf = ins["confidence"]
            pattern = ins["pattern"].replace("_", " ").title()
            print(f"\n    [{level}] {pattern} ({conf:.0%})")
            for e in ins["effects"][:3]:
                print(f"      {e}")
            if ins["pr_relevance"] >= 0.5:
                print(f"      PR: {ins['pr_note']}")
    else:
        print(f"\n  No causal patterns triggered.")

    # PR-specific
    pr_signals = [s for s in signals if "puerto_rico" in s.get("tags", [])]
    if pr_signals:
        print(f"\n  PUERTO RICO ({len(pr_signals)} signals):")
        for s in pr_signals[:5]:
            print(f"    {s['title'][:70]}")

    print(f"\n  {'='*60}")
    print(f"  End of report. {len(insights)} insights generated.")
    print(f"  {'='*60}\n")


def main():
    if "--digest" in sys.argv:
        print_digest()
    elif "--report" in sys.argv:
        print_report()
    else:
        signals = load_signals()
        if not signals:
            print("  No signals. Run ingestion first.")
            return

        print(f"  Processing {len(signals)} signals...")
        triggered = match_causal(signals)
        insights = generate_insights(triggered)

        existing = load_insights()
        all_insights = existing + insights
        save_insights(all_insights)

        print(f"  {len(triggered)} patterns triggered. {len(insights)} insights generated.")
        if insights:
            for ins in insights:
                print(f"    [{ins['action_level']}] {ins['pattern']} ({ins['confidence']:.0%})")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
Polymarket Research Automation -- BIOS Alpha Scanner

Fetches active Polymarket markets, cross-references with BIOS signals,
and identifies disagreement-based alpha opportunities.

Usage:
    python3 polymarket_research.py --scan          # full market scan + report
    python3 polymarket_research.py --report        # generate report from last scan
    python3 polymarket_research.py --history       # show past prediction accuracy
    python3 polymarket_research.py --alerts-only   # only send Telegram for disagreement > 20%

Cron (every 6 hours):
    0 */6 * * * cd ~/behique && python3 bios/trading/polymarket_research.py --scan
"""

import argparse
import json
import os
import re
import sys
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

# -- Paths -------------------------------------------------------------------

BASE_DIR = Path(__file__).parent
BIOS_DIR = BASE_DIR.parent
STORAGE_DIR = BIOS_DIR / "storage"
REPORTS_DIR = BIOS_DIR / "reports"
SIGNALS_FILE = STORAGE_DIR / "signals.json"
CONVICTIONS_FILE = STORAGE_DIR / "convictions.json"
PREDICTION_HISTORY = BASE_DIR / "prediction_history.json"
LAST_SCAN_FILE = BASE_DIR / ".last_polymarket_scan.json"

POLYMARKET_API = "https://gamma-api.polymarket.com/markets"
MIN_VOLUME = 10_000  # $10K minimum volume
DISAGREEMENT_ALERT_THRESHOLD = 0.20  # 20%

# -- Telegram ----------------------------------------------------------------

TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID", "")


def send_telegram(text: str) -> bool:
    """Send a Telegram message. Falls back to stdout if no token configured."""
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        print(f"[POLYMARKET ALERT] {text}")
        return True
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        payload = json.dumps({
            "chat_id": TELEGRAM_CHAT_ID,
            "text": text,
            "parse_mode": "Markdown",
        }).encode("utf-8")
        req = urllib.request.Request(
            url, data=payload, headers={"Content-Type": "application/json"}
        )
        with urllib.request.urlopen(req, timeout=15) as resp:
            result = json.loads(resp.read().decode("utf-8"))
            return result.get("ok", False)
    except (urllib.error.URLError, urllib.error.HTTPError, OSError) as exc:
        print(f"[POLYMARKET ALERT] Telegram failed: {exc}", file=sys.stderr)
        print(f"[POLYMARKET ALERT] {text}")
        return False


# -- Data Loaders ------------------------------------------------------------

def load_json(path, default=None):
    if default is None:
        default = {}
    try:
        with open(path, "r") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return default


def save_json(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w") as f:
        json.dump(data, f, indent=2, default=str)


def load_signals():
    """Load BIOS signals from storage/signals.json."""
    return load_json(SIGNALS_FILE, default=[])


def load_convictions():
    """Load BIOS convictions from storage/convictions.json."""
    data = load_json(CONVICTIONS_FILE)
    return data.get("convictions", []) if isinstance(data, dict) else data


def load_prediction_history():
    return load_json(PREDICTION_HISTORY, default={
        "predictions": [],
        "resolved": [],
        "stats": {"bios_correct": 0, "market_correct": 0, "total_resolved": 0}
    })


def save_prediction_history(data):
    save_json(PREDICTION_HISTORY, data)


# -- Polymarket API ----------------------------------------------------------

def fetch_markets(limit=100, offset=0):
    """Fetch active markets from Polymarket Gamma API."""
    all_markets = []
    page = 0
    max_pages = 10  # safety cap

    while page < max_pages:
        params = f"?limit={limit}&offset={offset + page * limit}&active=true&closed=false"
        url = POLYMARKET_API + params
        try:
            req = urllib.request.Request(url, headers={
                "User-Agent": "BIOS-Polymarket-Research/1.0",
                "Accept": "application/json",
            })
            with urllib.request.urlopen(req, timeout=30) as resp:
                data = json.loads(resp.read().decode("utf-8"))
        except (urllib.error.URLError, urllib.error.HTTPError, OSError) as exc:
            print(f"[ERROR] Failed to fetch markets (page {page}): {exc}", file=sys.stderr)
            break

        if not data:
            break

        # Handle both list response and dict with results key
        markets = data if isinstance(data, list) else data.get("results", data.get("markets", []))
        if not markets:
            break

        all_markets.extend(markets)
        page += 1

        # If we got fewer than limit, we hit the end
        if len(markets) < limit:
            break

    return all_markets


def parse_market(raw):
    """Extract relevant fields from a raw Polymarket market object."""
    volume = 0
    try:
        volume = float(raw.get("volume", 0) or 0)
    except (ValueError, TypeError):
        pass

    # volumeNum is sometimes provided as a cleaner field
    if volume == 0:
        try:
            volume = float(raw.get("volumeNum", 0) or 0)
        except (ValueError, TypeError):
            pass

    # Probability / price
    probability = None
    for field in ("outcomePrices", "bestAsk", "lastTradePrice"):
        val = raw.get(field)
        if val is not None:
            try:
                if isinstance(val, str) and val.startswith("["):
                    prices = json.loads(val)
                    if prices:
                        probability = float(prices[0])
                elif isinstance(val, list) and val:
                    probability = float(val[0])
                else:
                    probability = float(val)
                break
            except (ValueError, TypeError, json.JSONDecodeError):
                continue

    if probability is None:
        probability = 0.5  # default unknown

    return {
        "id": raw.get("id", raw.get("conditionId", "")),
        "question": raw.get("question", raw.get("title", "Unknown")),
        "description": raw.get("description", ""),
        "volume": volume,
        "probability": probability,
        "category": raw.get("category", raw.get("tags", "")),
        "end_date": raw.get("endDate", raw.get("end_date_iso", "")),
        "url": raw.get("url", f"https://polymarket.com/event/{raw.get('slug', '')}"),
        "active": raw.get("active", True),
    }


# -- BIOS Cross-Reference ---------------------------------------------------

def extract_keywords(text):
    """Extract meaningful keywords from a market question."""
    stop_words = {
        "will", "the", "be", "in", "on", "at", "to", "a", "an", "of",
        "by", "for", "is", "it", "or", "and", "this", "that", "with",
        "from", "as", "are", "was", "were", "been", "being", "have",
        "has", "had", "do", "does", "did", "but", "not", "no", "yes",
        "if", "than", "so", "can", "would", "could", "should", "may",
        "might", "must", "shall", "before", "after", "above", "below",
        "between", "under", "over", "through", "during", "until",
        "what", "when", "where", "who", "which", "how", "much", "many",
        "more", "most", "other", "some", "any", "all", "both", "each",
        "few", "only", "own", "same", "such", "very",
    }
    # Clean and split
    words = re.findall(r"[a-zA-Z0-9]+", text.lower())
    keywords = [w for w in words if w not in stop_words and len(w) > 2]
    return keywords


def match_signals(market, signals):
    """Find BIOS signals related to a market question."""
    keywords = extract_keywords(market["question"])
    if market.get("description"):
        keywords.extend(extract_keywords(market["description"])[:5])

    # Deduplicate while preserving order
    seen = set()
    unique_keywords = []
    for k in keywords:
        if k not in seen:
            seen.add(k)
            unique_keywords.append(k)
    keywords = unique_keywords

    matched = []
    for signal in signals:
        signal_text = (
            f"{signal.get('title', '')} {signal.get('description', '')} "
            f"{' '.join(signal.get('tags', []))}"
        ).lower()

        overlap = sum(1 for kw in keywords if kw in signal_text)
        if overlap >= 2:  # at least 2 keyword matches
            matched.append({
                "signal_id": signal.get("id", ""),
                "title": signal.get("title", ""),
                "sentiment": signal.get("sentiment", 0.0),
                "priority": signal.get("priority", 0.0),
                "source": signal.get("source", ""),
                "overlap_count": overlap,
                "matched_keywords": [kw for kw in keywords if kw in signal_text],
            })

    # Sort by overlap count
    matched.sort(key=lambda x: x["overlap_count"], reverse=True)
    return matched, keywords


def match_convictions(market, convictions):
    """Find BIOS convictions related to a market question."""
    keywords = extract_keywords(market["question"])
    matched = []

    for conv in convictions:
        topic = conv.get("topic", "").lower()
        overlap = sum(1 for kw in keywords if kw in topic)
        if overlap >= 1:
            matched.append({
                "topic": conv.get("topic", ""),
                "score": conv.get("score", 0),
                "level": conv.get("level", ""),
                "sentiment": conv.get("sentiment", 50),
                "sources": conv.get("sources", []),
            })

    matched.sort(key=lambda x: x.get("score", 0), reverse=True)
    return matched


def compute_bios_probability(matched_signals, matched_convictions, market_prob):
    """
    Estimate what BIOS thinks the probability should be based on signals.

    Logic:
    - Start from market probability as baseline
    - Shift based on signal sentiment (positive signals push toward YES)
    - Weight by conviction score and signal priority
    - Clamp to [0.05, 0.95]
    """
    if not matched_signals and not matched_convictions:
        return market_prob, 0.0, "no_data"

    adjustments = []

    # Signal-based adjustment
    for sig in matched_signals:
        sentiment = sig.get("sentiment", 0.0)
        priority = sig.get("priority", 0.0)
        overlap = sig.get("overlap_count", 1)
        # Sentiment ranges from -1 to 1. Convert to probability shift.
        # High priority + strong sentiment = bigger shift.
        weight = (overlap / 5.0) * max(priority, 0.5) / 3.0
        shift = sentiment * weight * 0.15
        adjustments.append(shift)

    # Conviction-based adjustment
    for conv in matched_convictions:
        score = conv.get("score", 0) / 100.0
        sentiment = conv.get("sentiment", 50) / 100.0
        # Conviction sentiment > 50 = bullish (push toward YES)
        direction = (sentiment - 0.5) * 2  # range -1 to 1
        shift = direction * score * 0.20
        adjustments.append(shift)

    if not adjustments:
        return market_prob, 0.0, "no_data"

    total_shift = sum(adjustments) / max(len(adjustments), 1)
    bios_prob = market_prob + total_shift
    bios_prob = max(0.05, min(0.95, bios_prob))

    disagreement = abs(bios_prob - market_prob)

    if disagreement > 0.20:
        confidence = "high"
    elif disagreement > 0.10:
        confidence = "medium"
    else:
        confidence = "low"

    return bios_prob, disagreement, confidence


# -- Scanner -----------------------------------------------------------------

def scan_markets():
    """Full scan: fetch markets, cross-reference with BIOS, score disagreements."""
    print("[SCAN] Fetching active Polymarket markets...")
    raw_markets = fetch_markets()
    print(f"[SCAN] Fetched {len(raw_markets)} markets")

    # Parse and filter by volume
    markets = []
    for raw in raw_markets:
        parsed = parse_market(raw)
        if parsed["volume"] >= MIN_VOLUME:
            markets.append(parsed)

    print(f"[SCAN] {len(markets)} markets with volume > ${MIN_VOLUME:,}")

    # Load BIOS data
    signals = load_signals()
    convictions = load_convictions()
    print(f"[SCAN] Loaded {len(signals)} signals, {len(convictions)} convictions")

    # Score each market
    opportunities = []
    for market in markets:
        matched_signals, keywords = match_signals(market, signals)
        matched_convictions = match_convictions(market, convictions)

        bios_prob, disagreement, confidence = compute_bios_probability(
            matched_signals, matched_convictions, market["probability"]
        )

        entry = {
            "market_id": market["id"],
            "question": market["question"],
            "market_probability": round(market["probability"], 4),
            "bios_probability": round(bios_prob, 4),
            "disagreement": round(disagreement, 4),
            "confidence": confidence,
            "volume": market["volume"],
            "category": market["category"],
            "url": market["url"],
            "end_date": market["end_date"],
            "signal_count": len(matched_signals),
            "conviction_count": len(matched_convictions),
            "matched_keywords": keywords[:10],
            "top_signals": matched_signals[:3],
            "top_convictions": matched_convictions[:2],
            "direction": "YES" if bios_prob > market["probability"] else "NO",
            "scanned_at": datetime.now(timezone.utc).isoformat(),
        }
        opportunities.append(entry)

    # Sort by disagreement descending
    opportunities.sort(key=lambda x: x["disagreement"], reverse=True)

    # Cache the scan
    save_json(LAST_SCAN_FILE, {
        "scanned_at": datetime.now(timezone.utc).isoformat(),
        "total_fetched": len(raw_markets),
        "volume_filtered": len(markets),
        "opportunities": opportunities,
    })

    print(f"[SCAN] Found {len(opportunities)} scored opportunities")
    print(f"[SCAN] High disagreement (>20%): "
          f"{sum(1 for o in opportunities if o['disagreement'] > 0.20)}")

    # Record predictions for tracking
    record_predictions(opportunities)

    return opportunities


def record_predictions(opportunities):
    """Record predictions with disagreement > 5% for future accuracy tracking."""
    history = load_prediction_history()
    now = datetime.now(timezone.utc).isoformat()

    for opp in opportunities:
        if opp["disagreement"] < 0.05:
            continue

        # Check if we already have an active prediction for this market
        existing = [
            p for p in history["predictions"]
            if p["market_id"] == opp["market_id"] and p.get("status") == "active"
        ]
        if existing:
            # Update the latest prediction
            existing[0]["bios_probability"] = opp["bios_probability"]
            existing[0]["market_probability"] = opp["market_probability"]
            existing[0]["disagreement"] = opp["disagreement"]
            existing[0]["last_updated"] = now
            continue

        history["predictions"].append({
            "market_id": opp["market_id"],
            "question": opp["question"],
            "bios_probability": opp["bios_probability"],
            "market_probability": opp["market_probability"],
            "disagreement": opp["disagreement"],
            "direction": opp["direction"],
            "confidence": opp["confidence"],
            "recorded_at": now,
            "last_updated": now,
            "status": "active",
            "resolved_at": None,
            "actual_outcome": None,
            "bios_was_right": None,
        })

    save_prediction_history(history)


# -- Report Generation -------------------------------------------------------

def generate_report(opportunities=None):
    """Generate daily report from scan data."""
    if opportunities is None:
        cached = load_json(LAST_SCAN_FILE)
        opportunities = cached.get("opportunities", [])
        if not opportunities:
            print("[REPORT] No scan data found. Run --scan first.")
            return None

    now = datetime.now(timezone.utc)
    date_str = now.strftime("%Y-%m-%d")

    top_5 = opportunities[:5]

    report = {
        "date": date_str,
        "generated_at": now.isoformat(),
        "total_markets_scanned": len(opportunities),
        "high_disagreement_count": sum(
            1 for o in opportunities if o["disagreement"] > 0.20
        ),
        "medium_disagreement_count": sum(
            1 for o in opportunities if 0.10 < o["disagreement"] <= 0.20
        ),
        "top_5_opportunities": top_5,
        "all_opportunities": [
            o for o in opportunities if o["disagreement"] > 0.05
        ],
    }

    # Save report
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    report_path = REPORTS_DIR / f"polymarket-{date_str}.json"
    save_json(report_path, report)
    print(f"[REPORT] Saved to {report_path}")

    # Print summary
    print()
    print("=" * 70)
    print(f"  POLYMARKET RESEARCH REPORT -- {date_str}")
    print("=" * 70)
    print()
    print(f"  Markets scanned:        {report['total_markets_scanned']}")
    print(f"  High disagreement:      {report['high_disagreement_count']}")
    print(f"  Medium disagreement:    {report['medium_disagreement_count']}")
    print()

    if top_5:
        print("  -- TOP 5 ALPHA OPPORTUNITIES --")
        print()
        for i, opp in enumerate(top_5, 1):
            d_pct = opp["disagreement"] * 100
            arrow = "^" if opp["direction"] == "YES" else "v"
            tag = " ** ALERT **" if opp["disagreement"] > DISAGREEMENT_ALERT_THRESHOLD else ""
            print(f"  {i}. [{arrow}] {opp['question'][:60]}{tag}")
            print(f"     Market: {opp['market_probability']:.1%}  "
                  f"BIOS: {opp['bios_probability']:.1%}  "
                  f"Disagreement: {d_pct:.1f}%")
            print(f"     Volume: ${opp['volume']:,.0f}  "
                  f"Signals: {opp['signal_count']}  "
                  f"Convictions: {opp['conviction_count']}")
            if opp.get("url"):
                print(f"     {opp['url']}")
            print()
    else:
        print("  No opportunities with meaningful disagreement found.")
        print()

    return report


# -- Telegram Alerts ---------------------------------------------------------

def send_alerts(opportunities=None):
    """Send Telegram alerts for markets with disagreement > 20%."""
    if opportunities is None:
        cached = load_json(LAST_SCAN_FILE)
        opportunities = cached.get("opportunities", [])

    alerts = [o for o in opportunities if o["disagreement"] > DISAGREEMENT_ALERT_THRESHOLD]

    if not alerts:
        print("[ALERTS] No markets above 20% disagreement threshold.")
        return

    header = (
        "*BIOS Polymarket Alpha Scanner*\n"
        f"_{datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}_\n"
        f"{len(alerts)} market(s) with >20% BIOS disagreement:\n"
    )

    lines = [header]
    for opp in alerts[:10]:  # cap at 10 alerts
        arrow = "YES ^" if opp["direction"] == "YES" else "NO v"
        lines.append(
            f"\n*{opp['question'][:55]}*\n"
            f"  Market: {opp['market_probability']:.0%} | "
            f"BIOS: {opp['bios_probability']:.0%} | "
            f"Gap: {opp['disagreement']:.0%}\n"
            f"  Direction: {arrow} | "
            f"Vol: ${opp['volume']:,.0f}\n"
            f"  Signals: {opp['signal_count']} | "
            f"Confidence: {opp['confidence']}"
        )

    message = "\n".join(lines)
    send_telegram(message)
    print(f"[ALERTS] Sent {len(alerts)} alert(s)")


# -- History & Accuracy ------------------------------------------------------

def resolve_prediction(market_id, outcome):
    """
    Resolve a prediction after market closes.

    outcome: "yes" or "no" (what actually happened)
    """
    history = load_prediction_history()
    outcome = outcome.lower()
    if outcome not in ("yes", "no"):
        print(f"[ERROR] outcome must be 'yes' or 'no', got '{outcome}'")
        return

    found = False
    for pred in history["predictions"]:
        if pred["market_id"] == market_id and pred["status"] == "active":
            pred["status"] = "resolved"
            pred["resolved_at"] = datetime.now(timezone.utc).isoformat()
            pred["actual_outcome"] = outcome

            # Determine who was right
            actual_prob = 1.0 if outcome == "yes" else 0.0
            bios_error = abs(pred["bios_probability"] - actual_prob)
            market_error = abs(pred["market_probability"] - actual_prob)

            pred["bios_error"] = round(bios_error, 4)
            pred["market_error"] = round(market_error, 4)
            pred["bios_was_right"] = bios_error < market_error

            # Update stats
            history["stats"]["total_resolved"] += 1
            if pred["bios_was_right"]:
                history["stats"]["bios_correct"] += 1
            else:
                history["stats"]["market_correct"] += 1

            # Move to resolved list
            history["resolved"].append(pred.copy())
            found = True
            break

    if not found:
        print(f"[ERROR] No active prediction found for market_id={market_id}")
        return

    # Remove from active predictions
    history["predictions"] = [
        p for p in history["predictions"]
        if not (p["market_id"] == market_id and p["status"] == "resolved")
    ]

    save_prediction_history(history)
    pred_copy = history["resolved"][-1]
    winner = "BIOS" if pred_copy["bios_was_right"] else "MARKET"
    print(f"[RESOLVED] {pred_copy['question'][:50]}")
    print(f"  Outcome: {outcome.upper()}")
    print(f"  BIOS error: {pred_copy['bios_error']:.1%} vs Market error: {pred_copy['market_error']:.1%}")
    print(f"  Winner: {winner}")


def show_history():
    """Display prediction accuracy history."""
    history = load_prediction_history()
    stats = history["stats"]
    resolved = history["resolved"]
    active = [p for p in history["predictions"] if p["status"] == "active"]

    print()
    print("=" * 70)
    print("  BIOS vs MARKET -- Prediction Accuracy History")
    print("=" * 70)
    print()

    total = stats["total_resolved"]
    if total > 0:
        bios_rate = stats["bios_correct"] / total * 100
        market_rate = stats["market_correct"] / total * 100

        print(f"  Total resolved:    {total}")
        print(f"  BIOS correct:      {stats['bios_correct']} ({bios_rate:.1f}%)")
        print(f"  Market correct:    {stats['market_correct']} ({market_rate:.1f}%)")
        print()

        # Bar visualization
        bios_bar = "#" * int(bios_rate / 5) + "." * (20 - int(bios_rate / 5))
        market_bar = "#" * int(market_rate / 5) + "." * (20 - int(market_rate / 5))
        print(f"  BIOS:   [{bios_bar}] {bios_rate:.1f}%")
        print(f"  Market: [{market_bar}] {market_rate:.1f}%")
        print()

        # Recent resolved
        if resolved:
            print("  -- RECENT RESOLVED --")
            for r in resolved[-10:]:
                winner = "BIOS" if r["bios_was_right"] else "MKT"
                print(f"  [{winner:4s}] {r['question'][:45]}  "
                      f"BIOS={r['bios_probability']:.0%} "
                      f"MKT={r['market_probability']:.0%} "
                      f"Actual={r['actual_outcome'].upper()}")
            print()
    else:
        print("  No resolved predictions yet.")
        print("  Run --scan to start tracking, then resolve with:")
        print("    python3 polymarket_research.py --resolve MARKET_ID yes|no")
        print()

    # Active predictions
    if active:
        print(f"  -- ACTIVE PREDICTIONS ({len(active)}) --")
        for p in active[:15]:
            d_pct = p["disagreement"] * 100
            print(f"  [{p['direction']:3s}] {p['question'][:45]}  "
                  f"Gap={d_pct:.0f}%  "
                  f"BIOS={p['bios_probability']:.0%} "
                  f"MKT={p['market_probability']:.0%}")
        if len(active) > 15:
            print(f"  ... and {len(active) - 15} more")
        print()


# -- CLI ---------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="BIOS Polymarket Research Automation -- Alpha Scanner"
    )
    parser.add_argument("--scan", action="store_true",
                        help="Full market scan, cross-reference BIOS, generate report")
    parser.add_argument("--report", action="store_true",
                        help="Generate report from last scan data")
    parser.add_argument("--history", action="store_true",
                        help="Show prediction accuracy history")
    parser.add_argument("--alerts-only", action="store_true",
                        help="Only send Telegram alerts for disagreement > 20%%")
    parser.add_argument("--resolve", nargs=2, metavar=("MARKET_ID", "OUTCOME"),
                        help="Resolve a prediction: --resolve MARKET_ID yes|no")

    args = parser.parse_args()

    if not any([args.scan, args.report, args.history, args.alerts_only, args.resolve]):
        parser.print_help()
        return

    if args.scan:
        opportunities = scan_markets()
        generate_report(opportunities)
        send_alerts(opportunities)

    elif args.report:
        generate_report()

    elif args.history:
        show_history()

    elif args.alerts_only:
        send_alerts()

    elif args.resolve:
        market_id, outcome = args.resolve
        resolve_prediction(market_id, outcome)


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
Polymarket Trading Assistant — BIOS Conviction-Based Decision Support

Reads BIOS conviction scores + social signals to generate trade suggestions.
Manual decision support only. No API trading.

Usage:
    python3 polymarket_assistant.py suggest
    python3 polymarket_assistant.py trade "Will X happen" long 50 0.65
    python3 polymarket_assistant.py close TRADE_ID win
    python3 polymarket_assistant.py stats
    python3 polymarket_assistant.py accuracy
"""

import json
import os
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path

# ── Paths ──────────────────────────────────────────────────────────────────────

BASE_DIR = Path(__file__).parent
BIOS_STORAGE = BASE_DIR.parent / "storage"
CONVICTIONS_FILE = BIOS_STORAGE / "convictions.json"
SIGNALS_FILE = BIOS_STORAGE / "social_signals.json"
POSITIONS_FILE = BASE_DIR / "positions.json"
ACCURACY_FILE = BASE_DIR / "accuracy.json"


# ── Data Loaders ───────────────────────────────────────────────────────────────

def load_json(path, default=None):
    if default is None:
        default = {}
    try:
        with open(path, "r") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return default


def save_json(path, data):
    with open(path, "w") as f:
        json.dump(data, f, indent=2, default=str)


def load_convictions():
    data = load_json(CONVICTIONS_FILE)
    return data.get("convictions", [])


def load_signals():
    return load_json(SIGNALS_FILE, default=[])


def load_positions():
    data = load_json(POSITIONS_FILE, default={"trades": [], "next_id": 1})
    if "trades" not in data:
        data = {"trades": [], "next_id": 1}
    return data


def load_accuracy():
    return load_json(ACCURACY_FILE, default={
        "suggestions": [],
        "by_level": {"HIGH": {"correct": 0, "total": 0},
                     "MEDIUM": {"correct": 0, "total": 0},
                     "LOW": {"correct": 0, "total": 0}}
    })


# ── Sentiment Analysis ────────────────────────────────────────────────────────

def get_fear_greed(signals):
    """Extract most recent Fear & Greed score from social signals."""
    fg_signals = [s for s in signals if s.get("source") == "fear_greed_index"]
    if not fg_signals:
        return None, "unknown"
    # Sort by timestamp descending, take most recent
    fg_signals.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
    latest = fg_signals[0]
    score = latest.get("score", 50)
    if score <= 25:
        label = "extreme_fear"
    elif score <= 40:
        label = "fear"
    elif score <= 60:
        label = "neutral"
    elif score <= 75:
        label = "greed"
    else:
        label = "extreme_greed"
    return score, label


def classify_sentiment(conviction):
    """Classify a conviction's sentiment as bullish, bearish, or neutral."""
    sent = conviction.get("sentiment", 50)
    if sent >= 55:
        return "bullish"
    elif sent <= 35:
        return "bearish"
    else:
        return "neutral"


def count_confirming_sources(conviction):
    """Count unique source categories (deduping reddit sub-sources)."""
    sources = conviction.get("sources", [])
    categories = set()
    for s in sources:
        if s.startswith("reddit"):
            categories.add("reddit")
        else:
            categories.add(s)
    return len(categories)


# ── Suggestion Engine ──────────────────────────────────────────────────────────

def generate_suggestions():
    """Generate trade suggestions from conviction data + social signals."""
    convictions = load_convictions()
    signals = load_signals()
    fg_score, fg_label = get_fear_greed(signals)

    suggestions = []

    for conv in convictions:
        topic = conv["topic"]
        score = conv["score"]
        level = conv["level"]
        sentiment = classify_sentiment(conv)
        source_count = count_confirming_sources(conv)
        cross_confirmed = source_count >= 3

        # Determine action
        if level == "HIGH" and score >= 75:
            if sentiment == "bullish":
                action = "LONG"
                confidence = "high"
            elif sentiment == "bearish":
                action = "SHORT"
                confidence = "high"
            else:
                action = "WATCH"
                confidence = "medium"
        elif level == "MEDIUM" and 50 <= score < 75:
            action = "WATCH"
            confidence = "medium"
        else:
            action = "SKIP"
            confidence = "low"

        # Boost confidence if cross-source confirmed
        if cross_confirmed and action != "SKIP":
            if confidence == "medium":
                confidence = "high"
            elif confidence == "high":
                confidence = "very_high"

        if action == "SKIP":
            continue

        suggestions.append({
            "topic": topic,
            "conviction_score": score,
            "conviction_level": level,
            "sentiment": sentiment,
            "sentiment_raw": conv.get("sentiment", 0),
            "action": action,
            "confidence": confidence,
            "source_count": source_count,
            "cross_confirmed": cross_confirmed,
            "velocity": conv.get("velocity", 0),
            "volume": conv.get("volume", 0),
        })

    # Sort: actionable first (LONG/SHORT before WATCH), then by conviction score
    action_order = {"LONG": 0, "SHORT": 1, "WATCH": 2}
    suggestions.sort(key=lambda x: (action_order.get(x["action"], 3), -x["conviction_score"]))

    return suggestions, fg_score, fg_label


def print_suggestions():
    """Print formatted trade suggestions."""
    suggestions, fg_score, fg_label = generate_suggestions()

    print("=" * 70)
    print("  POLYMARKET TRADING ASSISTANT — BIOS Conviction Signals")
    print("=" * 70)
    print()

    if fg_score is not None:
        fg_bar = "█" * (fg_score // 5) + "░" * (20 - fg_score // 5)
        print(f"  Fear & Greed Index: {fg_score}/100 [{fg_label.upper().replace('_', ' ')}]")
        print(f"  [{fg_bar}]")
    else:
        print("  Fear & Greed Index: unavailable")
    print()

    if not suggestions:
        print("  No actionable signals right now.")
        return

    # Print actionable trades
    actionable = [s for s in suggestions if s["action"] in ("LONG", "SHORT")]
    watchlist = [s for s in suggestions if s["action"] == "WATCH"]

    if actionable:
        print("  ── ACTIONABLE ─────────────────────────────────────────────")
        for s in actionable:
            arrow = "▲" if s["action"] == "LONG" else "▼"
            xc = " [CROSS-CONFIRMED]" if s["cross_confirmed"] else ""
            print(f"  {arrow} {s['action']:5s}  {s['topic']:20s}  "
                  f"score={s['conviction_score']:.1f}  "
                  f"sentiment={s['sentiment']:8s}  "
                  f"confidence={s['confidence']}{xc}")
            print(f"          velocity={s['velocity']:.0f}  "
                  f"volume={s['volume']:.0f}  "
                  f"sources={s['source_count']}")
        print()

    if watchlist:
        print("  ── WATCH LIST ─────────────────────────────────────────────")
        for s in watchlist:
            xc = " [CROSS-CONFIRMED]" if s["cross_confirmed"] else ""
            print(f"  ◎ WATCH  {s['topic']:20s}  "
                  f"score={s['conviction_score']:.1f}  "
                  f"sentiment={s['sentiment']:8s}  "
                  f"confidence={s['confidence']}{xc}")
        print()

    print("  ── NOTES ──────────────────────────────────────────────────")
    if fg_score is not None and fg_score <= 25:
        print("  ⚠  Extreme Fear detected — contrarian opportunities possible")
        print("     but also elevated risk. Size positions conservatively.")
    elif fg_score is not None and fg_score >= 75:
        print("  ⚠  Extreme Greed detected — market may be overextended.")
        print("     Consider taking profits or tightening stops.")
    print(f"  Generated: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}")
    print()


# ── Position Tracker ───────────────────────────────────────────────────────────

def log_trade(market, direction, amount, odds):
    """Log a new trade."""
    positions = load_positions()
    trade_id = positions["next_id"]
    positions["next_id"] = trade_id + 1

    # Capture conviction state at time of trade
    convictions = load_convictions()
    matching = [c for c in convictions if c["topic"].lower() in market.lower()
                or market.lower() in c["topic"].lower()]

    trade = {
        "id": trade_id,
        "market": market,
        "direction": direction.upper(),
        "amount": float(amount),
        "odds": float(odds),
        "status": "open",
        "opened_at": datetime.now(timezone.utc).isoformat(),
        "closed_at": None,
        "result": None,
        "pnl": None,
        "conviction_at_entry": matching[0] if matching else None,
    }

    positions["trades"].append(trade)
    save_json(POSITIONS_FILE, positions)

    potential_profit = float(amount) * (1.0 / float(odds) - 1.0)
    print(f"\n  Trade #{trade_id} logged:")
    print(f"    Market:    {market}")
    print(f"    Direction: {direction.upper()}")
    print(f"    Amount:    ${amount}")
    print(f"    Odds:      {odds}")
    print(f"    Potential:  +${potential_profit:.2f} if correct")
    if matching:
        print(f"    Conviction: {matching[0]['score']:.1f} ({matching[0]['level']})")
    print()
    return trade_id


def close_trade(trade_id, result):
    """Close a trade with result: win, loss, or push."""
    positions = load_positions()
    trade_id = int(trade_id)
    result = result.lower()

    if result not in ("win", "loss", "push"):
        print(f"  Error: result must be 'win', 'loss', or 'push'. Got '{result}'")
        return

    trade = None
    for t in positions["trades"]:
        if t["id"] == trade_id:
            trade = t
            break

    if trade is None:
        print(f"  Error: trade #{trade_id} not found.")
        return

    if trade["status"] == "closed":
        print(f"  Error: trade #{trade_id} already closed.")
        return

    trade["status"] = "closed"
    trade["closed_at"] = datetime.now(timezone.utc).isoformat()
    trade["result"] = result

    if result == "win":
        trade["pnl"] = trade["amount"] * (1.0 / trade["odds"] - 1.0)
    elif result == "loss":
        trade["pnl"] = -trade["amount"]
    else:  # push
        trade["pnl"] = 0.0

    save_json(POSITIONS_FILE, positions)

    # Update accuracy tracking
    accuracy = load_accuracy()
    entry_conv = trade.get("conviction_at_entry")
    if entry_conv:
        level = entry_conv.get("level", "MEDIUM")
        if level in accuracy["by_level"]:
            accuracy["by_level"][level]["total"] += 1
            if result == "win":
                accuracy["by_level"][level]["correct"] += 1

    accuracy["suggestions"].append({
        "trade_id": trade_id,
        "market": trade["market"],
        "direction": trade["direction"],
        "conviction_level": entry_conv.get("level", "unknown") if entry_conv else "unknown",
        "conviction_score": entry_conv.get("score", 0) if entry_conv else 0,
        "result": result,
        "pnl": trade["pnl"],
        "closed_at": trade["closed_at"],
    })
    save_json(ACCURACY_FILE, accuracy)

    pnl_str = f"+${trade['pnl']:.2f}" if trade["pnl"] >= 0 else f"-${abs(trade['pnl']):.2f}"
    print(f"\n  Trade #{trade_id} closed:")
    print(f"    Market:  {trade['market']}")
    print(f"    Result:  {result.upper()}")
    print(f"    P/L:     {pnl_str}")
    print()


def portfolio_summary():
    """Print portfolio summary with P/L and win rate."""
    positions = load_positions()
    trades = positions.get("trades", [])

    if not trades:
        print("\n  No trades logged yet.\n")
        return

    open_trades = [t for t in trades if t["status"] == "open"]
    closed_trades = [t for t in trades if t["status"] == "closed"]

    total_pnl = sum(t.get("pnl", 0) or 0 for t in closed_trades)
    total_invested = sum(t.get("amount", 0) for t in closed_trades)
    wins = sum(1 for t in closed_trades if t.get("result") == "win")
    losses = sum(1 for t in closed_trades if t.get("result") == "loss")
    pushes = sum(1 for t in closed_trades if t.get("result") == "push")

    win_rate = (wins / len(closed_trades) * 100) if closed_trades else 0
    roi = (total_pnl / total_invested * 100) if total_invested > 0 else 0

    open_exposure = sum(t.get("amount", 0) for t in open_trades)

    print()
    print("=" * 60)
    print("  PORTFOLIO SUMMARY")
    print("=" * 60)
    print()
    print(f"  Total Trades:    {len(trades)}")
    print(f"  Open:            {len(open_trades)}")
    print(f"  Closed:          {len(closed_trades)}")
    print()

    if closed_trades:
        print(f"  Wins:            {wins}")
        print(f"  Losses:          {losses}")
        print(f"  Pushes:          {pushes}")
        print(f"  Win Rate:        {win_rate:.1f}%")
        print()

        pnl_str = f"+${total_pnl:.2f}" if total_pnl >= 0 else f"-${abs(total_pnl):.2f}"
        print(f"  Total P/L:       {pnl_str}")
        print(f"  Total Invested:  ${total_invested:.2f}")
        print(f"  ROI:             {roi:+.1f}%")
    print()

    if open_trades:
        print(f"  Open Exposure:   ${open_exposure:.2f}")
        print()
        print("  ── OPEN POSITIONS ──────────────────────────────────────")
        for t in open_trades:
            arrow = "▲" if t["direction"] == "LONG" else "▼"
            print(f"  #{t['id']:3d} {arrow} {t['direction']:5s}  "
                  f"${t['amount']:<8.2f} @ {t['odds']:.2f}  "
                  f"{t['market']}")
        print()


# ── Accuracy Tracker ───────────────────────────────────────────────────────────

def print_accuracy():
    """Print prediction accuracy breakdown."""
    accuracy = load_accuracy()

    print()
    print("=" * 60)
    print("  PREDICTION ACCURACY — by Conviction Level")
    print("=" * 60)
    print()

    has_data = False
    for level in ("HIGH", "MEDIUM", "LOW"):
        stats = accuracy["by_level"].get(level, {"correct": 0, "total": 0})
        total = stats["total"]
        correct = stats["correct"]
        if total > 0:
            has_data = True
            rate = correct / total * 100
            bar_filled = int(rate / 5)
            bar = "█" * bar_filled + "░" * (20 - bar_filled)
            print(f"  {level:8s}  {correct}/{total}  ({rate:.1f}%)  [{bar}]")
        else:
            print(f"  {level:8s}  —  no data yet")

    print()

    suggestions = accuracy.get("suggestions", [])
    if suggestions:
        print("  ── RECENT RESULTS ─────────────────────────────────────")
        for s in suggestions[-10:]:  # last 10
            result_icon = {"win": "✓", "loss": "✗", "push": "—"}.get(s["result"], "?")
            pnl = s.get("pnl", 0)
            pnl_str = f"+${pnl:.2f}" if pnl >= 0 else f"-${abs(pnl):.2f}"
            print(f"  {result_icon} #{s['trade_id']:3d}  "
                  f"conv={s['conviction_score']:.0f} ({s['conviction_level']:6s})  "
                  f"{pnl_str:>10s}  {s['market']}")
        print()

        # Overall stats
        total_suggestions = len(suggestions)
        total_wins = sum(1 for s in suggestions if s["result"] == "win")
        overall_pnl = sum(s.get("pnl", 0) for s in suggestions)
        print(f"  Overall: {total_wins}/{total_suggestions} wins "
              f"({total_wins/total_suggestions*100:.1f}%)  "
              f"P/L: {'+'if overall_pnl>=0 else ''}{overall_pnl:.2f}")
    else:
        print("  No closed trades to analyze yet.")
        print("  Log trades with 'trade' and close them with 'close' to build data.")
    print()


# ── CLI ────────────────────────────────────────────────────────────────────────

def print_usage():
    print("""
  Polymarket Trading Assistant — BIOS Conviction Signals

  Usage:
    python3 polymarket_assistant.py suggest
        Show current trade suggestions based on conviction data

    python3 polymarket_assistant.py trade "market name" long|short amount odds
        Log a trade. Example:
        python3 polymarket_assistant.py trade "Will BTC hit 100k" long 50 0.65

    python3 polymarket_assistant.py close TRADE_ID win|loss|push
        Close a trade with its result

    python3 polymarket_assistant.py stats
        Portfolio summary — P/L, win rate, ROI, open positions

    python3 polymarket_assistant.py accuracy
        Prediction accuracy breakdown by conviction level
""")


def main():
    if len(sys.argv) < 2:
        print_usage()
        return

    cmd = sys.argv[1].lower()

    if cmd == "suggest":
        print_suggestions()

    elif cmd == "trade":
        if len(sys.argv) < 6:
            print("  Usage: python3 polymarket_assistant.py trade \"market\" long|short amount odds")
            print("  Example: python3 polymarket_assistant.py trade \"Will BTC hit 100k\" long 50 0.65")
            return
        market = sys.argv[2]
        direction = sys.argv[3]
        amount = sys.argv[4]
        odds = sys.argv[5]
        if direction.lower() not in ("long", "short"):
            print(f"  Error: direction must be 'long' or 'short'. Got '{direction}'")
            return
        try:
            float(amount)
            float(odds)
        except ValueError:
            print("  Error: amount and odds must be numbers.")
            return
        log_trade(market, direction, amount, odds)

    elif cmd == "close":
        if len(sys.argv) < 4:
            print("  Usage: python3 polymarket_assistant.py close TRADE_ID win|loss|push")
            return
        close_trade(sys.argv[2], sys.argv[3])

    elif cmd == "stats":
        portfolio_summary()

    elif cmd == "accuracy":
        print_accuracy()

    else:
        print(f"  Unknown command: {cmd}")
        print_usage()


if __name__ == "__main__":
    main()

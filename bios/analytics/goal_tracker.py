#!/usr/bin/env python3
"""Daily revenue goal tracker. $10K/month target broken into daily wins."""

import json, os, sys, argparse, math
from datetime import datetime, timedelta
from pathlib import Path
from urllib.request import Request, urlopen

DATA = Path(__file__).parent / "data" / "sales.json"
MILESTONES = [1, 10, 100, 500, 1000, 5000, 10000]
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID", "")

def load():
    if not DATA.exists():
        return {"month_goal": 10000, "sales": []}
    with open(DATA) as f:
        return json.load(f)

def save(data):
    DATA.parent.mkdir(parents=True, exist_ok=True)
    with open(DATA, "w") as f:
        json.dump(data, f, indent=2)

def sales_this_month(data, now=None):
    now = now or datetime.now()
    prefix = now.strftime("%Y-%m")
    return [s for s in data["sales"] if s["date"].startswith(prefix)]

def sales_this_week(data, now=None):
    now = now or datetime.now()
    week_start = now - timedelta(days=now.weekday())
    start = week_start.strftime("%Y-%m-%d")
    end = now.strftime("%Y-%m-%d")
    return [s for s in data["sales"] if start <= s["date"] <= end]

def progress_bar(current, goal, width=30):
    pct = min(current / goal, 1.0) if goal > 0 else 0
    filled = int(width * pct)
    bar = "█" * filled + "░" * (width - filled)
    return f"[{bar}] {pct*100:.1f}%"

def streak(data):
    dates = sorted(set(s["date"] for s in data["sales"]), reverse=True)
    if not dates:
        return 0
    count = 0
    check = datetime.now().date()
    for d in dates:
        dt = datetime.strptime(d, "%Y-%m-%d").date()
        if dt == check:
            count += 1
            check -= timedelta(days=1)
        elif dt < check:
            break
    return count

def stats(data):
    if not data["sales"]:
        return {"best": 0, "worst": 0, "avg": 0}
    by_day = {}
    for s in data["sales"]:
        by_day[s["date"]] = by_day.get(s["date"], 0) + s["amount"]
    vals = list(by_day.values())
    return {"best": max(vals), "worst": min(vals), "avg": sum(vals) / len(vals)}

def hit_milestones(data):
    total = sum(s["amount"] for s in data["sales"])
    return [m for m in MILESTONES if total >= m]

def pending_milestones(data):
    total = sum(s["amount"] for s in data["sales"])
    return [m for m in MILESTONES if total < m]

def cmd_today(data):
    now = datetime.now()
    month_sales = sales_this_month(data, now)
    total = sum(s["amount"] for s in month_sales)
    goal = data.get("month_goal", 10000)
    day_of_month = now.day
    days_in_month = (now.replace(month=now.month % 12 + 1, day=1) - timedelta(days=1)).day if now.month < 12 else 31
    daily_target = goal / days_in_month
    days_left = days_in_month - day_of_month + 1
    remaining = max(goal - total, 0)
    needed_per_day = remaining / days_left if days_left > 0 else remaining
    projected = (total / day_of_month) * days_in_month if day_of_month > 0 else 0
    today_sales = [s for s in month_sales if s["date"] == now.strftime("%Y-%m-%d")]
    today_total = sum(s["amount"] for s in today_sales)
    st = stats(data)

    print(f"\n  GOAL TRACKER -- {now.strftime('%B %d, %Y')}")
    print(f"  {'='*44}")
    print(f"  Monthly goal:      ${goal:,.0f}")
    print(f"  Earned this month: ${total:,.2f}")
    print(f"  {progress_bar(total, goal)}")
    print(f"  Today:             ${today_total:,.2f}")
    print(f"  Daily target:      ${daily_target:,.2f}")
    print(f"  Needed/day:        ${needed_per_day:,.2f}  ({days_left} days left)")
    print(f"  Projected month:   ${projected:,.2f}")
    print(f"  Streak:            {streak(data)} days")
    print(f"  Best day:          ${st['best']:,.2f}")
    print(f"  Worst day:         ${st['worst']:,.2f}")
    print(f"  Average day:       ${st['avg']:,.2f}")

    hit = hit_milestones(data)
    if hit:
        print(f"  Milestones hit:    {', '.join(f'${m:,}' for m in hit)}")
    nxt = pending_milestones(data)
    if nxt:
        print(f"  Next milestone:    ${nxt[0]:,}")
    print()

def cmd_week(data):
    now = datetime.now()
    week = sales_this_week(data, now)
    total = sum(s["amount"] for s in week)
    by_day = {}
    for s in week:
        by_day[s["date"]] = by_day.get(s["date"], 0) + s["amount"]
    print(f"\n  WEEK SUMMARY (Mon-Sun)")
    print(f"  {'='*44}")
    print(f"  Total: ${total:,.2f}")
    for d in sorted(by_day):
        label = datetime.strptime(d, "%Y-%m-%d").strftime("%a %m/%d")
        print(f"    {label}: ${by_day[d]:,.2f}")
    if not by_day:
        print("    No sales this week yet.")
    print()

def cmd_month(data):
    now = datetime.now()
    month = sales_this_month(data, now)
    total = sum(s["amount"] for s in month)
    goal = data.get("month_goal", 10000)
    by_day = {}
    for s in month:
        by_day[s["date"]] = by_day.get(s["date"], 0) + s["amount"]
    print(f"\n  MONTH SUMMARY -- {now.strftime('%B %Y')}")
    print(f"  {'='*44}")
    print(f"  {progress_bar(total, goal)}")
    print(f"  Total: ${total:,.2f} / ${goal:,.0f}")
    print(f"  Days with sales: {len(by_day)}")
    if by_day:
        print(f"  Top day: {max(by_day, key=by_day.get)} (${max(by_day.values()):,.2f})")
    for d in sorted(by_day):
        label = datetime.strptime(d, "%Y-%m-%d").strftime("%d %a")
        bar_w = int(min(by_day[d] / (goal / 30) * 15, 30))
        print(f"    {label} {'█' * bar_w} ${by_day[d]:,.2f}")
    print()

def build_morning_msg(data):
    now = datetime.now()
    month_sales = sales_this_month(data, now)
    total = sum(s["amount"] for s in month_sales)
    goal = data.get("month_goal", 10000)
    day = now.day
    days_in_month = (now.replace(month=now.month % 12 + 1, day=1) - timedelta(days=1)).day if now.month < 12 else 31
    remaining = max(goal - total, 0)
    days_left = days_in_month - day + 1
    needed = remaining / days_left if days_left > 0 else remaining
    pct = (total / goal) * 100 if goal > 0 else 0
    s = streak(data)

    msg = f"Day {day} of {now.strftime('%B')}.\n"
    msg += f"${total:,.2f} earned. ${remaining:,.2f} to go.\n"
    msg += f"You need ${needed:,.2f}/day to hit ${goal:,}.\n"
    msg += f"{progress_bar(total, goal)}\n"
    if s > 1:
        msg += f"Streak: {s} days.\n"

    hit = hit_milestones(data)
    nxt = pending_milestones(data)
    if hit and hit[-1] >= 100:
        msg += f"Milestones cleared: {', '.join(f'${m:,}' for m in hit)}\n"
    if nxt:
        to_next = nxt[0] - total
        msg += f"Next milestone: ${nxt[0]:,} (${to_next:,.2f} away)\n"

    if pct >= 100:
        msg += "\nGOAL HIT. Keep stacking."
    elif pct >= 75:
        msg += "\nAlmost there. Push."
    elif pct >= 50:
        msg += "\nHalfway. Stay locked in."
    return msg

def send_telegram(msg):
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        print("  Set TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID env vars.")
        print(f"\n  Morning message preview:\n")
        for line in msg.split("\n"):
            print(f"  {line}")
        print()
        return
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = json.dumps({"chat_id": TELEGRAM_CHAT_ID, "text": msg}).encode()
    req = Request(url, data=payload, headers={"Content-Type": "application/json"})
    try:
        urlopen(req)
        print("  Morning message sent to Telegram.")
    except Exception as e:
        print(f"  Telegram send failed: {e}")
        print(f"  Message was:\n{msg}")

def cmd_milestones(data):
    total = sum(s["amount"] for s in data["sales"])
    print(f"\n  MILESTONES -- Total all-time: ${total:,.2f}")
    print(f"  {'='*44}")
    for m in MILESTONES:
        if total >= m:
            print(f"  [x] ${m:,}")
        else:
            diff = m - total
            print(f"  [ ] ${m:,}  (${diff:,.2f} to go)")
    print()

def cmd_add(data, amount, note=""):
    today = datetime.now().strftime("%Y-%m-%d")
    entry = {"date": today, "amount": float(amount), "note": note}
    data["sales"].append(entry)
    save(data)
    print(f"  Added ${float(amount):,.2f} for {today}. {note}")
    total = sum(s["amount"] for s in data["sales"])
    new_milestones = [m for m in MILESTONES if total >= m and total - float(amount) < m]
    for m in new_milestones:
        print(f"\n  *** MILESTONE UNLOCKED: ${m:,}! ***\n")

def main():
    p = argparse.ArgumentParser(description="$10K/month revenue goal tracker")
    p.add_argument("--today", action="store_true", help="Today's dashboard")
    p.add_argument("--week", action="store_true", help="Weekly summary")
    p.add_argument("--month", action="store_true", help="Monthly summary")
    p.add_argument("--morning", action="store_true", help="Send morning Telegram message")
    p.add_argument("--milestones", action="store_true", help="Milestone progress")
    p.add_argument("--add", type=float, help="Log a sale amount")
    p.add_argument("--note", default="", help="Note for --add")
    args = p.parse_args()

    data = load()

    if args.add is not None:
        cmd_add(data, args.add, args.note)
        return
    if args.week:
        cmd_week(data)
        return
    if args.month:
        cmd_month(data)
        return
    if args.morning:
        msg = build_morning_msg(data)
        send_telegram(msg)
        return
    if args.milestones:
        cmd_milestones(data)
        return

    cmd_today(data)

if __name__ == "__main__":
    main()

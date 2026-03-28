#!/usr/bin/env python3
"""Customer segmentation engine. Zero deps. Under 200 lines.

Reads: analytics/data/sales.json, analytics/data/leads.json, analytics/data/views.json
Writes: reports/segments-YYYY-MM-DD.json

CLI:
  python segmentation.py --analyze          Full analysis to stdout
  python segmentation.py --report           Generate dated JSON report
  python segmentation.py --segment "high-value"   Show one segment
"""

import json, os, sys, argparse
from datetime import datetime
from collections import defaultdict
from pathlib import Path

BASE = Path(__file__).resolve().parent
DATA = BASE / "data"
REPORTS = BASE.parent / "reports"

def load(name):
    p = DATA / name
    if not p.exists():
        return []
    with open(p) as f:
        return json.load(f)

def build_segments():
    sales = load("sales.json")
    leads = load("leads.json")
    views = load("views.json")

    # Index customers
    buyers = defaultdict(lambda: {"orders": 0, "spent": 0.0, "products": []})
    viewer_ids = set()
    lead_ids = set()

    for s in sales:
        cid = s.get("customer_id") or s.get("email") or s.get("id", "unknown")
        buyers[cid]["orders"] += 1
        buyers[cid]["spent"] += float(s.get("amount", s.get("price", s.get("total", 0))))
        prod = s.get("product", s.get("product_name", s.get("item", "")))
        if prod:
            buyers[cid]["products"].append(prod)

    for v in views:
        vid = v.get("customer_id") or v.get("visitor_id") or v.get("email") or v.get("id", "anon")
        viewer_ids.add(vid)

    for l in leads:
        lid = l.get("customer_id") or l.get("email") or l.get("id", "unknown")
        lead_ids.add(lid)

    buyer_ids = set(buyers.keys())

    # Segment assignment
    segments = {
        "browsers": {"ids": [], "label": "Visited but didn't buy"},
        "one_time": {"ids": [], "label": "Bought 1 product"},
        "repeat":   {"ids": [], "label": "Bought 2+ products"},
        "high_value": {"ids": [], "label": "Spent $50+"},
        "lead_magnet": {"ids": [], "label": "Got free product only"},
    }

    for vid in viewer_ids:
        if vid not in buyer_ids and vid not in lead_ids:
            segments["browsers"]["ids"].append(vid)

    for lid in lead_ids:
        if lid not in buyer_ids:
            segments["lead_magnet"]["ids"].append(lid)

    for cid, data in buyers.items():
        if data["spent"] >= 50:
            segments["high_value"]["ids"].append(cid)
        if data["orders"] == 1:
            segments["one_time"]["ids"].append(cid)
        elif data["orders"] >= 2:
            segments["repeat"]["ids"].append(cid)

    # Build stats per segment
    campaigns = {
        "browsers":    "Retarget with discount code. Subject: 'Still thinking it over? Here's 10% off'",
        "one_time":    "Cross-sell related products. Subject: 'You might also like...'",
        "repeat":      "Loyalty program invite + early access to new drops",
        "high_value":  "VIP treatment. Exclusive bundles, personal thank-you, referral program",
        "lead_magnet": "Nurture sequence. Send 3 value emails then soft pitch paid product",
    }

    results = {}
    for key, seg in segments.items():
        ids = seg["ids"]
        count = len(ids)
        if count == 0:
            avg_spend = 0.0
            top_products = []
        else:
            total_spend = sum(buyers[i]["spent"] for i in ids if i in buyers)
            avg_spend = round(total_spend / max(count, 1), 2)
            prod_count = defaultdict(int)
            for i in ids:
                if i in buyers:
                    for p in buyers[i]["products"]:
                        prod_count[p] += 1
            top_products = sorted(prod_count, key=prod_count.get, reverse=True)[:5]

        results[key] = {
            "label": seg["label"],
            "count": count,
            "avg_spend": avg_spend,
            "top_products": top_products,
            "recommended_action": campaigns[key],
        }

    return results

def print_segment(name, data):
    print(f"\n{'='*50}")
    print(f"  {name.upper()} - {data['label']}")
    print(f"{'='*50}")
    print(f"  Customers: {data['count']}")
    print(f"  Avg spend: ${data['avg_spend']:.2f}")
    print(f"  Top products: {', '.join(data['top_products']) if data['top_products'] else 'n/a'}")
    print(f"  Action: {data['recommended_action']}")

def cmd_analyze():
    segments = build_segments()
    total = sum(s["count"] for s in segments.values())
    print(f"\nCustomer Segmentation Report - {datetime.now().strftime('%Y-%m-%d')}")
    print(f"Total unique customers across segments: {total}")
    for name, data in segments.items():
        print_segment(name, data)
    print()

def cmd_report():
    segments = build_segments()
    REPORTS.mkdir(parents=True, exist_ok=True)
    fname = f"segments-{datetime.now().strftime('%Y-%m-%d')}.json"
    path = REPORTS / fname
    report = {
        "generated": datetime.now().isoformat(),
        "segments": segments,
        "total_customers": sum(s["count"] for s in segments.values()),
    }
    with open(path, "w") as f:
        json.dump(report, f, indent=2)
    print(f"Report saved to {path}")

def cmd_segment(name):
    segments = build_segments()
    # Normalize input
    key = name.lower().replace("-", "_").replace(" ", "_")
    aliases = {"highvalue": "high_value", "onetime": "one_time", "leadmagnet": "lead_magnet",
               "high_value": "high_value", "one_time": "one_time", "lead_magnet": "lead_magnet"}
    key = aliases.get(key, key)
    if key not in segments:
        print(f"Unknown segment: {name}")
        print(f"Available: {', '.join(segments.keys())}")
        sys.exit(1)
    print_segment(key, segments[key])

def main():
    parser = argparse.ArgumentParser(description="Customer segmentation engine")
    parser.add_argument("--analyze", action="store_true", help="Full analysis to stdout")
    parser.add_argument("--report", action="store_true", help="Generate dated JSON report")
    parser.add_argument("--segment", type=str, help="Show a specific segment")
    args = parser.parse_args()

    if not any([args.analyze, args.report, args.segment]):
        parser.print_help()
        sys.exit(0)

    if args.analyze:
        cmd_analyze()
    if args.report:
        cmd_report()
    if args.segment:
        cmd_segment(args.segment)

if __name__ == "__main__":
    main()

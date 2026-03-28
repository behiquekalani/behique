#!/usr/bin/env python3
"""
Overnight Machine -- Behike eBay Product Discovery Pipeline
Runs nightly. Discovers trending products, scores them, queues listing drafts for morning review.

Usage:
  python3 overnight_machine.py           # Full run
  python3 overnight_machine.py --test    # Run with dummy data
  python3 overnight_machine.py --dry-run # Run without saving to review folder
  python3 overnight_machine.py --setup   # Create ~/.overnight/ directory structure
  python3 overnight_machine.py --report  # Generate competitive landscape report

Machines:
  Ceiba  -- M4 Mac, main (this machine)
  Cobo   -- GTX 1080 Ti
  Hutia  -- Always-on server at 192.168.0.152
"""

import json
import os
import sys
import hashlib
import argparse
import random
import logging
from datetime import datetime, timedelta
from pathlib import Path

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------

OVERNIGHT_DIR = Path.home() / ".overnight"
CONFIG_PATH = OVERNIGHT_DIR / "config.json"
TRENDS_PATH = OVERNIGHT_DIR / "trends_cache.json"
REVIEW_DIR = OVERNIGHT_DIR / "review"
SNAPSHOTS_DIR = OVERNIGHT_DIR / "snapshots"
LOGS_DIR = OVERNIGHT_DIR / "logs"
MORNING_REPORT_PATH = OVERNIGHT_DIR / "morning_report.txt"

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------

logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] %(levelname)s -- %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
log = logging.getLogger("overnight_machine")


# ---------------------------------------------------------------------------
# 1. setup_directories
# ---------------------------------------------------------------------------

def setup_directories():
    """Create ~/.overnight/{logs,review,snapshots}/ and write template files."""
    dirs = [OVERNIGHT_DIR, LOGS_DIR, REVIEW_DIR, SNAPSHOTS_DIR]
    for d in dirs:
        d.mkdir(parents=True, exist_ok=True)
        log.info("Directory ready: %s", d)

    # Config template
    if not CONFIG_PATH.exists():
        default_config = {
            "margin_target": 0.30,
            "min_score": 65,
            "max_listings": 5,
            "listing_style": "professional",
            "price_range": {"min": 10, "max": 200},
            "excluded_categories": ["adult", "weapons"],
            "our_products_file": "~/.overnight/our_products.json"
        }
        CONFIG_PATH.write_text(json.dumps(default_config, indent=2))
        log.info("Config template written: %s", CONFIG_PATH)
    else:
        log.info("Config already exists, skipping: %s", CONFIG_PATH)

    # Trends cache template
    if not TRENDS_PATH.exists():
        sample_trends = [
            {"rank": 1, "name": "silicone kitchen utensil set", "category": "Home & Garden"},
            {"rank": 2, "name": "USB-C hub 7-in-1", "category": "Electronics"},
            {"rank": 3, "name": "resistance bands set", "category": "Sporting Goods"},
        ]
        TRENDS_PATH.write_text(json.dumps(sample_trends, indent=2))
        log.info("Trends cache template written: %s", TRENDS_PATH)
    else:
        log.info("Trends cache already exists, skipping: %s", TRENDS_PATH)

    print("\nOvernight Machine setup complete.")
    print(f"  Config:        {CONFIG_PATH}")
    print(f"  Trends cache:  {TRENDS_PATH}")
    print(f"  Review dir:    {REVIEW_DIR}")
    print(f"  Logs dir:      {LOGS_DIR}")
    print("\nNext steps:")
    print("  1. Edit ~/.overnight/config.json to set your margin target and price range")
    print("  2. Point your trends scraper to write ~/.overnight/trends_cache.json")
    print("  3. Run: python3 overnight_machine.py --test")


# ---------------------------------------------------------------------------
# 2. load_config
# ---------------------------------------------------------------------------

def load_config():
    """Load ~/.overnight/config.json. Returns defaults if file missing."""
    defaults = {
        "margin_target": 0.30,
        "min_score": 65,
        "max_listings": 5,
        "listing_style": "professional",
        "price_range": {"min": 10, "max": 200},
        "excluded_categories": ["adult", "weapons"],
        "our_products_file": "~/.overnight/our_products.json"
    }
    if not CONFIG_PATH.exists():
        log.warning("Config not found at %s. Using defaults.", CONFIG_PATH)
        return defaults
    try:
        data = json.loads(CONFIG_PATH.read_text())
        # Merge with defaults so new keys are always present
        merged = {**defaults, **data}
        return merged
    except Exception as e:
        log.error("Failed to load config: %s. Using defaults.", e)
        return defaults


# ---------------------------------------------------------------------------
# 3. load_trends
# ---------------------------------------------------------------------------

TEST_TRENDS = [
    {"rank": 1,  "name": "silicone kitchen utensil set",       "category": "Home & Garden"},
    {"rank": 2,  "name": "USB-C hub 7-in-1 multiport adapter", "category": "Electronics"},
    {"rank": 3,  "name": "resistance bands set 5 levels",       "category": "Sporting Goods"},
    {"rank": 4,  "name": "stainless steel water bottle 32oz",   "category": "Sports & Outdoors"},
    {"rank": 5,  "name": "LED desk lamp with USB charging port","category": "Electronics"},
    {"rank": 6,  "name": "foam roller deep tissue massage",     "category": "Health & Beauty"},
    {"rank": 7,  "name": "cable management box organizer",      "category": "Home & Garden"},
    {"rank": 8,  "name": "wireless phone charger stand 15W",    "category": "Electronics"},
    {"rank": 9,  "name": "yoga mat non-slip 6mm",               "category": "Sporting Goods"},
    {"rank": 10, "name": "bamboo cutting board set of 3",       "category": "Home & Garden"},
]


def load_trends(test_mode=False):
    """
    Load trends from ~/.overnight/trends_cache.json.
    In test mode returns hardcoded list of 10 sample trends.
    """
    if test_mode:
        log.info("Test mode: using hardcoded sample trends (%d items)", len(TEST_TRENDS))
        return TEST_TRENDS

    if not TRENDS_PATH.exists():
        log.warning(
            "Trends cache not found at %s. "
            "Run your trends scraper first, or use --test for dummy data.",
            TRENDS_PATH
        )
        return []

    try:
        data = json.loads(TRENDS_PATH.read_text())
        if not isinstance(data, list):
            log.error("trends_cache.json must be a JSON array. Got: %s", type(data).__name__)
            return []
        log.info("Loaded %d trends from cache.", len(data))
        return data
    except Exception as e:
        log.error("Failed to load trends cache: %s", e)
        return []


# ---------------------------------------------------------------------------
# 4. score_opportunity
# ---------------------------------------------------------------------------

def score_opportunity(trend, config):
    """
    Score a trend 0-100.
    Returns dict with: score, reasoning, estimated_price_range
    """
    name = trend.get("name", "unknown")
    rank = trend.get("rank", 50)

    # Demand factor: rank 1 = 1.0, rank 50+ = 0.1
    demand_factor = max(0.1, 1.0 - (rank - 1) * 0.018)

    # Deterministic competition estimate based on name hash
    name_hash = int(hashlib.md5(name.encode()).hexdigest(), 16)
    rng = random.Random(name_hash)
    competition_raw = rng.uniform(0.2, 0.9)
    competition_score = 1.0 - competition_raw  # lower competition = higher score

    # Margin estimate: use price range midpoint vs eBay fee model
    price_min = config["price_range"]["min"]
    price_max = config["price_range"]["max"]
    mid_price = (price_min + price_max) / 2
    # Rough margin estimate: assume COGS is 55-65% of sell price at midpoint
    cogs_factor = rng.uniform(0.50, 0.65)
    ebay_fee_factor = 0.1325  # ~13.25% final value fee
    margin_estimate = 1.0 - cogs_factor - ebay_fee_factor
    margin_score = min(1.0, max(0.0, margin_estimate / config["margin_target"]))

    # Weighted composite score
    raw_score = (
        demand_factor * 0.40 +
        competition_score * 0.35 +
        margin_score * 0.25
    ) * 100

    score = round(min(100.0, max(0.0, raw_score)), 1)

    # Price range for this product
    price_low = round(mid_price * (cogs_factor + ebay_fee_factor + 0.05), 2)
    price_high = round(price_low * 1.4, 2)

    reasoning = (
        f"Demand factor {demand_factor:.2f} (rank #{rank}), "
        f"competition pressure {competition_raw:.2f} (lower=better), "
        f"estimated margin {margin_estimate*100:.1f}% vs target {config['margin_target']*100:.0f}%"
    )

    return {
        "score": score,
        "reasoning": reasoning,
        "estimated_price_range": {"low": price_low, "high": price_high},
        "margin_estimate": round(margin_estimate, 3),
        "competition_raw": round(competition_raw, 3),
        "demand_factor": round(demand_factor, 3),
    }


# ---------------------------------------------------------------------------
# 5. research_product
# ---------------------------------------------------------------------------

def research_product(trend, score_data, config):
    """
    Generate a product research brief for a scored trend.
    Returns dict with all data needed to build a listing.
    """
    name = trend.get("name", "unknown product")
    category = trend.get("category", "General")

    # Generate eBay-friendly keywords
    words = name.lower().replace("-", " ").split()
    stopwords = {"a", "an", "the", "of", "in", "for", "with", "and", "set", "pack"}
    core_words = [w for w in words if w not in stopwords]

    keywords = list(dict.fromkeys(core_words))[:3]  # deduplicated core words
    # Add category-specific power keywords
    category_keywords = {
        "Electronics": ["fast charging", "compatible"],
        "Home & Garden": ["premium quality", "durable"],
        "Sporting Goods": ["professional grade", "workout"],
        "Sports & Outdoors": ["BPA-free", "leak-proof"],
        "Health & Beauty": ["therapeutic", "relief"],
    }
    extra = category_keywords.get(category, ["high quality", "fast shipping"])
    keywords += extra
    keywords = keywords[:5]

    # Supplier notes (placeholder -- real version hooks into Alibaba/AliExpress API)
    supplier_notes = (
        f"Source from Alibaba/AliExpress: search '{name}'. "
        "Compare MOQ, lead time, and unit cost. "
        "Target COGS under 50% of sell price after shipping. "
        "Check supplier reviews (4.5+ stars, 50+ orders). "
        "Order samples before bulk purchase."
    )

    price_range = score_data["estimated_price_range"]

    return {
        "name": name,
        "score": score_data["score"],
        "category": category,
        "estimated_price_range": price_range,
        "margin_estimate": score_data["margin_estimate"],
        "keywords": keywords,
        "supplier_notes": supplier_notes,
        "reasoning": score_data["reasoning"],
        "rank": trend.get("rank", 0),
    }


# ---------------------------------------------------------------------------
# 6. generate_listing
# ---------------------------------------------------------------------------

def generate_listing(brief, config):
    """
    Generate a complete eBay listing draft from a product brief.
    Returns dict ready for JSON export.
    """
    name = brief["name"]
    category = brief["category"]
    keywords = brief["keywords"]
    price_range = brief["estimated_price_range"]

    # Title: max 80 chars, keyword-optimized, title case, no spam
    keyword_str = " ".join(kw.title() for kw in keywords[:2])
    raw_title = f"{name.title()} - {keyword_str}"
    if len(raw_title) > 80:
        raw_title = raw_title[:77] + "..."
    title = raw_title

    # Price: midpoint of estimated range, rounded to .99
    mid = (price_range["low"] + price_range["high"]) / 2
    price = round(mid - 0.01, 2)
    if price < config["price_range"]["min"]:
        price = float(config["price_range"]["min"]) - 0.01
    if price > config["price_range"]["max"]:
        price = float(config["price_range"]["max"]) - 0.01

    # HTML description: professional, 150-200 words
    kw_list_html = "".join(f"<li>{kw.title()}</li>" for kw in keywords)
    description_html = f"""<div style="font-family: Arial, sans-serif; max-width: 680px; color: #333;">
  <h2 style="color: #1a1a1a;">{name.title()}</h2>
  <p>
    Upgrade your everyday routine with this premium <strong>{name}</strong>.
    Designed for quality and convenience, this product delivers reliable performance
    whether you're using it at home, in the office, or on the go.
  </p>
  <h3>Key Features</h3>
  <ul>
    {kw_list_html}
    <li>Durable construction built to last</li>
    <li>Compact and easy to store</li>
  </ul>
  <h3>What's Included</h3>
  <p>
    Everything you need right out of the box. No additional purchases required.
    Arrives securely packaged to ensure it reaches you in perfect condition.
  </p>
  <h3>Why Buy From Us</h3>
  <p>
    We're committed to fast shipping, honest descriptions, and responsive support.
    If you have any questions before or after your purchase, message us anytime.
    Your satisfaction is our priority.
  </p>
  <p style="font-size: 0.85em; color: #666;">
    Ships within 1 business day. Free returns within 30 days.
  </p>
</div>"""

    return {
        "title": title,
        "condition": "New",
        "category": category,
        "price": price,
        "currency": "USD",
        "description_html": description_html,
        "shipping": "Free shipping, ships within 1 business day",
        "returns": "30-day free returns",
        "keywords": keywords,
        "score": brief["score"],
        "margin_estimate": brief["margin_estimate"],
        "source_trend_rank": brief["rank"],
        "generated_at": datetime.now().isoformat(),
        "status": "draft",
        "notes": brief["supplier_notes"],
    }


# ---------------------------------------------------------------------------
# 7. queue_for_review
# ---------------------------------------------------------------------------

def queue_for_review(listings, dry_run=False):
    """
    Write each listing as JSON to ~/.overnight/review/YYYY-MM-DD/listing_N.json.
    In dry_run mode, prints to stdout instead.
    """
    today = datetime.now().strftime("%Y-%m-%d")
    review_today = REVIEW_DIR / today

    saved_paths = []

    for i, listing in enumerate(listings, start=1):
        if dry_run:
            print(f"\n--- DRY RUN: Listing {i} ---")
            print(json.dumps(listing, indent=2))
        else:
            try:
                review_today.mkdir(parents=True, exist_ok=True)
                out_path = review_today / f"listing_{i}.json"
                out_path.write_text(json.dumps(listing, indent=2))
                saved_paths.append(str(out_path))
                log.info("Queued listing %d: %s", i, out_path)
            except Exception as e:
                log.error("Failed to save listing %d: %s", i, e)

    if not dry_run and saved_paths:
        log.info("All listings queued to: %s", review_today)

    return saved_paths


# ---------------------------------------------------------------------------
# 8. write_morning_report
# ---------------------------------------------------------------------------

def write_morning_report(results, report_path=None):
    """
    Write a human-readable morning report to ~/.overnight/morning_report.txt.
    results: dict with keys: trends_analyzed, top_opportunities, listings
    """
    if report_path is None:
        report_path = MORNING_REPORT_PATH

    now = datetime.now()
    next_run = (now + timedelta(days=1)).replace(hour=23, minute=0, second=0, microsecond=0)

    lines = [
        "=" * 60,
        "OVERNIGHT MACHINE -- MORNING REPORT",
        f"Generated: {now.strftime('%A, %B %d %Y at %I:%M %p')}",
        "=" * 60,
        "",
        f"Trends analyzed:     {results.get('trends_analyzed', 0)}",
        f"Opportunities found: {len(results.get('top_opportunities', []))}",
        f"Listings queued:     {len(results.get('listings', []))}",
        "",
        "TOP OPPORTUNITIES",
        "-" * 40,
    ]

    for i, opp in enumerate(results.get("top_opportunities", []), start=1):
        lines.append(
            f"  {i}. {opp['name']} (score: {opp['score']}, "
            f"margin est: {opp['margin_estimate']*100:.1f}%)"
        )

    lines += ["", "LISTING DRAFTS READY FOR REVIEW", "-" * 40]

    for i, listing in enumerate(results.get("listings", []), start=1):
        lines.append(f"  {i}. {listing['title']}")
        lines.append(f"     Price: ${listing['price']} | Score: {listing['score']}")

    today = now.strftime("%Y-%m-%d")
    lines += [
        "",
        "REVIEW YOUR LISTINGS",
        "-" * 40,
        f"  ls ~/.overnight/review/{today}/",
        f"  cat ~/.overnight/review/{today}/listing_1.json",
        "",
        "NEXT RUN",
        "-" * 40,
        f"  Scheduled: {next_run.strftime('%A, %B %d at %I:%M %p')}",
        "  (cron: 0 23 * * * python3 ~/behique/tools/overnight_machine.py)",
        "",
        "=" * 60,
    ]

    report_text = "\n".join(lines)

    try:
        Path(report_path).write_text(report_text)
        log.info("Morning report written: %s", report_path)
    except Exception as e:
        log.error("Failed to write morning report: %s", e)

    return report_text


# ---------------------------------------------------------------------------
# 9. generate_report
# ---------------------------------------------------------------------------

def generate_report():
    """
    Load all snapshots from ~/.overnight/snapshots/ and generate a markdown summary.
    Prints to stdout.
    """
    if not SNAPSHOTS_DIR.exists():
        print("No snapshots directory found. Run the pipeline first.")
        return

    snapshot_files = sorted(SNAPSHOTS_DIR.glob("*.json"))

    if not snapshot_files:
        print("No snapshots found in ~/.overnight/snapshots/. Run the pipeline a few times first.")
        return

    lines = [
        "# Overnight Machine -- Competitive Landscape Report",
        f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
        f"Snapshots analyzed: {len(snapshot_files)}",
        "",
        "## Snapshot History",
        "",
    ]

    all_top = []

    for sf in snapshot_files:
        try:
            data = json.loads(sf.read_text())
            date = data.get("date", sf.stem)
            trends_count = data.get("trends_analyzed", 0)
            top = data.get("top_opportunities", [])
            lines.append(f"### {date}")
            lines.append(f"- Trends analyzed: {trends_count}")
            lines.append(f"- Top opportunities: {len(top)}")
            for opp in top:
                lines.append(
                    f"  - {opp['name']} (score: {opp['score']}, "
                    f"margin: {opp.get('margin_estimate', 0)*100:.1f}%)"
                )
                all_top.append(opp)
            lines.append("")
        except Exception as e:
            lines.append(f"### {sf.name} -- ERROR: {e}")
            lines.append("")

    # Frequency analysis
    if all_top:
        from collections import Counter
        name_counts = Counter(opp["name"] for opp in all_top)
        lines += [
            "## Recurring Opportunities (appeared in multiple runs)",
            "",
        ]
        for name, count in name_counts.most_common(10):
            if count > 1:
                avg_score = sum(
                    o["score"] for o in all_top if o["name"] == name
                ) / count
                lines.append(f"- **{name}** -- appeared {count}x, avg score {avg_score:.1f}")
        lines.append("")

    report = "\n".join(lines)
    print(report)

    # Also save to snapshots dir
    report_path = SNAPSHOTS_DIR / f"landscape_report_{datetime.now().strftime('%Y%m%d')}.md"
    try:
        report_path.write_text(report)
        print(f"\nReport saved to: {report_path}")
    except Exception as e:
        log.error("Could not save report: %s", e)


# ---------------------------------------------------------------------------
# 10. main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Overnight Machine -- Behike eBay Product Discovery Pipeline"
    )
    parser.add_argument("--test",    action="store_true", help="Run with dummy trend data")
    parser.add_argument("--dry-run", action="store_true", dest="dry_run",
                        help="Run without saving listings to disk")
    parser.add_argument("--setup",   action="store_true", help="Create ~/.overnight/ directory structure")
    parser.add_argument("--report",  action="store_true", help="Generate competitive landscape report")
    args = parser.parse_args()

    # --setup
    if args.setup:
        setup_directories()
        return

    # --report
    if args.report:
        generate_report()
        return

    # Full pipeline
    start_time = datetime.now()
    log.info("=" * 50)
    log.info("Overnight Machine starting at %s", start_time.strftime("%Y-%m-%d %H:%M:%S"))
    if args.test:
        log.info("Mode: TEST (dummy data)")
    if args.dry_run:
        log.info("Mode: DRY RUN (no files saved)")
    log.info("=" * 50)

    # Ensure directories exist silently
    try:
        for d in [OVERNIGHT_DIR, LOGS_DIR, REVIEW_DIR, SNAPSHOTS_DIR]:
            d.mkdir(parents=True, exist_ok=True)
    except Exception as e:
        log.error("Could not create directories: %s", e)

    # Stage 1: Load config
    config = {}
    try:
        config = load_config()
        log.info(
            "Config loaded. Target margin: %.0f%%, min score: %s, max listings: %s",
            config["margin_target"] * 100,
            config["min_score"],
            config["max_listings"],
        )
    except Exception as e:
        log.error("Config load failed: %s. Using defaults.", e)
        config = load_config()  # will return defaults

    # Stage 2: Load trends
    trends = []
    try:
        trends = load_trends(test_mode=args.test)
        if not trends:
            log.warning("No trends loaded. Exiting.")
            return
    except Exception as e:
        log.error("Trend load failed: %s", e)
        return

    log.info("Loaded %d trends. Scoring opportunities...", len(trends))

    # Stage 3: Score all trends
    scored = []
    for trend in trends:
        try:
            score_data = score_opportunity(trend, config)
            scored.append({"trend": trend, "score_data": score_data})
        except Exception as e:
            log.error("Scoring failed for '%s': %s", trend.get("name", "?"), e)

    # Filter and sort by score
    qualified = [
        s for s in scored
        if s["score_data"]["score"] >= config["min_score"]
    ]
    qualified.sort(key=lambda x: x["score_data"]["score"], reverse=True)
    top_n = qualified[:config["max_listings"]]

    log.info(
        "Scored %d trends. %d qualified (score >= %s). Taking top %d.",
        len(scored), len(qualified), config["min_score"], len(top_n)
    )

    if not top_n:
        log.warning(
            "No trends met the minimum score of %s. "
            "Try lowering min_score in config, or check your trends data.",
            config["min_score"]
        )
        # In test mode, just take the top 5 regardless
        if args.test:
            log.info("Test mode: taking top 5 regardless of score threshold.")
            all_sorted = sorted(scored, key=lambda x: x["score_data"]["score"], reverse=True)
            top_n = all_sorted[:config["max_listings"]]
        else:
            return

    # Stage 4: Research each
    briefs = []
    for item in top_n:
        try:
            brief = research_product(item["trend"], item["score_data"], config)
            briefs.append(brief)
            log.info(
                "Research brief: '%s' (score: %.1f, margin est: %.1f%%)",
                brief["name"], brief["score"], brief["margin_estimate"] * 100
            )
        except Exception as e:
            log.error("Research failed for '%s': %s", item["trend"].get("name", "?"), e)

    # Stage 5: Generate listings
    listings = []
    for brief in briefs:
        try:
            listing = generate_listing(brief, config)
            listings.append(listing)
            log.info("Listing generated: '%s' at $%.2f", listing["title"], listing["price"])
        except Exception as e:
            log.error("Listing generation failed for '%s': %s", brief.get("name", "?"), e)

    # Stage 6: Queue for review
    saved_paths = []
    try:
        saved_paths = queue_for_review(listings, dry_run=args.dry_run)
    except Exception as e:
        log.error("Queue for review failed: %s", e)

    # Stage 7: Write morning report
    results = {
        "date": start_time.strftime("%Y-%m-%d"),
        "trends_analyzed": len(trends),
        "top_opportunities": [
            {
                "name": b["name"],
                "score": b["score"],
                "margin_estimate": b["margin_estimate"],
                "category": b["category"],
            }
            for b in briefs
        ],
        "listings": listings,
    }

    try:
        if not args.dry_run:
            write_morning_report(results)
        else:
            log.info("Dry run: skipping morning report file write.")
    except Exception as e:
        log.error("Morning report failed: %s", e)

    # Stage 8: Save snapshot
    if not args.dry_run:
        try:
            snapshot_path = SNAPSHOTS_DIR / f"snapshot_{start_time.strftime('%Y%m%d_%H%M%S')}.json"
            snapshot_path.write_text(json.dumps(results, indent=2))
            log.info("Snapshot saved: %s", snapshot_path)
        except Exception as e:
            log.error("Snapshot save failed: %s", e)

    # Done
    end_time = datetime.now()
    elapsed = (end_time - start_time).total_seconds()
    log.info("=" * 50)
    log.info(
        "Overnight Machine complete in %.2fs. %d listings queued.",
        elapsed, len(listings)
    )
    if saved_paths:
        log.info("Review folder: %s", REVIEW_DIR / start_time.strftime("%Y-%m-%d"))
    if not args.dry_run:
        log.info("Morning report: cat ~/.overnight/morning_report.txt")
    log.info("=" * 50)


if __name__ == "__main__":
    main()

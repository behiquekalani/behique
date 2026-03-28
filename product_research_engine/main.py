"""
Product Research Engine — CLI Entry Point.

Usage:
    python main.py --discover                    # Run source scrapers
    python main.py --cross-reference             # eBay + trends lookup
    python main.py --score                       # Re-score without re-scraping
    python main.py --full-pipeline               # discover -> cross-ref -> score -> report
    python main.py --report                      # Generate reports from existing scores
    python main.py --status                      # Show DB stats
    python main.py --sources amazon,walmart      # Only specific sources
    python main.py --category electronics        # Filter by category
"""

import os
import sys
import argparse
import logging
import yaml

# Add parent dir to path so we can import from core/, scrapers/, etc.
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core.database import Database
from pipeline.discovery import DiscoveryPipeline
from pipeline.cross_reference import CrossReferencePipeline
from pipeline.scoring import ScoringPipeline
from pipeline.reporting import ReportingPipeline
from core.utils import ProxyManager


def load_config():
    config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.yaml")
    with open(config_path) as f:
        return yaml.safe_load(f)


def show_status(config):
    db = Database(config["database"]["path"])
    tables = ["products", "ebay_market_data", "trend_data", "features", "scores"]

    print("\n  PRODUCT RESEARCH ENGINE -- STATUS")
    print("  " + "=" * 45)

    for t in tables:
        count = db.count_rows(t)
        print(f"  {t:<25} {count:>6} rows")

    last_discovery = db.last_run("products", "discovered_at")
    last_score = db.last_run("scores", "scored_at")
    print(f"\n  Last discovery:  {last_discovery or 'never'}")
    print(f"  Last scoring:    {last_score or 'never'}")

    # Proxy count
    proxy_mgr = ProxyManager(config["proxy"]["path"])
    print(f"  Proxies loaded:  {proxy_mgr.count}")

    # Cache age
    cache_path = config["database"]["path"]
    if os.path.exists(cache_path):
        import time
        age_hours = (time.time() - os.path.getmtime(cache_path)) / 3600
        print(f"  Cache age:       {age_hours:.1f} hours")

    print()


def main():
    parser = argparse.ArgumentParser(
        description="Cross-Platform Product Research Engine for eBay Dropshipping"
    )
    parser.add_argument("--discover", action="store_true", help="Run source scrapers")
    parser.add_argument("--cross-reference", action="store_true", help="eBay + trends lookup")
    parser.add_argument("--score", action="store_true", help="Re-score without re-scraping")
    parser.add_argument("--full-pipeline", action="store_true", help="Full: discover -> cross-ref -> score -> report")
    parser.add_argument("--report", action="store_true", help="Generate reports from existing scores")
    parser.add_argument("--status", action="store_true", help="Show database stats")
    parser.add_argument("--sources", type=str, help="Comma-separated sources: amazon,walmart")
    parser.add_argument("--category", type=str, help="Filter by category")
    args = parser.parse_args()

    config = load_config()

    # Set up logging
    log_level = config.get("logging", {}).get("level", "INFO")
    logging.basicConfig(
        level=getattr(logging, log_level),
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler(
                os.path.join(os.path.dirname(os.path.abspath(__file__)), "output", "engine.log"),
                encoding="utf-8"
            ),
        ],
    )

    sources = args.sources.split(",") if args.sources else None

    if args.status:
        show_status(config)
        return

    if args.full_pipeline:
        # Run everything
        dp = DiscoveryPipeline(config)
        dp.run(sources=sources, category=args.category)

        cr = CrossReferencePipeline(config)
        cr.run()

        sp = ScoringPipeline(config)
        sp.run()

        rp = ReportingPipeline(config)
        rp.generate()
        return

    if args.discover:
        dp = DiscoveryPipeline(config)
        dp.run(sources=sources, category=args.category)

    if args.cross_reference:
        cr = CrossReferencePipeline(config)
        cr.run()

    if args.score:
        sp = ScoringPipeline(config)
        sp.run()

    if args.report:
        rp = ReportingPipeline(config)
        rp.generate()


if __name__ == "__main__":
    main()

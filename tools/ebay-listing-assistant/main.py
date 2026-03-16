"""
eBay Listing Assistant — CLI entry point.

Usage:
  python main.py "Sony WH-1000XM4 Headphones" --condition Used --dry-run
  python main.py "Nintendo Switch Pro Controller" --provider ollama
  python main.py --history
  python main.py --stats
"""

import argparse
import json
import logging
import sys

from core.types import ProductInput
from core.pipeline import ListingPipeline
from providers.ebay.auth import EbayAuth
from providers.ebay.research import EbayResearchAdapter
from providers.ebay.publisher import EbayPublisher
from ai.content_generator import ContentGenerator
from storage.history import ListingHistory

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger(__name__)


def build_pipeline(args) -> ListingPipeline:
    """Wire up all adapters and return a ready pipeline."""
    auth = EbayAuth(sandbox=args.sandbox)
    research = EbayResearchAdapter(auth)
    content = ContentGenerator(provider=args.provider, model=args.model)
    publisher = EbayPublisher(auth)

    return ListingPipeline(research, content, publisher)


def run_listing(args):
    """Run the full listing pipeline for a product."""
    pipeline = build_pipeline(args)
    history = ListingHistory()

    product = ProductInput(
        name=args.product,
        condition=args.condition,
        category_hint=args.category,
        notes=args.notes,
    )

    logger.info(f"Starting pipeline for: {product.name}")
    result = pipeline.run(product, dry_run=args.dry_run)

    # Log to history
    history.log_attempt(product.name, result)

    # Output
    if result["errors"]:
        logger.warning(f"Errors: {json.dumps(result['errors'], indent=2)}")

    if result["content"]:
        content = result["content"]
        print(f"\n--- Generated Listing ---")
        print(f"Title: {content.title}")
        print(f"Price: ${content.suggested_price:.2f}")
        print(f"Condition: {content.suggested_condition}")
        print(f"Keywords: {', '.join(content.keywords)}")
        print(f"\nDescription:\n{content.description[:500]}...")
        print(f"\nItem Specifics:")
        for k, v in content.item_specifics.items():
            print(f"  {k}: {v}")

    if result["published"]:
        pub = result["published"]
        if isinstance(pub, dict) and pub.get("dry_run"):
            print(f"\n[DRY RUN] Would publish: {pub['title']} @ ${pub['price']:.2f}")
        else:
            print(f"\nLIVE: {pub.listing_url}")

    return 0 if not result["errors"] else 1


def show_history(args):
    """Show recent listing attempts."""
    history = ListingHistory()
    recent = history.get_recent(limit=args.limit)

    if not recent:
        print("No listing history yet.")
        return

    for entry in recent:
        status = entry["status"]
        icon = {"active": "+", "dry_run": "~", "failed": "x"}.get(status, "?")
        print(f"  [{icon}] {entry['product_name']} | {entry['title'] or 'N/A'} | "
              f"${entry['price'] or 0:.2f} | {entry['created_at']}")


def show_stats():
    """Show listing stats."""
    history = ListingHistory()
    s = history.stats()
    print(f"Total attempts: {s['total_attempts']}")
    print(f"Active listings: {s['active_listings']}")
    print(f"Failed: {s['failed']}")
    print(f"Dry runs: {s['dry_runs']}")


def main():
    parser = argparse.ArgumentParser(description="eBay Listing Assistant")
    sub = parser.add_subparsers(dest="command")

    # list command
    list_cmd = sub.add_parser("list", help="Create a listing")
    list_cmd.add_argument("product", help="Product name/description")
    list_cmd.add_argument("--condition", default="Used", choices=["New", "Used", "Refurbished", "For Parts"])
    list_cmd.add_argument("--category", default=None, help="eBay category ID hint")
    list_cmd.add_argument("--notes", default=None, help="Extra notes for the LLM")
    list_cmd.add_argument("--provider", default="claude", choices=["claude", "ollama"])
    list_cmd.add_argument("--model", default=None, help="Override LLM model")
    list_cmd.add_argument("--sandbox", action="store_true", default=True, help="Use eBay sandbox (default)")
    list_cmd.add_argument("--production", action="store_true", help="Use production eBay")
    list_cmd.add_argument("--dry-run", action="store_true", help="Skip publishing step")

    # history command
    hist_cmd = sub.add_parser("history", help="Show listing history")
    hist_cmd.add_argument("--limit", type=int, default=20)

    # stats command
    sub.add_parser("stats", help="Show listing stats")

    args = parser.parse_args()

    if args.command == "list":
        if args.production:
            args.sandbox = False
        sys.exit(run_listing(args))
    elif args.command == "history":
        show_history(args)
    elif args.command == "stats":
        show_stats()
    else:
        parser.print_help()


if __name__ == "__main__":
    main()

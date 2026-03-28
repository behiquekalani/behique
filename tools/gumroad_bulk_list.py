#!/usr/bin/env python3
"""
Gumroad Bulk Product Lister
Reads READY-TO-SELL/GUMROAD_UPLOAD_MANIFEST.md, creates listings via Gumroad API.

Usage:
    python3 tools/gumroad_bulk_list.py --list
    python3 tools/gumroad_bulk_list.py --dry-run
    python3 tools/gumroad_bulk_list.py --create-one "Blueprint AI Agency"
    python3 tools/gumroad_bulk_list.py --create-all

Setup:
    1. Go to https://gumroad.com/settings/advanced
    2. Create application > Generate access token
    3. Either:
       - export GUMROAD_ACCESS_TOKEN=your_token
       - or put GUMROAD_ACCESS_TOKEN=your_token in ~/.env.gumroad

Dependencies: requests (pip install requests)
"""

import argparse
import json
import logging
import os
import re
import sys
import time
from datetime import datetime
from pathlib import Path

try:
    import requests
except ImportError:
    print("ERROR: 'requests' is required. Install with: pip install requests")
    sys.exit(1)

# --- Paths ---
ROOT = Path(__file__).resolve().parent.parent
MANIFEST_PATH = ROOT / "READY-TO-SELL" / "GUMROAD_UPLOAD_MANIFEST.md"
READY_DIR = ROOT / "READY-TO-SELL"
LOG_DIR = ROOT / "bios" / "logs"
LOG_PATH = LOG_DIR / "gumroad_listing.log"

# --- API ---
API_BASE = "https://api.gumroad.com/v2"
RATE_LIMIT_DELAY = 1.5  # seconds between requests (~40 req/min, safe under 50)


# --- Logging ---

def setup_logging():
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        handlers=[
            logging.FileHandler(LOG_PATH, encoding="utf-8"),
            logging.StreamHandler(sys.stdout),
        ],
    )
    return logging.getLogger("gumroad")


log = setup_logging()


# --- Token ---

def load_token():
    """Load Gumroad access token from env or ~/.env.gumroad."""
    token = os.environ.get("GUMROAD_ACCESS_TOKEN")
    if token:
        return token.strip()

    env_file = Path.home() / ".env.gumroad"
    if env_file.exists():
        for line in env_file.read_text().splitlines():
            line = line.strip()
            if line.startswith("#") or "=" not in line:
                continue
            key, val = line.split("=", 1)
            if key.strip() == "GUMROAD_ACCESS_TOKEN":
                return val.strip()

    return None


# --- Manifest Parser ---

def parse_manifest(path):
    """Parse GUMROAD_UPLOAD_MANIFEST.md into a list of product dicts."""
    if not path.exists():
        log.error("Manifest not found at %s", path)
        log.error("Run: python3 tools/gumroad_uploader.py  (to generate it)")
        sys.exit(1)

    text = path.read_text(encoding="utf-8")
    products = []

    # Split on ### headers
    blocks = re.split(r"^### \d+\.\s+", text, flags=re.MULTILINE)

    for block in blocks[1:]:  # skip preamble
        lines = block.strip().splitlines()
        if not lines:
            continue

        title = lines[0].strip()
        product = {
            "title": title,
            "price": 0,
            "category": "",
            "files": [],
            "size_kb": 0,
            "tags": [],
            "description": "",
        }

        for line in lines[1:]:
            line = line.strip()
            if line.startswith("- **Price:**"):
                match = re.search(r"\$([0-9.]+)", line)
                if match:
                    product["price"] = float(match.group(1))
            elif line.startswith("- **Category:**"):
                product["category"] = line.split(":", 1)[1].strip().strip("*")
            elif line.startswith("- **File(s):**"):
                raw = line.split(":", 1)[1].strip().strip("*")
                product["files"] = [f.strip() for f in raw.split(",")]
            elif line.startswith("- **Size:**"):
                match = re.search(r"([\d.]+)", line)
                if match:
                    product["size_kb"] = float(match.group(1))
            elif line.startswith("- **Tags:**"):
                raw = line.split(":", 1)[1].strip().strip("*")
                product["tags"] = [t.strip() for t in raw.split(",")]
            elif line.startswith("- **Description:**"):
                # description is on the next line(s)
                pass
            elif line and not line.startswith("- **"):
                # continuation of description
                product["description"] += (" " if product["description"] else "") + line

        products.append(product)

    return products


# --- Gumroad API ---

class GumroadClient:
    def __init__(self, token):
        self.token = token
        self.session = requests.Session()
        self.session.headers.update({"Authorization": f"Bearer {token}"})
        self._last_request = 0

    def _throttle(self):
        """Respect rate limits."""
        elapsed = time.time() - self._last_request
        if elapsed < RATE_LIMIT_DELAY:
            time.sleep(RATE_LIMIT_DELAY - elapsed)
        self._last_request = time.time()

    def get_existing_products(self):
        """Fetch all existing products, return dict of name -> product."""
        self._throttle()
        resp = self.session.get(f"{API_BASE}/products", params={"access_token": self.token})
        resp.raise_for_status()
        data = resp.json()

        if not data.get("success"):
            log.error("Failed to fetch products: %s", data.get("message", "unknown"))
            return {}

        products = {}
        for p in data.get("products", []):
            products[p["name"]] = p
        return products

    def create_product(self, product, dry_run=False):
        """Create a single product on Gumroad. Returns API response dict or None."""
        name = product["title"]
        price_cents = int(product["price"] * 100)

        # Build form data
        form = {
            "access_token": self.token,
            "name": name,
            "price": price_cents,
            "description": product["description"],
        }

        # Add tags (Gumroad accepts tags[] as repeated field)
        tags = product.get("tags", [])

        if dry_run:
            file_names = ", ".join(product["files"])
            log.info("[DRY RUN] Would create: %s ($%.2f) files=[%s] tags=%s",
                     name, product["price"], file_names, tags)
            return {"dry_run": True, "name": name}

        # Find and open files for upload
        file_handles = []
        files_multipart = []
        try:
            for fname in product["files"]:
                fpath = READY_DIR / fname
                if not fpath.exists():
                    log.warning("File not found, skipping: %s", fpath)
                    continue
                fh = open(fpath, "rb")
                file_handles.append(fh)
                files_multipart.append(("file", (fname, fh, "application/octet-stream")))

            # Add tags as repeated form fields
            tag_tuples = [("tags[]", t) for t in tags]

            self._throttle()

            if files_multipart:
                # multipart upload: form fields + files
                form_tuples = list(form.items()) + tag_tuples
                resp = self.session.post(
                    f"{API_BASE}/products",
                    data=form_tuples,
                    files=files_multipart,
                )
            else:
                form_tuples = list(form.items()) + tag_tuples
                resp = self.session.post(f"{API_BASE}/products", data=form_tuples)

        finally:
            for fh in file_handles:
                fh.close()

        if resp.status_code == 429:
            log.warning("Rate limited. Waiting 60s before retry...")
            time.sleep(60)
            return self.create_product(product, dry_run=False)

        try:
            data = resp.json()
        except Exception:
            log.error("Non-JSON response (%d): %s", resp.status_code, resp.text[:500])
            return None

        if not data.get("success"):
            log.error("Failed to create '%s': %s", name, data.get("message", resp.text[:300]))
            return None

        gumroad_product = data.get("product", {})
        log.info("Created: %s -> %s (id: %s)",
                 name,
                 gumroad_product.get("short_url", "?"),
                 gumroad_product.get("id", "?"))
        return data


# --- CLI Commands ---

def cmd_list(products):
    """Show all products from the manifest."""
    print(f"\n{'#':>3}  {'Price':>7}  {'Category':<18}  {'Title'}")
    print("-" * 80)
    for i, p in enumerate(products, 1):
        price_str = f"${p['price']:.2f}" if p["price"] > 0 else "FREE"
        print(f"{i:>3}  {price_str:>7}  {p['category']:<18}  {p['title']}")
    print(f"\nTotal: {len(products)} products, catalog value: ${sum(p['price'] for p in products):,.2f}")


def cmd_create_one(client, products, name, dry_run=False):
    """Create a single product by name."""
    # Find the product
    match = None
    name_lower = name.lower()
    for p in products:
        if p["title"].lower() == name_lower:
            match = p
            break
    if not match:
        # Try partial match
        for p in products:
            if name_lower in p["title"].lower():
                match = p
                break

    if not match:
        log.error("Product not found: '%s'", name)
        log.info("Use --list to see available products.")
        sys.exit(1)

    # Check if already exists
    if not dry_run:
        existing = client.get_existing_products()
        if match["title"] in existing:
            log.info("SKIP (already exists): %s -> %s",
                     match["title"], existing[match["title"]].get("short_url", "?"))
            return

    result = client.create_product(match, dry_run=dry_run)
    if result:
        log.info("Done.")


def cmd_create_all(client, products, dry_run=False):
    """Create all products, skipping existing ones."""
    existing = {}
    if not dry_run:
        log.info("Fetching existing products...")
        existing = client.get_existing_products()
        log.info("Found %d existing products on Gumroad.", len(existing))

    created = 0
    skipped = 0
    failed = 0

    for i, p in enumerate(products, 1):
        prefix = f"[{i}/{len(products)}]"

        if p["title"] in existing:
            log.info("%s SKIP (exists): %s", prefix, p["title"])
            skipped += 1
            continue

        result = client.create_product(p, dry_run=dry_run)
        if result:
            created += 1
        else:
            failed += 1

    log.info("")
    log.info("=== RESULTS ===")
    log.info("Created: %d", created)
    log.info("Skipped (existing): %d", skipped)
    log.info("Failed: %d", failed)
    log.info("Total: %d", len(products))


# --- Main ---

def main():
    parser = argparse.ArgumentParser(
        description="Bulk-list products on Gumroad from the upload manifest.",
        epilog=(
            "Setup:\n"
            "  1. Go to https://gumroad.com/settings/advanced\n"
            "  2. Create application, then generate access token\n"
            "  3. export GUMROAD_ACCESS_TOKEN=your_token\n"
            "     (or save to ~/.env.gumroad)\n"
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--list", action="store_true", help="Show all products from manifest")
    group.add_argument("--create-one", metavar="NAME", help="Create a single product by name")
    group.add_argument("--create-all", action="store_true", help="Create all products")
    parser.add_argument("--dry-run", action="store_true", help="Show what would happen without doing it")
    parser.add_argument("--manifest", type=str, default=None, help="Path to manifest file (default: READY-TO-SELL/GUMROAD_UPLOAD_MANIFEST.md)")

    args = parser.parse_args()

    manifest = Path(args.manifest) if args.manifest else MANIFEST_PATH
    products = parse_manifest(manifest)
    log.info("Loaded %d products from manifest.", len(products))

    if args.list:
        cmd_list(products)
        return

    # For create commands, we need a token (unless dry-run)
    token = load_token()
    if not token and not args.dry_run:
        log.error("No Gumroad access token found.")
        log.error("Set GUMROAD_ACCESS_TOKEN env var or create ~/.env.gumroad")
        log.error("See: .env.gumroad.template for instructions")
        sys.exit(1)

    client = GumroadClient(token or "dry-run-no-token")

    if args.create_one:
        cmd_create_one(client, products, args.create_one, dry_run=args.dry_run)
    elif args.create_all:
        cmd_create_all(client, products, dry_run=args.dry_run)


if __name__ == "__main__":
    main()

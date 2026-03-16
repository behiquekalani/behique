"""
Listing history — tracks every listing attempt and result.
SQLite-backed, lives alongside the tool.
"""

import logging
import os
import sqlite3
from datetime import datetime

from core.types import PublishedListing

logger = logging.getLogger(__name__)

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "cache", "listings.db")


class ListingHistory:
    """Tracks all listing attempts — successes, failures, dry runs."""

    def __init__(self, db_path: str = None):
        self.db_path = db_path or DB_PATH
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        self._init_db()

    def _init_db(self):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS listings (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    product_name TEXT NOT NULL,
                    platform TEXT,
                    listing_id TEXT,
                    listing_url TEXT,
                    title TEXT,
                    price REAL,
                    status TEXT DEFAULT 'pending',
                    dry_run INTEGER DEFAULT 0,
                    errors TEXT,
                    created_at TEXT DEFAULT (datetime('now')),
                    updated_at TEXT DEFAULT (datetime('now'))
                )
            """)

    def log_attempt(self, product_name: str, result: dict):
        """Log a pipeline run result."""
        published = result.get("published")
        errors = result.get("errors", [])

        is_dry_run = isinstance(published, dict) and published.get("dry_run")

        with sqlite3.connect(self.db_path) as conn:
            if published and not is_dry_run:
                conn.execute(
                    """INSERT INTO listings
                       (product_name, platform, listing_id, listing_url, title, price, status, dry_run, errors)
                       VALUES (?, ?, ?, ?, ?, ?, ?, 0, ?)""",
                    (
                        product_name,
                        published.platform if isinstance(published, PublishedListing) else "unknown",
                        published.listing_id if isinstance(published, PublishedListing) else "",
                        published.listing_url if isinstance(published, PublishedListing) else "",
                        published.title if isinstance(published, PublishedListing) else published.get("title", ""),
                        published.price if isinstance(published, PublishedListing) else published.get("price", 0),
                        "active",
                        str(errors) if errors else None,
                    ),
                )
            elif is_dry_run:
                conn.execute(
                    """INSERT INTO listings
                       (product_name, title, price, status, dry_run, errors)
                       VALUES (?, ?, ?, 'dry_run', 1, ?)""",
                    (
                        product_name,
                        published.get("title", ""),
                        published.get("price", 0),
                        str(errors) if errors else None,
                    ),
                )
            else:
                conn.execute(
                    """INSERT INTO listings
                       (product_name, status, errors)
                       VALUES (?, 'failed', ?)""",
                    (product_name, str(errors)),
                )

    def get_recent(self, limit: int = 20) -> list[dict]:
        """Get recent listing attempts."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            rows = conn.execute(
                "SELECT * FROM listings ORDER BY created_at DESC LIMIT ?",
                (limit,),
            ).fetchall()
            return [dict(r) for r in rows]

    def stats(self) -> dict:
        """Get listing stats summary."""
        with sqlite3.connect(self.db_path) as conn:
            total = conn.execute("SELECT COUNT(*) FROM listings").fetchone()[0]
            active = conn.execute("SELECT COUNT(*) FROM listings WHERE status='active'").fetchone()[0]
            failed = conn.execute("SELECT COUNT(*) FROM listings WHERE status='failed'").fetchone()[0]
            dry_runs = conn.execute("SELECT COUNT(*) FROM listings WHERE dry_run=1").fetchone()[0]
            return {
                "total_attempts": total,
                "active_listings": active,
                "failed": failed,
                "dry_runs": dry_runs,
            }

"""
Imports trend data from the existing Google Trends scraper at ~/behique/tools/trends_scraper.py.
Reads directly from the SQLite cache (trends_cache.db) to avoid re-scraping.
Falls back to neutral scores if no data is available.
"""

import os
import sys
import json
import sqlite3
import logging
import time

logger = logging.getLogger(__name__)

# The trends scraper cache DB
DEFAULT_CACHE_PATH = os.path.expanduser("~/behique/cache/trends_cache.db")


class TrendsAdapter:

    def __init__(self, config=None):
        cache_path = DEFAULT_CACHE_PATH
        if config and "trends" in config:
            alt = config["trends"].get("cache_db")
            if alt:
                expanded = os.path.expanduser(alt)
                if os.path.exists(expanded):
                    cache_path = expanded

        self.cache_path = cache_path
        self.conn = None

        if os.path.exists(cache_path):
            try:
                self.conn = sqlite3.connect(cache_path)
                self.conn.row_factory = sqlite3.Row
                logger.info(f"Trends cache connected: {cache_path}")
            except Exception as e:
                logger.warning(f"Could not connect to trends cache: {e}")
        else:
            logger.warning(f"Trends cache not found at {cache_path} -- using neutral scores")

    def get_trend_signal(self, keyword):
        """
        Look up a keyword in the trends cache.
        Returns dict with trend_velocity, trend_classification, trend_score.
        Falls back to neutral if no data.
        """
        if not self.conn:
            return self._neutral()

        try:
            c = self.conn.cursor()

            # Check for 3-month data first (most useful for velocity)
            c.execute("""
                SELECT data, fetched_at FROM trends_cache
                WHERE keyword=? AND timeframe='today 3-m'
                ORDER BY fetched_at DESC LIMIT 1
            """, (keyword,))
            row_3m = c.fetchone()

            c.execute("""
                SELECT data, fetched_at FROM trends_cache
                WHERE keyword=? AND timeframe='today 1-m'
                ORDER BY fetched_at DESC LIMIT 1
            """, (keyword,))
            row_1m = c.fetchone()

            c.execute("""
                SELECT data, fetched_at FROM trends_cache
                WHERE keyword=? AND timeframe='now 7-d'
                ORDER BY fetched_at DESC LIMIT 1
            """, (keyword,))
            row_7d = c.fetchone()

            if not row_3m and not row_1m:
                return self._neutral()

            # Parse cached data
            data_3m = json.loads(row_3m["data"]) if row_3m else {"mean": 0, "values": []}
            data_1m = json.loads(row_1m["data"]) if row_1m else {"mean": 0, "values": []}
            data_7d = json.loads(row_7d["data"]) if row_7d else {"mean": 0, "values": []}

            # Compute velocity
            velocity = self._compute_velocity(data_3m, data_1m)

            # Classify
            classification = self._classify(data_7d, data_1m, data_3m)

            # Score (normalized 0-1)
            trend_score = min(velocity / 3.0, 1.0)  # velocity of 3x = max score

            return {
                "trend_velocity": round(velocity, 3),
                "trend_classification": classification,
                "trend_score": round(trend_score, 3),
            }

        except Exception as e:
            logger.warning(f"Trend lookup failed for '{keyword}': {e}")
            return self._neutral()

    def _compute_velocity(self, data_3m, data_1m):
        values = data_3m.get("values", [])
        if len(values) >= 10:
            mid = len(values) // 2
            first_half = sum(values[:mid]) / max(mid, 1)
            second_half = sum(values[mid:]) / max(len(values) - mid, 1)
            if first_half > 0:
                return second_half / first_half
        # Fallback to 1m mean vs 3m mean
        m1 = data_1m.get("mean", 0)
        m3 = data_3m.get("mean", 0)
        if m3 > 0:
            return m1 / m3
        return 1.0

    def _classify(self, data_7d, data_1m, data_3m):
        d7_mean = data_7d.get("mean", 0)
        m1_mean = data_1m.get("mean", 0)
        m3_mean = data_3m.get("mean", 0)
        m3_std = data_3m.get("std", 0)

        if m1_mean > 0 and d7_mean > 2 * m1_mean:
            return "spike"

        values = data_3m.get("values", [])
        if len(values) >= 10:
            mid = len(values) // 2
            first_half = sum(values[:mid]) / max(mid, 1)
            second_half = sum(values[mid:]) / max(len(values) - mid, 1)
            if second_half > first_half * 1.2:
                return "emerging"

        if m3_mean > 0 and m3_std / m3_mean > 0.5:
            return "seasonal"

        return "stable"

    def _neutral(self):
        return {
            "trend_velocity": 0.5,
            "trend_classification": "stable",
            "trend_score": 0.5,
        }

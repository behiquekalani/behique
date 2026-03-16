"""
SQLite database — stores signals separately for instant re-scoring.
Tables: products, ebay_market_data, trend_data, features, scores
"""

import sqlite3
import logging
from pathlib import Path
from datetime import datetime

logger = logging.getLogger(__name__)


class Database:

    def __init__(self, db_path: str):
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)
        self.conn = sqlite3.connect(db_path)
        self.conn.row_factory = sqlite3.Row
        self.init_schema()

    def init_schema(self):
        c = self.conn.cursor()

        c.execute("""
        CREATE TABLE IF NOT EXISTS products(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            normalized_name TEXT,
            category TEXT,
            source TEXT,
            source_price REAL,
            source_url TEXT,
            rank INTEGER,
            discovered_at TEXT,
            UNIQUE(normalized_name, source)
        )""")

        c.execute("""
        CREATE TABLE IF NOT EXISTS ebay_market_data(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_id INTEGER REFERENCES products(id),
            avg_price REAL,
            units_sold_90d INTEGER,
            active_listings INTEGER,
            sell_through REAL,
            last_sale_days INTEGER,
            fetched_at TEXT
        )""")

        c.execute("""
        CREATE TABLE IF NOT EXISTS trend_data(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_id INTEGER REFERENCES products(id),
            trend_velocity REAL,
            trend_classification TEXT,
            trend_score REAL,
            fetched_at TEXT
        )""")

        c.execute("""
        CREATE TABLE IF NOT EXISTS features(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_id INTEGER REFERENCES products(id),
            margin REAL,
            sales_velocity REAL,
            competition_ratio REAL,
            saturation REAL,
            price_score REAL,
            keyword_score REAL,
            computed_at TEXT
        )""")

        c.execute("""
        CREATE TABLE IF NOT EXISTS scores(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_id INTEGER REFERENCES products(id),
            demand_score REAL,
            margin_score REAL,
            competition_score REAL,
            recency_score REAL,
            quality_score REAL,
            final_score REAL,
            scored_at TEXT
        )""")

        self.conn.commit()
        logger.info("Database schema initialized")

    def upsert_product(self, product):
        c = self.conn.cursor()
        c.execute("""
        INSERT INTO products
        (name, normalized_name, category, source, source_price, source_url, rank, discovered_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(normalized_name, source)
        DO UPDATE SET
            name=excluded.name,
            source_price=excluded.source_price,
            source_url=excluded.source_url,
            rank=excluded.rank,
            discovered_at=excluded.discovered_at
        """, (
            product.name,
            product.normalized_name,
            product.category,
            product.source,
            product.source_price,
            product.source_url,
            product.rank,
            product.discovered_at.isoformat()
        ))
        self.conn.commit()
        return c.lastrowid

    def upsert_ebay_data(self, data):
        c = self.conn.cursor()
        c.execute("""
        INSERT INTO ebay_market_data
        (product_id, avg_price, units_sold_90d, active_listings, sell_through, last_sale_days, fetched_at)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            data.product_id, data.avg_price, data.units_sold_90d,
            data.active_listings, data.sell_through, data.last_sale_days,
            data.fetched_at.isoformat()
        ))
        self.conn.commit()

    def upsert_trend_data(self, data):
        c = self.conn.cursor()
        c.execute("""
        INSERT INTO trend_data
        (product_id, trend_velocity, trend_classification, trend_score, fetched_at)
        VALUES (?, ?, ?, ?, ?)
        """, (
            data.product_id, data.trend_velocity,
            data.trend_classification, data.trend_score,
            data.fetched_at.isoformat()
        ))
        self.conn.commit()

    def save_features(self, product_id, features):
        c = self.conn.cursor()
        c.execute("""
        INSERT INTO features
        (product_id, margin, sales_velocity, competition_ratio, saturation, price_score, keyword_score, computed_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            product_id,
            features["margin"],
            features["sales_velocity"],
            features.get("competition_ratio", 0),
            features.get("saturation", 0),
            features["price_score"],
            features["keyword_score"],
            datetime.utcnow().isoformat()
        ))
        self.conn.commit()

    def save_score(self, scored):
        c = self.conn.cursor()
        c.execute("""
        INSERT INTO scores
        (product_id, demand_score, margin_score, competition_score, recency_score, quality_score, final_score, scored_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            scored.product_id,
            scored.demand_score, scored.margin_score,
            scored.competition_score, scored.recency_score,
            scored.quality_score, scored.final_score,
            scored.scored_at.isoformat()
        ))
        self.conn.commit()

    def get_all_products(self):
        c = self.conn.cursor()
        c.execute("SELECT * FROM products ORDER BY id")
        return [dict(row) for row in c.fetchall()]

    def get_latest_ebay_data(self, product_id):
        c = self.conn.cursor()
        c.execute("""
        SELECT * FROM ebay_market_data
        WHERE product_id=? ORDER BY fetched_at DESC LIMIT 1
        """, (product_id,))
        row = c.fetchone()
        return dict(row) if row else None

    def get_latest_trend_data(self, product_id):
        c = self.conn.cursor()
        c.execute("""
        SELECT * FROM trend_data
        WHERE product_id=? ORDER BY fetched_at DESC LIMIT 1
        """, (product_id,))
        row = c.fetchone()
        return dict(row) if row else None

    def get_scored_products(self, limit=25):
        c = self.conn.cursor()
        c.execute("""
        SELECT p.*, s.final_score, s.demand_score, s.margin_score,
               s.competition_score, s.recency_score, s.quality_score, s.scored_at
        FROM products p
        JOIN scores s ON p.id = s.product_id
        ORDER BY s.final_score DESC
        LIMIT ?
        """, (limit,))
        return [dict(row) for row in c.fetchall()]

    def count_rows(self, table):
        c = self.conn.cursor()
        c.execute(f"SELECT COUNT(*) as cnt FROM {table}")
        return c.fetchone()["cnt"]

    def last_run(self, table, column="discovered_at"):
        c = self.conn.cursor()
        c.execute(f"SELECT MAX({column}) as last_ts FROM {table}")
        row = c.fetchone()
        return row["last_ts"] if row else None

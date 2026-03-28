"""
Computes derived features before scoring.
Takes raw product + market + trend data, outputs feature dict.
"""

import logging

logger = logging.getLogger(__name__)


class FeatureEngineer:

    def __init__(self, config):
        self.config = config
        self.price_ranges = config["quality"]["price_ranges"]

    def compute(self, product, market_data, trend_data):
        source_price = product.get("source_price", 0)
        ebay_price = market_data.get("avg_price", 0) if market_data else 0
        units_sold = market_data.get("units_sold_90d", 0) if market_data else 0
        active = market_data.get("active_listings", 1) if market_data else 1

        # Margin
        if source_price > 0 and ebay_price > 0:
            margin = (ebay_price - source_price) / source_price
        else:
            margin = 0.0

        # Sales velocity (weekly)
        sales_velocity = units_sold / 13

        # Competition ratio
        competition_ratio = active / max(sales_velocity, 0.1)

        # Saturation
        saturation = competition_ratio

        # Price score
        price_score = self._price_score(ebay_price if ebay_price > 0 else source_price)

        # Keyword score
        keyword_score = self._keyword_score(product.get("name", ""))

        return {
            "margin": margin,
            "sales_velocity": sales_velocity,
            "competition_ratio": competition_ratio,
            "saturation": saturation,
            "price_score": price_score,
            "keyword_score": keyword_score,
        }

    def _price_score(self, price):
        r = self.price_ranges
        if r["ideal_low"] <= price <= r["ideal_high"]:
            return 1.0
        if r["ideal_high"] < price <= r["mid_high"]:
            return 0.8
        if 10 <= price < r["ideal_low"]:
            return 0.6
        if r["mid_high"] < price <= r["upper_limit"]:
            return 0.5
        return 0.2

    def _keyword_score(self, name):
        words = len(name.split())
        if words >= 3:
            return 1.0
        if words == 2:
            return 0.6
        return 0.3

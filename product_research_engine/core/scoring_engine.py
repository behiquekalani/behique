"""
Configurable scoring engine — reads all weights/thresholds from config.yaml.
No code edits needed to tune the formula.

final_score = 100 * (
    0.35 * demand +
    0.20 * margin +
    0.20 * competition +
    0.15 * recency +
    0.10 * quality
)
"""

import logging
from datetime import datetime
from core.models import ScoredProduct

logger = logging.getLogger(__name__)


class ScoringEngine:

    def __init__(self, config):
        self.config = config
        self.weights = config["scoring_weights"]

    def score(self, product_id, features, market_data, trend_data):
        demand = self._demand(market_data, trend_data)
        margin = self._margin(features["margin"])
        competition = self._competition(features, market_data)
        recency = self._recency(market_data)
        quality = self._quality(features)

        w = self.weights
        final = 100 * (
            w["demand"] * demand +
            w["margin"] * margin +
            w["competition"] * competition +
            w["recency"] * recency +
            w["quality"] * quality
        )

        return ScoredProduct(
            product_id=product_id,
            demand_score=round(demand, 4),
            margin_score=round(margin, 4),
            competition_score=round(competition, 4),
            recency_score=round(recency, 4),
            quality_score=round(quality, 4),
            final_score=round(final, 2),
            scored_at=datetime.utcnow()
        )

    def _demand(self, market, trend):
        weekly_sales = market.get("units_sold_90d", 0) / 13
        denom = self.config["demand"]["velocity_weekly_denominator"]
        velocity_norm = min(weekly_sales / denom, 1.0)

        trend_vel = min(trend.get("trend_velocity", 0.5), 1.0)
        trend_class = trend.get("trend_classification", "stable")
        class_score = self.config["trend_class_scores"].get(trend_class, 0.5)

        return (
            0.5 * velocity_norm +
            0.3 * trend_vel +
            0.2 * class_score
        )

    def _margin(self, margin_pct):
        t = self.config["margin_thresholds"]
        if margin_pct >= t["high"]:
            return 1.0
        if margin_pct >= t["medium_high"]:
            return 0.8
        if margin_pct >= t["medium"]:
            return 0.6
        if margin_pct >= t["low"]:
            return 0.3
        return 0.1

    def _competition(self, features, market):
        sell_through = market.get("sell_through", 0.5)
        weekly_sales = features.get("sales_velocity", 1)
        active = market.get("active_listings", 1)

        if weekly_sales <= 0:
            weekly_sales = 0.1

        saturation = active / weekly_sales
        denom = self.config["competition"]["saturation_denominator"]
        sat_norm = min(saturation / denom, 1.0)

        return 0.6 * sell_through + 0.4 * (1 - sat_norm)

    def _recency(self, market):
        days = market.get("last_sale_days", 30)
        r = self.config["recency_days"]

        if days <= r["day1"]:
            return 1.0
        if days <= r["day3"]:
            return 0.8
        if days <= r["day7"]:
            return 0.6
        if days <= r["day14"]:
            return 0.4
        return 0.2

    def _quality(self, features):
        return 0.7 * features.get("price_score", 0.5) + 0.3 * features.get("keyword_score", 0.5)

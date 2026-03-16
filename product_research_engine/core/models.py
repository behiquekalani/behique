"""
Data models for the product research engine.
All modules speak this language.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


@dataclass
class Product:
    name: str
    normalized_name: str
    category: str
    source: str
    source_price: float
    source_url: str
    rank: Optional[int] = None
    discovered_at: datetime = field(default_factory=datetime.utcnow)
    id: Optional[int] = None


@dataclass
class EbayMarketData:
    product_id: int
    avg_price: float
    units_sold_90d: int
    active_listings: int
    sell_through: float
    last_sale_days: int
    fetched_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class TrendData:
    product_id: int
    trend_velocity: float
    trend_classification: str
    trend_score: float
    fetched_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class ScoredProduct:
    product_id: int
    demand_score: float
    margin_score: float
    competition_score: float
    recency_score: float
    quality_score: float
    final_score: float
    scored_at: datetime = field(default_factory=datetime.utcnow)

"""
eBay cross-reference module — STUB until API approval.
Interface defined so pipeline can call it.

When implemented, will:
- Search eBay sold/completed listings via Browse API
- Pull: total sold (90d), last sale date, avg sold price, active listings, sell-through
- Return EbayMarketData objects
"""

import logging
from core.models import EbayMarketData

logger = logging.getLogger(__name__)


class EbayCrossReference:

    def __init__(self, ebay_client=None):
        self.client = ebay_client

    def lookup_product(self, product_name: str, source_price: float = 0) -> dict:
        """
        Search eBay for a product and return market data.

        Returns dict:
        {
            "avg_price": float,
            "units_sold_90d": int,
            "active_listings": int,
            "sell_through": float,     # sold / (sold + unsold)
            "last_sale_days": int,     # days since last sale
        }
        """
        raise NotImplementedError("eBay API keys pending -- expected Monday 2026-03-16")

    def lookup_batch(self, products: list) -> list:
        """Look up multiple products. Returns list of (product, market_data) tuples."""
        raise NotImplementedError("eBay API keys pending -- expected Monday 2026-03-16")

    def estimate_margin(self, source_price: float, ebay_avg_price: float) -> float:
        """Calculate margin percentage."""
        if source_price <= 0:
            return 0.0
        return (ebay_avg_price - source_price) / source_price

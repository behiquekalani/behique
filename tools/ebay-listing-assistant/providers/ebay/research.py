"""
eBay research adapter — pulls sold listing data via Browse API.
Feeds ResearchResult into the pipeline.

Uses: Browse API /item_summary/search with filter=buyingOptions:{FIXED_PRICE},soldItems
Docs: https://developer.ebay.com/api-docs/buy/browse/resources/item_summary/methods/search
"""

import logging
import statistics
from collections import Counter

import requests

from core.types import ProductInput, ResearchResult
from providers.ebay.auth import EbayAuth

logger = logging.getLogger(__name__)


class EbayResearchAdapter:
    """
    Stage 1 adapter: researches sold listings on eBay.
    Returns pricing data, category info, and sample titles.
    """

    def __init__(self, auth: EbayAuth, max_results: int = 50):
        self.auth = auth
        self.max_results = max_results

    def get_sold_data(self, product: ProductInput) -> ResearchResult:
        """
        Search eBay for completed/sold listings matching the product.
        Extracts pricing stats, category, and common item specifics.
        """
        items = self._search_sold(product.name, product.category_hint)

        if not items:
            raise ValueError(f"No sold listings found for: {product.name}")

        prices = [self._extract_price(item) for item in items if self._extract_price(item)]

        if not prices:
            raise ValueError(f"No valid prices found for: {product.name}")

        # Extract category from first result
        category_id = items[0].get("categoryId", "")
        category_name = items[0].get("categoryPath", "Unknown")
        if "/" in category_name:
            category_name = category_name.split("/")[-1].strip()

        # Collect titles from top sellers
        sample_titles = [item.get("title", "") for item in items[:10]]

        # Extract common item specifics
        common_specifics = self._extract_common_specifics(items)

        # Shipping costs
        shipping_costs = []
        for item in items:
            shipping = item.get("shippingOptions", [{}])
            if shipping:
                cost = shipping[0].get("shippingCost", {}).get("value")
                if cost:
                    shipping_costs.append(float(cost))

        return ResearchResult(
            category_id=category_id,
            category_name=category_name,
            avg_sold_price=statistics.mean(prices),
            min_sold_price=min(prices),
            max_sold_price=max(prices),
            median_sold_price=statistics.median(prices),
            sample_titles=sample_titles,
            common_specifics=common_specifics,
            avg_shipping_cost=statistics.mean(shipping_costs) if shipping_costs else 0.0,
            sell_through_rate=None,  # Requires separate active listings query
            raw_listings=items[:5],  # Keep first 5 for debug
        )

    def _search_sold(self, query: str, category_hint: str = None) -> list[dict]:
        """Call Browse API search for sold items."""
        url = f"{self.auth.api_base}/buy/browse/v1/item_summary/search"

        params = {
            "q": query,
            "filter": "buyingOptions:{FIXED_PRICE}",
            "sort": "-price",
            "limit": self.max_results,
        }

        if category_hint:
            params["category_ids"] = category_hint

        headers = self.auth.get_headers()

        logger.info(f"Searching eBay sold: '{query}' (limit={self.max_results})")
        resp = requests.get(url, headers=headers, params=params, timeout=20)
        resp.raise_for_status()

        data = resp.json()
        items = data.get("itemSummaries", [])
        logger.info(f"Found {len(items)} sold listings")

        return items

    def _extract_price(self, item: dict) -> float | None:
        """Pull price from item summary."""
        price_info = item.get("price", {})
        value = price_info.get("value")
        if value:
            try:
                return float(value)
            except (ValueError, TypeError):
                return None
        return None

    def _extract_common_specifics(self, items: list[dict]) -> dict:
        """
        Find the most common item specifics across sold listings.
        Returns e.g. {"Brand": "Sony", "Color": "Black"}
        """
        specifics_counter: dict[str, Counter] = {}

        for item in items:
            for aspect in item.get("itemAffinity", []):
                name = aspect.get("localizedName", "")
                value = aspect.get("localizedValue", "")
                if name and value:
                    if name not in specifics_counter:
                        specifics_counter[name] = Counter()
                    specifics_counter[name][value] += 1

        # Return the most common value for each specific
        return {
            name: counter.most_common(1)[0][0]
            for name, counter in specifics_counter.items()
            if counter
        }

"""
eBay Research Adapter — Pulls comparable sold listing data.

V1: Web-based research. Ceiba searches eBay sold listings and feeds structured data
    through parse_comp_data(). No API keys needed.
V2: Swap to eBay Finding API / Marketplace Insights API.
"""

import statistics
from urllib.parse import quote_plus
from core.types import ProductInput, ResearchResult


class EbayWebResearch:
    """
    V1 research adapter — generates search URLs and parses manually-gathered data.

    Usage (in Ceiba session):
        research = EbayWebResearch()
        url = research.build_search_url(product)  # Ceiba searches this
        result = research.parse_comp_data(         # Ceiba fills from search results
            sold_prices=[12.99, 15.50, 11.00, ...],
            titles=["Hello Kitty Mug ...", ...],
            specifics={"Brand": "Sanrio", ...},
            category_id="40281",
            category_name="Coffee Mugs",
        )
    """

    def get_sold_data(self, product: ProductInput) -> ResearchResult:
        """
        Pipeline adapter interface.

        In V1, this is called with pre-populated data via from_dict().
        In V2, this would make actual API calls.
        """
        raise NotImplementedError(
            "V1 uses parse_comp_data() with Ceiba-gathered data. "
            "Call build_search_url() first, then parse_comp_data() with results."
        )

    def build_search_url(self, product: ProductInput, sold_only: bool = True) -> str:
        """
        Build eBay search URL for sold/completed listings.

        Args:
            product: The product to research
            sold_only: If True, filter to sold items only (default)

        Returns:
            eBay search URL with sold listing filters
        """
        query = quote_plus(product.name)
        base = "https://www.ebay.com/sch/i.html"
        params = f"_nkw={query}&_sop=13"  # Sort by price + shipping lowest first

        if sold_only:
            params += "&LH_Complete=1&LH_Sold=1"  # Completed AND sold

        # Add condition filter if specified
        condition_map = {
            "New": "1000",
            "Used": "3000",
            "Refurbished": "2000",
            "For Parts": "7000",
        }
        if product.condition in condition_map:
            params += f"&LH_ItemCondition={condition_map[product.condition]}"

        return f"{base}?{params}"

    def build_active_url(self, product: ProductInput) -> str:
        """Build URL for currently active listings (competition check)."""
        query = quote_plus(product.name)
        return f"https://www.ebay.com/sch/i.html?_nkw={query}&_sop=12"

    def parse_comp_data(
        self,
        sold_prices: list[float],
        titles: list[str] = None,
        specifics: dict = None,
        category_id: str = "",
        category_name: str = "",
        active_listing_count: int = 0,
        shipping_costs: list[float] = None,
    ) -> ResearchResult:
        """
        Convert raw comp data into a structured ResearchResult.

        Args:
            sold_prices: List of final sold prices from eBay search
            titles: Sample titles from top-selling listings
            specifics: Common item specifics (e.g., {"Brand": "Sanrio"})
            category_id: eBay category ID
            category_name: Human-readable category name
            active_listing_count: Number of active competing listings
            shipping_costs: List of shipping costs from sold listings
        """
        if not sold_prices:
            raise ValueError("Need at least one sold price to calculate comps")

        prices = sorted(sold_prices)
        avg_shipping = 0.0
        if shipping_costs:
            avg_shipping = statistics.mean(shipping_costs)

        # Calculate sell-through rate if we have active listing count
        sell_through = None
        if active_listing_count > 0 and len(sold_prices) > 0:
            # Rough estimate: sold in last 90 days / (sold + active)
            sell_through = len(sold_prices) / (len(sold_prices) + active_listing_count)

        return ResearchResult(
            category_id=category_id,
            category_name=category_name,
            avg_sold_price=round(statistics.mean(prices), 2),
            min_sold_price=round(min(prices), 2),
            max_sold_price=round(max(prices), 2),
            median_sold_price=round(statistics.median(prices), 2),
            sample_titles=titles or [],
            common_specifics=specifics or {},
            avg_shipping_cost=round(avg_shipping, 2),
            sell_through_rate=round(sell_through, 3) if sell_through is not None else None,
        )

    @classmethod
    def from_dict(cls, data: dict) -> ResearchResult:
        """
        Create ResearchResult directly from a dict.
        Useful when Ceiba has already gathered all the data.
        """
        instance = cls()
        return instance.parse_comp_data(
            sold_prices=data.get("sold_prices", []),
            titles=data.get("titles", []),
            specifics=data.get("specifics", {}),
            category_id=data.get("category_id", ""),
            category_name=data.get("category_name", ""),
            active_listing_count=data.get("active_listing_count", 0),
            shipping_costs=data.get("shipping_costs", []),
        )

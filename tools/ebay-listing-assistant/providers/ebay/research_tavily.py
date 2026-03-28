"""
eBay Research Adapter — Tavily-powered.

Uses the Tavily MCP connector (already installed in Claude Code) to search
eBay sold listings and extract pricing data. Replaces manual URL-based research.

Usage (in Ceiba session):
    from providers.ebay.research_tavily import TavilyEbayResearch
    research = TavilyEbayResearch()
    result = research.search_sold_listings("Hello Kitty Coffee Mug", condition="Used")
    # Returns ResearchResult with real pricing data

Note: This module provides helper methods for Ceiba to call Tavily via MCP.
The actual Tavily calls happen through the MCP connector in the Claude session,
not through Python API calls. This module formats queries and parses results.
"""

import re
import statistics
from core.types import ProductInput, ResearchResult


class TavilyEbayResearch:
    """
    Research adapter that generates Tavily search queries for eBay sold listings.

    How it works:
    1. build_tavily_query() generates the optimal search query
    2. Ceiba calls Tavily MCP with that query
    3. parse_tavily_results() converts Tavily output → ResearchResult
    """

    def build_tavily_query(self, product: ProductInput, sold_only: bool = True) -> dict:
        """
        Build a Tavily search query optimized for eBay sold listing data.

        Returns dict with:
            - query: The search string
            - include_domains: Restricted to eBay
            - search_depth: "advanced" for better results
        """
        condition_str = f" {product.condition}" if product.condition else ""
        sold_str = " sold" if sold_only else ""

        query = f"eBay{sold_str} {product.name}{condition_str} price"

        return {
            "query": query,
            "include_domains": ["ebay.com"],
            "search_depth": "advanced",
            "max_results": 10,
        }

    def build_reddit_query(self, product: ProductInput) -> dict:
        """
        Build a Tavily query to find Reddit discussions about the product.
        Useful for market sentiment, demand signals, common complaints.
        """
        query = f"reddit {product.name} worth price selling eBay"

        return {
            "query": query,
            "include_domains": ["reddit.com"],
            "search_depth": "advanced",
            "max_results": 5,
        }

    def extract_prices_from_text(self, text: str) -> list[float]:
        """
        Extract dollar prices from search result text.
        Handles formats: $12.99, $1,234.56, USD 12.99
        """
        # Match $XX.XX patterns
        price_patterns = [
            r'\$(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)',  # $12.99 or $1,234.56
            r'(?:USD|US\$)\s*(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)',  # USD 12.99
            r'(?:sold for|sold at|final price|winning bid)[:\s]*\$?(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)',
        ]

        prices = []
        for pattern in price_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for m in matches:
                try:
                    price = float(m.replace(",", ""))
                    # Filter unrealistic prices
                    if 0.99 <= price <= 10000:
                        prices.append(price)
                except ValueError:
                    continue

        return prices

    def extract_titles_from_text(self, text: str) -> list[str]:
        """Extract eBay listing titles from search result text."""
        # Look for patterns that look like eBay titles (usually ALL CAPS or Title Case, 30-80 chars)
        lines = text.split("\n")
        titles = []
        for line in lines:
            line = line.strip()
            if 20 <= len(line) <= 100 and not line.startswith("http"):
                # Looks like it could be a title
                titles.append(line)
        return titles[:10]  # Keep top 10

    def parse_tavily_results(
        self,
        results: list[dict],
        category_id: str = "",
        category_name: str = "",
        active_count: int = 0,
    ) -> ResearchResult:
        """
        Parse Tavily search results into a ResearchResult.

        Args:
            results: List of Tavily result dicts (each has 'content', 'title', 'url')
            category_id: eBay category ID (if known)
            category_name: Category name (if known)
            active_count: Number of active competing listings (from a separate search)
        """
        all_prices = []
        all_titles = []

        for r in results:
            content = r.get("content", "")
            title = r.get("title", "")

            # Extract prices from content
            prices = self.extract_prices_from_text(content)
            all_prices.extend(prices)

            # Extract from title too
            title_prices = self.extract_prices_from_text(title)
            all_prices.extend(title_prices)

            # Collect titles
            if title and "ebay" in title.lower():
                all_titles.append(title)

        if not all_prices:
            raise ValueError(
                "No prices found in Tavily results. "
                "Try a more specific product name or use manual research."
            )

        # Deduplicate prices (same item appearing in multiple results)
        prices = sorted(set(all_prices))

        # Calculate stats
        sell_through = None
        if active_count > 0 and len(prices) > 0:
            sell_through = len(prices) / (len(prices) + active_count)

        return ResearchResult(
            category_id=category_id,
            category_name=category_name,
            avg_sold_price=round(statistics.mean(prices), 2),
            min_sold_price=round(min(prices), 2),
            max_sold_price=round(max(prices), 2),
            median_sold_price=round(statistics.median(prices), 2),
            sample_titles=all_titles[:5],
            common_specifics={},
            avg_shipping_cost=0.0,
            sell_through_rate=round(sell_through, 3) if sell_through else None,
            raw_listings=[{"source": "tavily", "result_count": len(results)}],
        )

    def from_ceiba_session(
        self,
        sold_results: list[dict],
        active_results: list[dict] = None,
        category_id: str = "",
        category_name: str = "",
    ) -> ResearchResult:
        """
        Convenience method: Ceiba calls Tavily, passes raw results here.

        Usage in session:
            # Ceiba calls tavily_search with build_tavily_query() output
            # Then passes the results array here
            research = TavilyEbayResearch()
            result = research.from_ceiba_session(
                sold_results=tavily_sold_response["results"],
                active_results=tavily_active_response["results"],
                category_name="Coffee Mugs"
            )
        """
        active_count = 0
        if active_results:
            # Estimate active listing count from results
            for r in active_results:
                count_match = re.search(r'(\d+)\s*results', r.get("content", ""))
                if count_match:
                    active_count = max(active_count, int(count_match.group(1)))

        return self.parse_tavily_results(
            results=sold_results,
            category_id=category_id,
            category_name=category_name,
            active_count=active_count,
        )

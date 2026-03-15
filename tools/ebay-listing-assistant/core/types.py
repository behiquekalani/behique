"""
Shared data models — the contract between all layers.
Every adapter (eBay, Shopify, Amazon) speaks this language.
"""

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class ProductInput:
    """What comes in."""
    name: str
    image_path: Optional[str] = None      # Local file path
    image_url: Optional[str] = None       # Remote URL
    condition: str = "Used"               # New, Used, Refurbished
    category_hint: Optional[str] = None   # e.g. "Electronics > Cameras"
    notes: Optional[str] = None           # Any extra context for the LLM


@dataclass
class ResearchResult:
    """eBay sold listing research output."""
    category_id: str
    category_name: str
    avg_sold_price: float
    min_sold_price: float
    max_sold_price: float
    median_sold_price: float
    sample_titles: list[str] = field(default_factory=list)  # Top selling titles
    common_specifics: dict = field(default_factory=dict)     # e.g. {"Brand": "Sony"}
    avg_shipping_cost: float = 0.0
    sell_through_rate: Optional[float] = None                # % that sold vs listed
    raw_listings: list[dict] = field(default_factory=list)   # Full API response kept for debug


@dataclass
class ListingContent:
    """LLM-generated listing content."""
    title: str                                    # Max 80 chars (eBay limit)
    description: str                              # HTML-safe description
    item_specifics: dict = field(default_factory=dict)
    suggested_price: float = 0.0
    suggested_condition: str = "Used"
    keywords: list[str] = field(default_factory=list)


@dataclass
class PublishedListing:
    """Result of a successful listing publish."""
    platform: str                        # "ebay", "shopify", etc.
    listing_id: str
    listing_url: str
    title: str
    price: float
    status: str = "active"              # active, ended, sold
    raw_response: dict = field(default_factory=dict)

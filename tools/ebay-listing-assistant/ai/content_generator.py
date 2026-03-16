"""
eBay Content Generator — LLM-powered listing content creation.

V1: Builds structured prompts + applies eBay SEO rules deterministically.
    Ceiba (Claude) evaluates prompts in-session. No external LLM calls needed.
V2: Routes through routing.py for Ollama/Claude/ChatGPT model selection.
"""

from dataclasses import dataclass
from core.types import ProductInput, ResearchResult, ListingContent
from core.pricing import recommend_price, PricingRecommendation


class EbayContentGenerator:
    """
    Generates optimized eBay listing content from product + research data.

    V1 approach: deterministic title/description generation using templates
    and eBay SEO rules. The "LLM" is Ceiba running in-session — this module
    provides the structure, Ceiba provides the creativity.
    """

    def generate(
        self,
        product: ProductInput,
        research: ResearchResult,
        pricing: PricingRecommendation = None,
        item_cost: float = 0.0,
        weight_oz: float = 12.0,
        fragile: bool = False,
    ) -> ListingContent:
        """
        Pipeline adapter interface — generates full listing content.

        Returns ListingContent with title, description, specifics, and price.
        """
        # Generate pricing if not provided
        if pricing is None:
            pricing = recommend_price(
                research=research,
                item_cost=item_cost,
                weight_oz=weight_oz,
                fragile=fragile,
            )

        title = self._generate_title(product, research)
        description = self._generate_description(product, research, pricing)
        specifics = self._generate_specifics(product, research)

        return ListingContent(
            title=title,
            description=description,
            item_specifics=specifics,
            suggested_price=pricing.list_price,
            suggested_condition=product.condition or "Used",
            keywords=self._extract_keywords(product, research),
        )

    def _generate_title(self, product: ProductInput, research: ResearchResult) -> str:
        """
        Generate eBay-optimized title (max 80 chars).

        eBay SEO rules:
        - Front-load brand and key identifiers
        - Include condition for used items
        - No filler words (the, a, for, with, and)
        - No special characters or ALL CAPS
        - Use every character — 80 char max is precious real estate
        - Include item type at the end
        """
        # Start with product name, clean it up
        parts = product.name.strip().split()

        # Add brand from specifics if not in name
        brand = research.common_specifics.get("Brand", "")
        if brand and brand.lower() not in product.name.lower():
            parts.insert(0, brand)

        # Add condition if Used or Refurbished
        if product.condition in ("Used", "Refurbished"):
            parts.append(product.condition)

        # Remove filler words
        filler = {"the", "a", "an", "for", "with", "and", "of", "in", "on", "to", "is"}
        parts = [p for p in parts if p.lower() not in filler]

        # Join and enforce 80 char limit
        title = " ".join(parts)
        if len(title) > 80:
            # Trim from end, keeping whole words
            while len(title) > 80 and " " in title:
                title = title.rsplit(" ", 1)[0]

        return title

    def _generate_description(
        self,
        product: ProductInput,
        research: ResearchResult,
        pricing: PricingRecommendation,
    ) -> str:
        """
        Generate clean HTML description optimized for eBay mobile.

        Rules:
        - Mobile-first (most eBay browsing is mobile)
        - No external CSS/JS (eBay strips it)
        - Inline styles only
        - Bullet points for specs
        - Condition disclosure upfront
        - Shipping info included
        """
        specifics = research.common_specifics
        brand = specifics.get("Brand", "")
        condition_note = self._condition_description(product.condition)

        # Build item specifics bullets
        spec_bullets = ""
        for key, val in specifics.items():
            spec_bullets += f"<li><strong>{key}:</strong> {val}</li>\n"

        shipping_note = (
            f"Ships from Puerto Rico via {pricing.shipping.service}. "
            f"Estimated delivery: {pricing.shipping.delivery_days} business days."
        )

        html = f"""<div style="font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 10px;">

<h2 style="color: #333; margin-bottom: 5px;">{product.name}</h2>
{f'<p style="color: #666; font-size: 14px;">by {brand}</p>' if brand else ''}

<hr style="border: 1px solid #eee;">

<h3 style="color: #333;">Condition</h3>
<p>{condition_note}</p>

<h3 style="color: #333;">Details</h3>
<ul style="line-height: 1.8;">
{spec_bullets}</ul>

{f'<h3 style="color: #333;">Notes</h3><p>{product.notes}</p>' if product.notes else ''}

<hr style="border: 1px solid #eee;">

<h3 style="color: #333;">Shipping</h3>
<p>{shipping_note}</p>

<p style="color: #888; font-size: 12px; margin-top: 20px;">
Thank you for looking! Please message with any questions before purchasing.
</p>

</div>"""
        return html

    def _generate_specifics(self, product: ProductInput, research: ResearchResult) -> dict:
        """Merge research specifics with product input data."""
        specifics = dict(research.common_specifics)

        # Add condition
        specifics["Condition"] = product.condition or "Used"

        # Category hint can inform specifics
        if product.category_hint:
            specifics.setdefault("Category", product.category_hint)

        return specifics

    def _extract_keywords(self, product: ProductInput, research: ResearchResult) -> list[str]:
        """Extract search keywords from product name and research titles."""
        keywords = set()

        # From product name
        for word in product.name.lower().split():
            if len(word) > 2:
                keywords.add(word)

        # From top-selling titles
        for title in research.sample_titles[:5]:
            for word in title.lower().split():
                if len(word) > 3:
                    keywords.add(word)

        # From specifics
        for val in research.common_specifics.values():
            if isinstance(val, str) and len(val) > 2:
                keywords.add(val.lower())

        return sorted(keywords)

    def _condition_description(self, condition: str) -> str:
        """Generate appropriate condition disclosure text."""
        descriptions = {
            "New": "Brand new, unused, in original packaging (if applicable).",
            "Used": "Pre-owned item in good condition. Please see photos for actual condition. "
                    "May show minor signs of use.",
            "Refurbished": "Professionally refurbished to working condition. "
                          "May show minor cosmetic wear.",
            "For Parts": "Sold as-is for parts or repair. May not be fully functional.",
        }
        return descriptions.get(condition, descriptions["Used"])

    def build_prompt(self, product: ProductInput, research: ResearchResult) -> str:
        """
        Build a structured prompt for when Ceiba wants to use LLM creativity
        instead of the deterministic generator.

        Returns the prompt text — Ceiba evaluates it in-session.
        """
        comp_prices = f"${research.min_sold_price:.2f} - ${research.max_sold_price:.2f}"
        comp_median = f"${research.median_sold_price:.2f}"
        sample = "\n".join(f"  - {t}" for t in research.sample_titles[:5])

        return f"""Generate an optimized eBay listing for this product:

PRODUCT: {product.name}
CONDITION: {product.condition}
CATEGORY: {research.category_name} (ID: {research.category_id})

COMPARABLE SOLD LISTINGS:
  Price range: {comp_prices}
  Median sold price: {comp_median}
  Top-selling titles:
{sample}

  Common item specifics: {research.common_specifics}

RULES:
1. Title: MAX 80 characters. Front-load brand + keywords. No filler words.
2. Description: Clean HTML, mobile-friendly, bullet points for specs.
3. Item specifics: Include all that apply from the category.
4. Disclose condition honestly — builds trust and prevents returns.

OUTPUT FORMAT:
- title: (exactly 80 chars or fewer)
- description: (HTML)
- item_specifics: (key: value pairs)
- keywords: (comma-separated search terms)
"""

"""
Main orchestrator — generic pipeline that runs research → generate → publish.
Swap any adapter without touching this file.
"""

import logging
from typing import Optional
from core.types import ProductInput, ResearchResult, ListingContent, PublishedListing

logger = logging.getLogger(__name__)


class ListingPipeline:
    """
    Three-stage pipeline:
      1. Research — pull sold listing data from a marketplace
      2. Generate — use LLM to write title/description/specifics
      3. Publish  — post the listing

    Each stage is a pluggable adapter.
    """

    def __init__(self, research_adapter, content_generator, publishing_adapter):
        self.research = research_adapter
        self.content = content_generator
        self.publisher = publishing_adapter

    def run(self, product: ProductInput, dry_run: bool = False) -> dict:
        """
        Full pipeline. Returns result dict with all intermediate data.
        Set dry_run=True to skip the publish step (useful for testing).
        """
        result = {
            "product": product,
            "research": None,
            "content": None,
            "published": None,
            "errors": [],
        }

        # Stage 1: Research
        logger.info(f"[Pipeline] Researching: {product.name}")
        try:
            research: ResearchResult = self.research.get_sold_data(product)
            result["research"] = research
            logger.info(f"[Pipeline] Research complete — avg sold: ${research.avg_sold_price:.2f}")
        except Exception as e:
            logger.error(f"[Pipeline] Research failed: {e}")
            result["errors"].append({"stage": "research", "error": str(e)})
            return result

        # Stage 2: Generate content
        logger.info(f"[Pipeline] Generating content for: {product.name}")
        try:
            content: ListingContent = self.content.generate(product, research)
            result["content"] = content
            logger.info(f"[Pipeline] Content generated — title: {content.title}")
        except Exception as e:
            logger.error(f"[Pipeline] Content generation failed: {e}")
            result["errors"].append({"stage": "content", "error": str(e)})
            return result

        # Validate eBay constraints before publishing
        validation_errors = self._validate_content(content)
        if validation_errors:
            logger.warning(f"[Pipeline] Validation issues: {validation_errors}")
            result["errors"].extend(validation_errors)
            # Don't abort — log and continue, let publisher decide

        # Stage 3: Publish
        if dry_run:
            logger.info("[Pipeline] DRY RUN — skipping publish")
            result["published"] = {"dry_run": True, "title": content.title, "price": content.suggested_price}
            return result

        logger.info(f"[Pipeline] Publishing: {content.title}")
        try:
            published: PublishedListing = self.publisher.publish(product, content)
            result["published"] = published
            logger.info(f"[Pipeline] Published — ID: {published.listing_id}, URL: {published.listing_url}")
        except Exception as e:
            logger.error(f"[Pipeline] Publish failed: {e}")
            result["errors"].append({"stage": "publish", "error": str(e)})

        return result

    def _validate_content(self, content: ListingContent) -> list[dict]:
        """
        Validate LLM output against eBay's constraints.
        Catches issues before they fail at publish time.
        """
        errors = []

        if len(content.title) > 80:
            errors.append({
                "stage": "validation",
                "field": "title",
                "error": f"Title too long ({len(content.title)} chars, max 80). Will truncate."
            })
            content.title = content.title[:80]

        if len(content.description) > 500000:
            errors.append({
                "stage": "validation",
                "field": "description",
                "error": "Description exceeds 500k char limit. Will truncate."
            })
            content.description = content.description[:500000]

        if content.suggested_price <= 0:
            errors.append({
                "stage": "validation",
                "field": "price",
                "error": "Price must be > 0. Using research median."
            })

        return errors

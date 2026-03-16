"""Walmart Trending scraper — STUB. Interface defined, implementation pending."""

import logging
from scrapers.base_scraper import BaseScraper

logger = logging.getLogger(__name__)


class WalmartTrendingScraper(BaseScraper):

    def scrape(self) -> list:
        logger.info("WalmartTrendingScraper: not implemented yet")
        raise NotImplementedError("Walmart scraper coming soon")

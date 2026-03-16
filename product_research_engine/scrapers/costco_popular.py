"""Costco Popular Items scraper — STUB."""

import logging
from scrapers.base_scraper import BaseScraper

logger = logging.getLogger(__name__)


class CostcoPopularScraper(BaseScraper):

    def scrape(self) -> list:
        logger.info("CostcoPopularScraper: not implemented yet")
        raise NotImplementedError("Costco scraper coming soon")

"""Target Trending scraper — STUB."""

import logging
from scrapers.base_scraper import BaseScraper

logger = logging.getLogger(__name__)


class TargetTrendingScraper(BaseScraper):

    def scrape(self) -> list:
        logger.info("TargetTrendingScraper: not implemented yet")
        raise NotImplementedError("Target scraper coming soon")

"""Home Depot Best Sellers scraper — STUB."""

import logging
from scrapers.base_scraper import BaseScraper

logger = logging.getLogger(__name__)


class HomeDepotBestSellersScraper(BaseScraper):

    def scrape(self) -> list:
        logger.info("HomeDepotBestSellersScraper: not implemented yet")
        raise NotImplementedError("Home Depot scraper coming soon")

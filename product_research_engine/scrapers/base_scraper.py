"""
Abstract base scraper with anti-detection built in:
- Random delays, UA rotation, proxy rotation, retry with backoff
"""

import random
import time
import logging
import requests
from abc import ABC, abstractmethod
from bs4 import BeautifulSoup
from core.utils import UserAgentRotator, ProxyManager, RateLimiter
from urllib.parse import urlparse

logger = logging.getLogger(__name__)


class BaseScraper(ABC):

    def __init__(self, config):
        self.config = config
        self.ua = UserAgentRotator()
        self.proxy_mgr = ProxyManager(config["proxy"]["path"])
        self.rate_limiter = RateLimiter(config["rate_limit"]["per_domain_per_minute"])
        self.delay_min = config["scraper"]["delay_min_seconds"]
        self.delay_max = config["scraper"]["delay_max_seconds"]
        self.retries = config["scraper"]["retries"]
        self.backoff = config["scraper"]["backoff_factor"]
        self.timeout = config["scraper"]["timeout"]

    def fetch_page(self, url) -> BeautifulSoup:
        domain = urlparse(url).netloc
        self.rate_limiter.wait_if_needed(domain)

        for attempt in range(self.retries):
            try:
                ua = self.ua.random()
                proxy = self.proxy_mgr.get()
                proxies = {"http": proxy, "https": proxy} if proxy else None

                headers = {
                    "User-Agent": ua,
                    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                    "Accept-Language": "en-US,en;q=0.9",
                    "Accept-Encoding": "gzip, deflate, br",
                    "DNT": "1",
                    "Connection": "keep-alive",
                    "Upgrade-Insecure-Requests": "1",
                }

                resp = requests.get(url, headers=headers, proxies=proxies, timeout=self.timeout)
                resp.raise_for_status()

                self.proxy_mgr.report_success(proxy)
                self.rate_limiter.record(domain)

                # Random delay
                time.sleep(random.uniform(self.delay_min, self.delay_max))

                return BeautifulSoup(resp.text, "lxml")

            except Exception as e:
                self.proxy_mgr.report_failure(proxy) if proxy else None
                wait = self.backoff ** (attempt + 1) + random.uniform(0, 3)
                logger.warning(f"Fetch failed ({domain}, attempt {attempt+1}): {str(e)[:60]}. Retry in {wait:.1f}s")
                time.sleep(wait)

        raise Exception(f"Failed to fetch {url} after {self.retries} attempts")

    @abstractmethod
    def scrape(self) -> list:
        """Returns list of product dicts: name, price, url, rank, category"""
        raise NotImplementedError

    @property
    def source_name(self):
        return self.__class__.__name__

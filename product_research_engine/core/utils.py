"""
Shared utilities: UA rotation, proxy management, rate limiting, retry logic.
"""

import random
import time
import logging
from pathlib import Path
from collections import defaultdict

logger = logging.getLogger(__name__)

# 20+ real user agents for rotation
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.3 Safari/605.1.15",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:123.0) Gecko/20100101 Firefox/123.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:123.0) Gecko/20100101 Firefox/123.0",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64; rv:123.0) Gecko/20100101 Firefox/123.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 13_6) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Safari/605.1.15",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:122.0) Gecko/20100101 Firefox/122.0",
    "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:122.0) Gecko/20100101 Firefox/122.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36 OPR/108.0.0.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36 Vivaldi/6.5",
    "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_3) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.3 Safari/605.1.15",
]


class UserAgentRotator:
    def random(self):
        return random.choice(USER_AGENTS)


class ProxyManager:

    def __init__(self, proxy_path):
        self.proxies = []
        self.failures = {}
        path = Path(proxy_path).expanduser()

        if path.exists():
            with open(path) as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    parts = line.split(":")
                    if len(parts) == 4:
                        ip, port, user, pw = parts
                        url = f"http://{user}:{pw}@{ip}:{port}"
                        self.proxies.append(url)
                        self.failures[url] = 0
            logger.info(f"Loaded {len(self.proxies)} proxies from {path}")
        else:
            logger.warning(f"Proxy file not found: {path} -- running without proxies")

    def get(self):
        if not self.proxies:
            return None
        # Skip proxies with 3+ failures
        available = [p for p in self.proxies if self.failures.get(p, 0) < 3]
        if not available:
            # Reset all
            for p in self.proxies:
                self.failures[p] = 0
            available = self.proxies
        return random.choice(available)

    def report_failure(self, proxy):
        if proxy:
            self.failures[proxy] = self.failures.get(proxy, 0) + 1

    def report_success(self, proxy):
        if proxy:
            self.failures[proxy] = 0

    @property
    def count(self):
        return len(self.proxies)

    @property
    def active_count(self):
        return sum(1 for p in self.proxies if self.failures.get(p, 0) < 3)


class RateLimiter:
    """Track requests per domain, auto-throttle if approaching limits."""

    def __init__(self, max_per_minute=30):
        self.max_per_minute = max_per_minute
        self.requests = defaultdict(list)  # domain -> [timestamps]

    def wait_if_needed(self, domain):
        now = time.time()
        # Clean old entries (> 60s)
        self.requests[domain] = [t for t in self.requests[domain] if now - t < 60]

        if len(self.requests[domain]) >= self.max_per_minute:
            wait_time = 60 - (now - self.requests[domain][0])
            if wait_time > 0:
                logger.info(f"Rate limit reached for {domain}, waiting {wait_time:.1f}s")
                time.sleep(wait_time)

        self.requests[domain].append(time.time())

    def record(self, domain):
        self.requests[domain].append(time.time())


def random_delay(min_s, max_s):
    delay = random.uniform(min_s, max_s)
    time.sleep(delay)

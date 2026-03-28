"""
Amazon Best Sellers scraper.
Primary: Playwright with stealth (headless browser)
Fallback: Google Shopping results (no anti-bot issues)

Amazon blocks basic requests+BS4, so we use a real browser.
"""

import logging
import asyncio
import random
import time
from scrapers.base_scraper import BaseScraper
from core.utils import UserAgentRotator, random_delay

logger = logging.getLogger(__name__)

# Amazon Best Sellers category URLs
CATEGORY_URLS = {
    "electronics": "/Best-Sellers-Electronics/zgbs/electronics",
    "home-garden": "/Best-Sellers-Home-Garden/zgbs/garden",
    "toys-and-games": "/Best-Sellers-Toys-Games/zgbs/toys-and-games",
    "tools": "/Best-Sellers-Tools-Home-Improvement/zgbs/hi",
    "sports-outdoors": "/Best-Sellers-Sports-Outdoors/zgbs/sporting-goods",
    "kitchen": "/Best-Sellers-Kitchen-Dining/zgbs/kitchen",
    "beauty": "/Best-Sellers-Beauty/zgbs/beauty",
    "pet-supplies": "/Best-Sellers-Pet-Supplies/zgbs/pet-supplies",
}


class AmazonBestSellersScraper(BaseScraper):

    def __init__(self, config):
        super().__init__(config)
        self.headless = config["amazon"].get("playwright_headless", True)
        self.max_products = config["amazon"].get("max_products", 100)
        self.categories = config["amazon"].get("categories", list(CATEGORY_URLS.keys()))
        self.use_fallback = config["google_shopping"].get("enabled_fallback", True)

    def scrape(self) -> list:
        """Synchronous wrapper for async scrape."""
        products = []
        try:
            products = asyncio.run(self._scrape_playwright())
        except Exception as e:
            logger.error(f"Playwright scrape failed: {e}")

        # Fallback if Playwright returned nothing (blocked, CAPTCHA, layout change)
        if not products and self.use_fallback:
            logger.info("Playwright returned 0 products — falling back to Google Shopping...")
            products = self._scrape_google_shopping()

        return products

    async def _scrape_playwright(self):
        """Scrape Amazon Best Sellers using Playwright + stealth."""
        try:
            from playwright.async_api import async_playwright
        except ImportError:
            logger.error("Playwright not installed. Run: pip install playwright && playwright install")
            raise

        # Try importing stealth
        try:
            from playwright_stealth import stealth_async
            has_stealth = True
        except ImportError:
            logger.warning("playwright-stealth not installed, running without stealth")
            has_stealth = False

        products = []
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=self.headless)

            for cat_name in self.categories:
                if cat_name not in CATEGORY_URLS:
                    continue

                url = f"https://www.amazon.com{CATEGORY_URLS[cat_name]}"
                logger.info(f"Scraping Amazon Best Sellers: {cat_name}")

                try:
                    ua = self.ua.random()
                    proxy = self.proxy_mgr.get()
                    context_opts = {"user_agent": ua}
                    if proxy:
                        context_opts["proxy"] = {"server": proxy}

                    context = await browser.new_context(**context_opts)
                    page = await context.new_page()

                    if has_stealth:
                        await stealth_async(page)

                    await page.goto(url, timeout=self.timeout * 1000, wait_until="domcontentloaded")
                    await page.wait_for_timeout(random.randint(2000, 4000))

                    # Extract products — try multiple selector strategies
                    items = await self._extract_products(page, cat_name)
                    products.extend(items[:self.max_products // len(self.categories)])

                    self.proxy_mgr.report_success(proxy)
                    logger.info(f"  Found {len(items)} products in {cat_name}")

                    await context.close()
                    await asyncio.sleep(random.uniform(self.delay_min, self.delay_max))

                except Exception as e:
                    logger.warning(f"  Failed {cat_name}: {str(e)[:80]}")
                    self.proxy_mgr.report_failure(proxy) if proxy else None

            await browser.close()

        logger.info(f"Total Amazon products: {len(products)}")
        return products

    async def _extract_products(self, page, category):
        """Try multiple CSS selector strategies for Amazon BS pages."""
        products = []

        # Strategy 1: Modern Amazon layout (2025-2026)
        selectors = [
            ("div[data-asin]", "span.zg-text-center-align", "span._cDEzb_p13n-sc-price_3mJ9Z, span.p13n-sc-price"),
            ("div.zg-item-immersion", "div._cDEzb_p13n-sc-css-line-clamp-3_g3dy1, div.p13n-sc-truncate", "span._cDEzb_p13n-sc-price_3mJ9Z, span.p13n-sc-price"),
            ("li.zg-item-immersion", "span.zg-text-center-align", "span.p13n-sc-price"),
        ]

        for item_sel, title_sel, price_sel in selectors:
            items = await page.query_selector_all(item_sel)
            if not items:
                continue

            for rank, item in enumerate(items[:50], start=1):
                try:
                    title_el = await item.query_selector(title_sel)
                    price_el = await item.query_selector(price_sel)
                    link_el = await item.query_selector("a[href]")

                    if not title_el:
                        continue

                    name = (await title_el.inner_text()).strip()
                    if not name or len(name) < 3:
                        continue

                    price = 0.0
                    if price_el:
                        price_text = (await price_el.inner_text()).strip()
                        price_text = price_text.replace("$", "").replace(",", "").split("-")[0].strip()
                        try:
                            price = float(price_text)
                        except ValueError:
                            pass

                    href = ""
                    if link_el:
                        href = await link_el.get_attribute("href") or ""
                        if href and not href.startswith("http"):
                            href = "https://www.amazon.com" + href

                    products.append({
                        "name": name,
                        "price": price,
                        "url": href,
                        "rank": rank,
                        "category": category,
                        "source": "amazon",
                    })
                except Exception:
                    continue

            if products:
                break  # Found products with this selector strategy

        return products

    def _scrape_google_shopping(self):
        """
        Fallback: scrape Google Shopping for trending/best seller products.
        Less data but no anti-bot issues.
        """
        products = []
        queries = [
            "best sellers electronics 2026",
            "trending home products 2026",
            "popular kitchen gadgets",
            "best selling fitness equipment",
            "trending beauty products",
            "popular pet products",
        ]

        for query in queries:
            try:
                url = f"https://www.google.com/search?tbm=shop&q={query.replace(' ', '+')}"
                soup = self.fetch_page(url)

                # Google Shopping result cards
                cards = soup.select("div.sh-dgr__content, div.sh-dlr__list-result")
                for rank, card in enumerate(cards[:10], start=1):
                    title_el = card.select_one("h3, h4, div.tAxDx, div.rgHvZc a")
                    price_el = card.select_one("span.a8Pemb, span.HRLxBb")

                    if not title_el:
                        continue

                    name = title_el.get_text(strip=True)
                    price = 0.0
                    if price_el:
                        pt = price_el.get_text(strip=True).replace("$", "").replace(",", "")
                        try:
                            price = float(pt)
                        except ValueError:
                            pass

                    products.append({
                        "name": name,
                        "price": price,
                        "url": "",
                        "rank": rank,
                        "category": query.split()[1] if len(query.split()) > 1 else "general",
                        "source": "google_shopping",
                    })

                logger.info(f"Google Shopping: {query} -> {len(cards)} results")
                random_delay(self.delay_min, self.delay_max)

            except Exception as e:
                logger.warning(f"Google Shopping failed for '{query}': {str(e)[:60]}")

        return products

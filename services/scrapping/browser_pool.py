import asyncio
from contextlib import asynccontextmanager
from typing import Dict, Optional

from playwright.async_api import Browser, BrowserContext, Playwright, async_playwright

from core.browser_config import BrowserConfig
from core.logging_config import get_logger

logger = get_logger(__name__)


class BrowserPool:
    """Manages a pool of browser instances for efficient scraping."""

    def __init__(
        self,
        max_browsers: int = BrowserConfig.MAX_BROWSERS,
        headless: bool = BrowserConfig.HEADLESS,
    ):
        self.max_browsers = max_browsers
        self.headless = headless
        self._browsers: Dict[int, Browser] = {}
        self._contexts: Dict[int, BrowserContext] = {}
        self._playwright: Optional[Playwright] = None
        self._lock = asyncio.Lock()
        self._semaphore = asyncio.Semaphore(max_browsers)

    async def initialize(self):
        """Initialize the browser pool."""
        if self._playwright is None:
            self._playwright = await async_playwright().start()
            logger.info("Browser pool initialized")

    async def cleanup(self):
        """Clean up all browser instances."""
        async with self._lock:
            for context in self._contexts.values():
                try:
                    await context.close()
                except Exception as e:
                    logger.error(f"Error closing context: {e}")

            for browser in self._browsers.values():
                try:
                    await browser.close()
                except Exception as e:
                    logger.error(f"Error closing browser: {e}")

            if self._playwright:
                try:
                    await self._playwright.stop()
                except Exception as e:
                    logger.error(f"Error stopping playwright: {e}")

            self._browsers.clear()
            self._contexts.clear()
            self._playwright = None
            logger.info("Browser pool cleaned up")

    @asynccontextmanager
    async def get_browser_context(self):
        """Get a browser context from the pool."""
        await self.initialize()

        async with self._semaphore:
            browser_id = None
            for bid, browser in self._browsers.items():
                if bid not in self._contexts:
                    browser_id = bid
                    break

            if browser_id is None and len(self._browsers) < self.max_browsers:
                browser_id = len(self._browsers) + 1
                if self._playwright:
                    self._browsers[browser_id] = await self._playwright.chromium.launch(
                        headless=self.headless,
                        args=BrowserConfig.get_browser_args(),
                    )

            if browser_id is None:
                while True:
                    for bid in self._browsers:
                        if bid not in self._contexts:
                            browser_id = bid
                            break
                    if browser_id is not None:
                        break
                    await asyncio.sleep(0.1)

            context = await self._browsers[browser_id].new_context(
                **BrowserConfig.get_context_options()
            )
            self._contexts[browser_id] = context

            try:
                yield context
            finally:
                try:
                    await context.close()
                except Exception as e:
                    logger.error(f"Error closing context: {e}")
                finally:
                    self._contexts.pop(browser_id, None)

    @asynccontextmanager
    async def get_page(self):
        """Get a page from the browser pool."""
        async with self.get_browser_context() as context:
            page = await context.new_page()
            try:
                yield page
            finally:
                try:
                    await page.close()
                except Exception as e:
                    logger.error(f"Error closing page: {e}")


# Global browser pool instance
_browser_pool: Optional[BrowserPool] = None


async def get_browser_pool() -> BrowserPool:
    """Get the global browser pool instance."""
    global _browser_pool
    if _browser_pool is None:
        _browser_pool = BrowserPool()
    return _browser_pool


async def cleanup_browser_pool():
    """Clean up the global browser pool."""
    global _browser_pool
    if _browser_pool:
        await _browser_pool.cleanup()
        _browser_pool = None

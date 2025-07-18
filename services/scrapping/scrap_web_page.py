from core.logging_config import get_logger
from services.scrapping.browser_pool import get_browser_pool

logger = get_logger(__name__)


async def scrap_page(url, max_retries=3):
    browser_pool = await get_browser_pool()

    for attempt in range(max_retries):
        try:
            async with browser_pool.get_page() as page:
                await page.goto(url)
                await page.wait_for_load_state("domcontentloaded")
                await page.wait_for_timeout(250)
                content = await page.inner_text("body")
                await page.close()
                return content
        except Exception as e:
            logger.error(f"Attempt {attempt + 1} failed: {e}")
            if attempt == max_retries - 1:
                raise

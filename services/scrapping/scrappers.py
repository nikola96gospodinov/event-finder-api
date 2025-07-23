import asyncio
from typing import Optional

from playwright.async_api import Page

from core.logging_config import get_logger

from .browser_pool import get_browser_pool

logger = get_logger(__name__)


class BaseEventScraper:
    """Base class for event scrapers with common functionality."""

    def __init__(self, base_url: str):
        self.base_url = base_url

    async def extract_event_urls(self, page, keyword: Optional[str] = None, **kwargs):
        """
        Extract URLs of events. To be implemented by subclasses.

        Args:
            page: Playwright page instance
            keyword: Search term to find relevant events
            **kwargs: Additional keyword arguments

        Returns:
            List of event URLs
        """
        raise NotImplementedError("Subclasses must implement extract_event_urls")

    async def scrape_events_by_keyword(self, keyword: Optional[str] = None, **kwargs):
        """
        Scrape event URLs for a single keyword using the browser pool.

        Args:
            keyword: Single keyword to search for
            **kwargs: Additional keyword arguments for extract_event_urls

        Returns:
            List of event URLs
        """
        browser_pool = await get_browser_pool()

        async with browser_pool.get_page() as page:
            events = await self.extract_event_urls(page, keyword=keyword, **kwargs)
            return events


class EventBriteScraper(BaseEventScraper):
    def __init__(self):
        super().__init__(base_url="https://www.eventbrite.com")

    async def extract_event_urls(
        self,
        page: Page,
        keyword="tech",
        country="United Kingdom",
        city="London",
        promoted_count=2,
        regular_count=3,
        **kwargs,
    ):
        """
        Extract URLs of events from Eventbrite,
        separately for promoted and non-promoted events.

        Args:
            page: Playwright page instance
            keyword: Single search term to find relevant events
            country: Country to search in
            city: City to search in
            promoted_count: Number of promoted events to extract
            regular_count: Number of regular (non-promoted) events to extract

        Returns:
            List of event URLs
        """
        formatted_country = country.lower().replace(" ", "-")
        formatted_city = city.lower().replace(" ", "-")
        formatted_keyword = keyword.lower().replace(" ", "-")

        search_url = (
            f"{self.base_url}/d/"
            f"{formatted_country}--{formatted_city}/"
            f"{formatted_keyword}"
        )
        logger.info(f"Navigating to: {search_url}")

        await page.goto(search_url)

        await page.wait_for_selector(
            'ul[class*="SearchResultPanelContentEventCardList-module__eventList"]',
            timeout=10_000,
        )

        await asyncio.sleep(1)

        for _ in range(2):
            await page.evaluate("window.scrollBy(0, 800)")
            await asyncio.sleep(1)

        events = []

        all_event_cards = await page.query_selector_all(
            'ul[class*="SearchResultPanelContentEventCardList-module__eventList"] li'
        )

        # Process promoted events
        count = 0
        for card in all_event_cards:
            if count >= promoted_count:
                break

            try:
                is_promoted = await card.query_selector('p:has-text("Promoted")')
                if not is_promoted:
                    continue

                link_element = await card.query_selector('a[href*="/e/"]')
                if not link_element:
                    continue

                event_url = await link_element.get_attribute("href")

                events.append(event_url)

                count += 1

            except Exception as e:
                logger.error(f"Error extracting promoted event: {e}")

        # Process regular events
        count = 0
        for card in all_event_cards:
            if count >= regular_count:
                break

            try:
                is_promoted = await card.query_selector('p:has-text("Promoted")')
                if is_promoted:
                    continue

                link_element = await card.query_selector('a[href*="/e/"]')
                if not link_element:
                    continue

                event_url = await link_element.get_attribute("href")

                events.append(event_url)

                count += 1

            except Exception as e:
                logger.error(f"Error extracting regular event: {e}")

        return events


class MeetupScraper(BaseEventScraper):
    def __init__(self):
        super().__init__(base_url="https://www.meetup.com")

    async def extract_event_urls(
        self,
        page: Page,
        keyword="tech",
        location="London",
        country_code="gb",
        max_events=5,
        **kwargs,
    ):
        """
        Extract URLs of events from Meetup.

        Args:
            page: Playwright page instance
            keyword: Single search term to find relevant events
            location: Location to search in (city, country)
            max_events: Maximum number of events to extract

        Returns:
            List of event URLs
        """
        # Build the search URL
        # Transform keywords by replacing spaces with %20 for URL encoding
        encoded_keyword = keyword.replace(" ", "%20")
        search_url = (
            f"{self.base_url}/find/"
            f"?keywords={encoded_keyword}"
            f"&location={country_code}--{location}"
            f"&source=EVENTS"
        )

        logger.info(f"Navigating to: {search_url}")
        await page.goto(search_url)

        # Wait for the events to load
        await page.wait_for_selector('a[href*="/events/"]', timeout=10_000)

        # Scroll to load more events
        for _ in range(3):
            await page.evaluate("window.scrollBy(0, 1000)")
            await asyncio.sleep(1)

        # Extract event links
        events = []
        event_cards = await page.query_selector_all('a[href*="/events/"]')

        for i, card in enumerate(event_cards):
            if i >= max_events:
                break

            try:
                event_url = await card.get_attribute("href")
                if event_url and "/events/" in event_url:
                    full_url = (
                        event_url
                        if event_url.startswith("http")
                        else f"{self.base_url}{event_url}"
                    )
                    events.append(full_url)
            except Exception as e:
                logger.error(f"Error extracting meetup URL: {e}")

        return events


class LumaScraper(BaseEventScraper):
    def __init__(self):
        super().__init__(base_url="https://lu.ma")

    async def extract_event_urls(
        self, page: Page, keyword: Optional[str] = None, **kwargs
    ):
        """
        Extract URLs of events from Luma.

        Args:
            page: Playwright page instance
            keyword: Search term (ignored for Luma)
            **kwargs: Keyword arguments including:
                location: Location to search in (city name)
                max_events: Maximum number of events to extract

        Returns:
            List of event URLs
        """
        location = kwargs.get("location", "london")
        max_events = kwargs.get("max_events", 25)

        search_url = f"{self.base_url}/{location}".lower()
        logger.info(f"Navigating to: {search_url}")

        await page.goto(search_url)

        await page.wait_for_selector(
            'a[class*="event-link content-link"]', timeout=10_000
        )

        for _ in range(3):
            await page.evaluate("window.scrollBy(0, 1000)")
            await asyncio.sleep(1)

        events = []
        event_cards = await page.query_selector_all(
            'a[class*="event-link content-link"]'
        )

        # Skip the first 5 events
        event_cards = event_cards[5:]

        for i, card in enumerate(event_cards):
            if i >= max_events:
                break

            event_url = await card.get_attribute("href")
            events.append(f"https://lu.ma/{event_url}")

        return events


async def get_event_links(
    search_keyword: str,
    eventbrite=True,
    meetup=True,
    luma=True,
    country="United Kingdom",
    city="London",
    country_code="gb",
) -> list[str]:
    tasks = []

    if eventbrite:
        eventbrite_scraper = EventBriteScraper()
        tasks.append(
            eventbrite_scraper.scrape_events_by_keyword(
                keyword=search_keyword, country=country, city=city
            )
        )

    if meetup:
        meetup_scraper = MeetupScraper()
        tasks.append(
            meetup_scraper.scrape_events_by_keyword(
                keyword=search_keyword, location=city, country_code=country_code
            )
        )

    if luma:
        luma_scraper = LumaScraper()
        tasks.append(
            luma_scraper.scrape_events_by_keyword(
                keyword=search_keyword, location=city, max_events=40
            )
        )

    results = await asyncio.gather(*tasks, return_exceptions=True)

    event_links = set()

    for result in results:
        if isinstance(result, Exception):
            logger.error(f"Scraper error: {result}")
            continue

        if isinstance(result, list):
            event_links.update(result)
        else:
            logger.error(f"Unexpected result type: {type(result)}")

    return list(event_links)

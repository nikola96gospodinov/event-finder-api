import asyncio
import json
import re
from typing import List, Optional

from playwright.async_api import (
    Browser,
    BrowserContext,
    Page,
    Playwright,
    async_playwright,
)

from core.browser_config import BrowserConfig
from core.config import settings
from core.logging_config import get_logger
from core.scrappey import get_html_from_scrappey

logger = get_logger(__name__)


class BaseEventScraper:
    """Base class for event scrapers with common functionality."""

    def __init__(self, base_url: str, browser: Optional[Browser] = None):
        self.base_url = base_url
        self.browser = browser
        self.playwright: Optional[Playwright] = None
        self.context: Optional[BrowserContext] = None
        self.page: Optional[Page] = None
        self._owns_browser = browser is None

    async def setup(self):
        """Initialize playwright browser."""
        if self.browser is None:
            self.playwright = await async_playwright().start()
            self.browser = await self.playwright.chromium.launch(
                headless=True, args=BrowserConfig.get_browser_args()
            )
            self._owns_browser = True

        self.context = await self.browser.new_context(
            **BrowserConfig.get_context_options()
        )
        self.page = await self.context.new_page()

    async def close(self):
        """Close browser and playwright."""
        if self.context:
            await self.context.close()

        if self._owns_browser and self.browser:
            await self.browser.close()

        if self._owns_browser and self.playwright:
            await self.playwright.stop()

    async def extract_event_urls(self, keyword: str, **kwargs):
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

    async def scrape_events_by_keywords(self, keywords: List[str], **kwargs):
        """
        Scrape event URLs for a single keyword using the browser pool.

        Args:
            keyword: Single keyword to search for
            **kwargs: Additional keyword arguments for extract_event_urls

        Returns:
            List of event URLs
        """
        await self.setup()
        all_events = []

        try:
            for keyword in keywords:
                events = await self.extract_event_urls(keyword=keyword, **kwargs)
                all_events.extend(events)
        finally:
            await self.close()

        # Remove duplicates while preserving order
        unique_events = list(dict.fromkeys(all_events))
        return unique_events


class EventBriteScraper(BaseEventScraper):
    def __init__(self, browser: Optional[Browser] = None):
        super().__init__(base_url="https://www.eventbrite.com", browser=browser)

    async def extract_event_urls(
        self,
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

        # Use Scrappey to get the HTML content in production
        if settings.ENVIRONMENT == "production":
            logger.info(f"Using Scrappey to get event links for: {search_url}")
            event_links = await self.extract_event_urls_from_scrappey(search_url)
            total_count = promoted_count + regular_count
            return event_links[:total_count]

        logger.info(f"Navigating to: {search_url}")

        assert self.page is not None, "Page not initialized"
        await self.page.goto(search_url)

        await self.page.wait_for_selector(
            'ul[class*="SearchResultPanelContentEventCardList-module__eventList"]',
            timeout=10_000,
        )

        await asyncio.sleep(1)

        for _ in range(2):
            await self.page.evaluate("window.scrollBy(0, 800)")
            await asyncio.sleep(1)

        events = []

        all_event_cards = await self.page.query_selector_all(
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

    async def extract_event_urls_from_scrappey(self, url: str):
        """
        Extract URLs of events from Eventbrite using Scrappey.
        """
        try:
            html_content = await get_html_from_scrappey(url)
        except Exception as e:
            logger.error(f"Error getting HTML from Scrappey for {url}: {e}")
            return []

        script_pattern = (
            r'<script type="application/ld\+json">\s*'
            r'(\{.*?"itemListElement".*?\})'
            r"\s*</script>"
        )

        script_matches = re.finditer(
            script_pattern, html_content, re.DOTALL | re.IGNORECASE
        )

        if not script_matches:
            logger.error(f"No script matches found for URL: {url}")
            return []

        all_links = []

        for script_match in script_matches:
            try:
                json_data = json.loads(script_match.group(1))

                if "itemListElement" in json_data and isinstance(
                    json_data["itemListElement"], list
                ):
                    for item in json_data["itemListElement"]:
                        if "item" in item and isinstance(item["item"], dict):
                            event = item["item"]

                            if "url" in event and event["url"]:
                                if event["url"] and event["url"] not in all_links:
                                    all_links.append(event["url"])
                            else:
                                logger.error(f"No url found in event: {event}")
                        else:
                            logger.error(f"No item found in event: {event}")
                else:
                    logger.error(f"No itemListElement found in HTML: {html_content}")

            except json.JSONDecodeError as e:
                print(f"Error parsing JSON-LD script: {e}")
                continue

        return all_links


class MeetupScraper(BaseEventScraper):
    def __init__(self, browser: Optional[Browser] = None):
        super().__init__(base_url="https://www.meetup.com", browser=browser)

    async def extract_event_urls(
        self,
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
        assert self.page is not None, "Page not initialized"
        await self.page.goto(search_url)

        # Wait for the events to load
        await self.page.wait_for_selector('a[href*="/events/"]', timeout=10_000)

        # Scroll to load more events
        for _ in range(3):
            await self.page.evaluate("window.scrollBy(0, 1000)")
            await asyncio.sleep(1)

        # Extract event links
        events = []
        event_cards = await self.page.query_selector_all('a[href*="/events/"]')

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
    def __init__(self, browser: Optional[Browser] = None):
        super().__init__(base_url="https://lu.ma", browser=browser)

    async def extract_event_urls(self, keyword: Optional[str] = None, **kwargs):
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

        assert self.page is not None, "Page not initialized"
        await self.page.goto(search_url)

        await self.page.wait_for_selector(
            'a[class*="event-link content-link"]', timeout=10_000
        )

        for _ in range(3):
            await self.page.evaluate("window.scrollBy(0, 1000)")
            await asyncio.sleep(1)

        events = []
        event_cards = await self.page.query_selector_all(
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

    async def scrape_events(self, keywords=None, location="london", max_events=50):
        """
        Override the base class method for Luma since we don't use keywords.

        Args:
            keywords: Ignored for Luma
            location: Location to search in
            max_events: Maximum number of events to extract

        Returns:
            List of event URLs
        """
        # Just use location directly - ignore keywords
        await self.setup()

        try:
            events = await self.extract_event_urls(
                location=location, max_events=max_events
            )
            return events
        finally:
            await self.close()


async def get_event_links(
    search_keywords: List[str],
    eventbrite=True,
    meetup=True,
    luma=True,
    country="United Kingdom",
    city="London",
    country_code="gb",
    browser: Optional[Browser] = None,
) -> list[str]:
    tasks = []

    if eventbrite:
        eventbrite_scraper = EventBriteScraper(browser=browser)
        tasks.append(
            eventbrite_scraper.scrape_events_by_keywords(
                keywords=search_keywords, country=country, city=city
            )
        )

    if meetup:
        meetup_scraper = MeetupScraper(browser=browser)
        tasks.append(
            meetup_scraper.scrape_events_by_keywords(
                keywords=search_keywords, location=city, country_code=country_code
            )
        )

    if luma:
        luma_scraper = LumaScraper(browser=browser)
        tasks.append(luma_scraper.scrape_events(location=city, max_events=40))

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

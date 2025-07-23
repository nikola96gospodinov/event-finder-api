from playwright.async_api import async_playwright

from core.llm import gemma_3_27b
from core.logging_config import get_logger
from models.user_profile_model import UserProfile
from services.email.send_email import post_message
from services.event_processing.check_event import check_event
from services.scrapping.scrappers import get_event_links
from services.search_words.get_search_words_for_event_sites import (
    get_search_keywords_for_event_sites,
)
from utils.email_utils import format_events_for_email
from utils.event_utils import (
    filter_events_by_relevance,
    remove_duplicates_based_on_title,
)

logger = get_logger(__name__)


async def agent(user_profile: UserProfile, only_highly_relevant: bool = False):
    search_keywords = get_search_keywords_for_event_sites(user_profile, gemma_3_27b)

    event_links = await get_event_links(
        search_keywords=search_keywords,
        luma=True,
        eventbrite=True,
        meetup=True,
        country=user_profile.location.country,
        country_code=user_profile.location.country_code,
        city=user_profile.location.city,
    )

    playwright = await async_playwright().start()
    browser = await playwright.chromium.launch(headless=True)

    events = []
    for event_link in event_links:
        try:
            event_details = await check_event(
                event_link, user_profile, gemma_3_27b, browser
            )
            if event_details is not None:
                events.append(event_details)
        except Exception as e:
            logger.error(f"Error checking event: {e}")

    events = sorted(events, key=lambda x: x.relevance, reverse=True)
    events = remove_duplicates_based_on_title(events)
    events = filter_events_by_relevance(events, only_highly_relevant)

    for event in events:
        logger.info(
            (
                f"Event: {event.event_details.title} - "
                f"Link: {event.event_url} - "
                f"Relevance: {event.relevance}\n"
            )
        )

    html = format_events_for_email(events, user_profile)
    post_message(
        user_profile.email,
        "test@test.com",
        "Events specifically picked for you! 🤩",
        html,
    )

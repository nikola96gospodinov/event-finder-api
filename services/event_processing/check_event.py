import json
from typing import Optional

from langchain_core.language_models.chat_models import BaseChatModel
from playwright.async_api import Browser

from core.logging_config import get_logger
from core.redis_client import redis_client
from models.event_model import EventDetails, EventResult
from models.user_profile_model import UserProfile
from services.event_processing.event_disqualifier import EventDisqualifier
from services.event_processing.event_relevance_calculator import (
    EventRelevanceCalculator,
)
from services.event_processing.extract_event_details import extract_event_details
from services.scrapping.scrap_web_page import scrap_page
from utils.event_utils import get_seconds_until_event

logger = get_logger(__name__)


async def check_event(
    event_link: str,
    user_profile: UserProfile,
    model: BaseChatModel,
    browser: Optional[Browser],
) -> EventResult | None:
    logger.info(f"Checking event: {event_link}")

    # Try to get cached result
    cache_key = f"event_details:{event_link}"
    cached_result = redis_client.get(cache_key)

    if cached_result is not None:
        logger.info("Retrieved event from cache:")
        event_details_dict = json.loads(str(cached_result))
        event_details = EventDetails(**event_details_dict)
        logger.info(event_details)
    else:
        webpage_content = await scrap_page(event_link, browser)
        temp_event_details = extract_event_details(webpage_content, model)

        if temp_event_details is None:
            logger.error("Something went wrong while extracting event details.")
            return None

        event_details = temp_event_details

        # Cache the event details
        redis_client.setex(
            cache_key,
            get_seconds_until_event(
                event_details.date_of_event, event_details.start_time
            ),
            json.dumps(event_details.model_dump()),
        )

    assert event_details is not None
    event_disqualifier = EventDisqualifier(user_profile)
    is_compatible = event_disqualifier.check_compatibility(event_details)

    if is_compatible:
        event_relevance_calculator = EventRelevanceCalculator(model, user_profile)
        event_relevance_score = (
            event_relevance_calculator.calculate_event_relevance_score(
                webpage_content, event_details
            )
        )
        logger.info(f"Event relevance score: {event_relevance_score}")
        result = EventResult(
            event_details=event_details,
            event_url=event_link,
            relevance=event_relevance_score,
        )

        return result
    else:
        logger.info(
            "Event is not compatible with the user's profile and/or preferences."
        )
        return None

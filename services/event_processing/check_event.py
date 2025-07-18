import json

from langchain_core.language_models.chat_models import BaseChatModel

from core.logging_config import get_logger
from core.redis_client import redis_client
from models.event_model import EventResult
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
    event_disqualifier: EventDisqualifier,
    event_relevance_calculator: EventRelevanceCalculator,
    model: BaseChatModel,
) -> EventResult | None:
    logger.info(f"Checking event: {event_link}")

    # Try to get cached result
    cache_key = f"event_details:{event_link}"
    cached_result = redis_client.get(cache_key)

    webpage_content = await scrap_page(event_link)

    if cached_result is not None:
        logger.info("Retrieved event from cache:")
        event_details = json.loads(str(cached_result))
        logger.info(event_details)
    else:
        event_details = extract_event_details(webpage_content, model)

        if event_details is None:
            logger.error("Something went wrong while extracting event details.")
            return None
        else:
            redis_client.setex(
                cache_key,
                get_seconds_until_event(
                    event_details["date_of_event"], event_details["start_time"]
                ),
                json.dumps(event_details),
            )

    is_compatible = event_disqualifier.check_compatibility(event_details)

    if is_compatible:
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

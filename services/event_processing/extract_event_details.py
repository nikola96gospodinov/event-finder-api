import ast
import re
from datetime import datetime

from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.prompts import ChatPromptTemplate

from core.logging_config import get_logger
from schemas.bias_options import (
    event_format_options,
    gender_bias_options,
    relationship_status_bias_options,
    sexual_orientation_bias_options,
)
from schemas.event_model import EventDetails
from utils.address_utils import get_location_from_query
from utils.request_utils import retry_with_backoff

logger = get_logger(__name__)


def extract_event_details(
    webpage_content: str | None, model: BaseChatModel
) -> EventDetails | None:
    if webpage_content is None:
        return None

    extract_details_template = """
        The web page content is as follows:
        {webpage_content}

        Extract the details of the event from the web page.
        The details that are needed are:
        - Title of the event
        - Age range - return the age range in the following format: {{"min_age": 20, "max_age": 30}}.
            * If the age range is not mentioned, then return None.
            * If either the min_age or max_age is not mentioned, then return None for that value.
            * "18+" indicates a minimum age of 18 but no maximum age ({{"min_age": 18, "max_age": None}}).
            * "18-26" indicates a minimum age of 18 and a maximum age of 26 ({{"min_age": 18, "max_age": 26}}).
            * "Under 35s" or "U35" indicates a maximum age of 35 and no minimum age ({{"min_age": None, "max_age": 35}}).
            * "20s and 30s" indicate a minimum age of 20 and a maximum age of 39 ({{"min_age": 20, "max_age": 39}}).
        - Gender bias - return a list of gender bias options. The options are: {gender_bias_options}. For example it could be ["female", "male", "non-binary"] or just ["female"]. If there are no gender biases, then it should be None.
            * The event explicitly states it's for a specific gender
            * The event description uses gendered language throughout (e.g., "ladies", "sisterhood", "brotherhood")
            * The event focuses on experiences unique to a specific gender
            * The event is hosted by a gender-specific organization (e.g., "Women in Tech")
            * Marketing materials exclusively show one gender
            * The event addresses topics that are explicitly framed as gender-specific
        - Sexual orientation bias returns a list of options. The options are: {sexual_orientation_bias_options} - for example if the event is tailored to LGBTQ+ only, then the sexual orientation bias should be ["lesbian", "gay", "bisexual", "transgender"]. If there are no sexual orientation bias, then it should be None
        - Relationship status bias returns a list of options. The options are: {relationship_status_bias_options} - for example if the event is tailored to singles only, then the relationship status bias should be ["single"]. If there are no relationship status bias, then it should be None. Party nights and speed dating events are generally tailored to singles.
        - Date of the event - this should be in the following format: "DD-MM-YYYY". If the year of the event is not mentioned, then assume it's the current year - {current_year}. If there are multiple dates, then return the most relevant but never multiple dates. For example "14-01-2025 to 14-06-2025" should be "14-01-2025"
        - Start time of the event - this should be in the following format: "10:00", "22:00". Note that the time could be represented in many different ways on the page. 6, 6:00pm, 18:00 etc. but we need to extract the time in 24 hour format.
        - End time of the event - this should be in the following format: "10:00", "22:00". Note that the time could be represented in many different ways on the page. 6, 6:00pm, 18:00 etc. but we need to extract the time in 24 hour format.
        - Location of the event - be as specific as possible. For example, "123 Main St, EC1A 1BB, London, UK" is more specific than "London, UK". If the street is not mentioned, then the postcode is the most important thing. If it says TBC, then return None for the location. IMPORTANT: The location must be returned as a dictionary with a "full_address" field, not as a plain string.
        - Price of the event - just put the number like 20, 50, 100, etc. in either float or int format without the currency symbol. If an event is free, then the price should be 0 instead of None
        - Event format returns a list of of options. The options are: {event_format_options} - This tells us whether the event is online, in person or both. Mentions of Zoom, Online, Virtual, etc. should be considered online unless it's a combination of in person and online, in which case it should be ["offline", "online"].
        - Whether the event is sold out or out of spaces. Note that "Sales ending soon", "Sales end soon", "Limited spaces left", "Limited availability", "Limited availability left", or similar phrases are not a sign of a sold out event and details should be extracted.

        The response should be None if there is something to indicate so, or a Python dictionary:
        Example:
        {{
            "title": "Event Title",
            "age_range": {{"min_age": 20, "max_age": 30}},
            "gender_bias": ["female],
            "sexual_orientation_bias": ["lesbian", "gay", "bisexual", "transgender"],
            "relationship_status_bias": "singles only",
            "date_of_event": "06-01-2025",
            "start_time": "10:00",
            "end_time": "12:00",
            "location_of_event": {{
                "full_address": "123 Main St, EC1A 1BB, London, UK"
            }},
            "price_of_event": "20",
            "event_format": ["offline"],
            "is_sold_out": False
        }}

        CRITICAL: The location_of_event field MUST be a dictionary with a "full_address" key, never a plain string.
        Don't do any formatting. Just return the Python dictionary as plain text. Under any circumstances, don't use ```python or ``` in the response.
        Under any circumstances, don't return JSON and make sure the response is a valid Python dictionary. This is crucial. If the location is not mentioned, then return None for the location.

        If there is no information about a particular detail, return None for that detail.
    """

    event_details_prompt = ChatPromptTemplate.from_template(extract_details_template)
    event_details_chain = event_details_prompt | model

    result = retry_with_backoff(
        event_details_chain.invoke,
        max_retries=5,
        base_delay=2.0,
        input={
            "webpage_content": webpage_content,
            "current_year": datetime.now().year,
            "gender_bias_options": gender_bias_options,
            "sexual_orientation_bias_options": sexual_orientation_bias_options,
            "relationship_status_bias_options": relationship_status_bias_options,
            "event_format_options": event_format_options,
        },
    )

    response_str = str(result.content) if hasattr(result, "content") else str(result)

    event_details = str(response_str)
    og_event_details = event_details  # Store the original event details for debugging

    # Sometimes the model doesn't play along so we need to extract the dictionary from the response if there is more to the response than just the dictionary
    event_details = event_details.strip()
    dict_pattern = r"\{.*\}"
    dict_match = re.search(dict_pattern, event_details, re.DOTALL)
    if dict_match:
        event_details = dict_match.group(0)

    if event_details.lower() == "none":
        return None

    try:
        event_details_dict = ast.literal_eval(event_details)

        if isinstance(event_details_dict.get("location_of_event"), str):
            location_string = event_details_dict["location_of_event"]
            event_details_dict["location_of_event"] = {"full_address": location_string}

        event_details_result: EventDetails | None = EventDetails(**event_details_dict)
    except (SyntaxError, ValueError) as e:
        logger.error(f"Error parsing event details: {e}")
        logger.error(f"Original event details: {og_event_details}")
        logger.error(f"Raw event details: {event_details}")
        return None
    except Exception as e:
        logger.error(f"Error creating EventDetails object: {e}")
        logger.error(f"Processed event details dict: {event_details_dict}")
        logger.error(f"Original event details: {og_event_details}")
        return None

    if (
        event_details_result
        and event_details_result.location_of_event
        and event_details_result.location_of_event.full_address
    ):
        coordinates = get_location_from_query(
            event_details_result.location_of_event.full_address
        )
        if (
            coordinates
            and coordinates.latitude is not None
            and coordinates.longitude is not None
        ):
            event_details_result.location_of_event.latitude = coordinates.latitude
            event_details_result.location_of_event.longitude = coordinates.longitude
        else:
            event_details_result.location_of_event.full_address = None

    logger.info("Event details:")
    logger.info(event_details_result)

    return event_details_result

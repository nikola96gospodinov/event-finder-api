import json
from datetime import datetime
from typing import Any, Dict, Optional

from core.logging_config import get_logger
from models.user_profile_model import (
    AcceptableTimes,
    DistanceThreshold,
    Location,
    StartEndTime,
    UserProfile,
)
from utils.address_utils import get_location_from_postcode
from utils.date_utils import time_to_string

logger = get_logger(__name__)


def convert_from_supabase_user_to_user_profile(
    profile_data: Dict[str, Any], user_data: Optional[Dict[str, Any]] = None
) -> UserProfile | None:
    """Convert database profile data to UserProfile model"""
    try:
        birthday = profile_data.get("birthday")
        if isinstance(birthday, str):
            birth_date = datetime.fromisoformat(birthday)
        elif birthday and hasattr(birthday, "date"):  # If it's a date object
            birth_date = datetime.combine(birthday, datetime.min.time())
        else:
            birth_date = datetime(1995, 1, 1)  # Default fallback

        weekday_start = profile_data.get("weekday_start_time")
        weekday_end = profile_data.get("weekday_end_time")
        weekend_start = profile_data.get("weekend_start_time")
        weekend_end = profile_data.get("weekend_end_time")

        acceptable_times = AcceptableTimes(
            weekdays=StartEndTime(
                start=time_to_string(weekday_start) or "17:00",
                end=time_to_string(weekday_end) or "22:00",
            ),
            weekends=StartEndTime(
                start=time_to_string(weekend_start) or "8:00",
                end=time_to_string(weekend_end) or "23:00",
            ),
        )

        distance_threshold = DistanceThreshold(
            distance_threshold=profile_data.get("distance_threshold_value", 20),
            unit=profile_data.get("distance_threshold_unit", "miles"),
        )

        location = get_location_from_postcode(profile_data.get("postcode")) or Location(
            latitude=0, longitude=0, country="", city="", country_code=""
        )

        budget_value = profile_data.get("budget", 0)
        willingness_to_pay = budget_value > 0

        time_commitment_in_minutes = profile_data.get("time_commitment_in_minutes", 240)

        email = user_data.get("email") if user_data else ""

        willingness_for_online = profile_data.get("willingness_for_online") or False

        return UserProfile(
            birth_date=birth_date,
            gender=profile_data.get("gender", "male"),
            sexual_orientation=profile_data.get("sexual_orientation", "straight"),
            relationship_status=profile_data.get("relationship_status", "single"),
            willingness_to_pay=willingness_to_pay,
            budget=budget_value,
            willingness_for_online=willingness_for_online,
            acceptable_times=acceptable_times,
            location=location,
            distance_threshold=distance_threshold,
            time_commitment_in_minutes=time_commitment_in_minutes,
            interests=profile_data.get("interests", []),
            goals=profile_data.get("goals", []),
            occupation=profile_data.get("occupation", ""),
            email=email or "",
        )

    except Exception as e:
        logger.error(f"Error converting profile data: {e}")
        return None


def serialize_user_profile(user_profile: UserProfile) -> str:
    """Serialize user profile to JSON, handling datetime fields properly."""
    profile_dict = user_profile.model_dump()

    if "birth_date" in profile_dict and isinstance(
        profile_dict["birth_date"], datetime
    ):
        profile_dict["birth_date"] = profile_dict["birth_date"].isoformat()

    return json.dumps(profile_dict)


def convert_from_json_to_user_profile(
    json_data: str,
) -> UserProfile | None:
    """Convert JSON data to UserProfile model"""
    try:
        profile_dict = json.loads(json_data)
        if "birth_date" in profile_dict and isinstance(profile_dict["birth_date"], str):
            profile_dict["birth_date"] = datetime.fromisoformat(
                profile_dict["birth_date"]
            )
        return UserProfile(**profile_dict)
    except Exception as e:
        logger.error(f"Error converting JSON to user profile: {e}")
        return None

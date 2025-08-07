import math
import re
from urllib.parse import quote

import httpx

from core.logging_config import get_logger
from schemas.coordinates_model import Coordinates
from schemas.user_profile_model import DistanceUnit, Location

logger = get_logger(__name__)


def extract_postcode_from_address(address: str) -> str | None:
    postcode_pattern = r"\b[A-Z]{1,2}\d[A-Z\d]?\s?\d[A-Z]{2}\b"
    match = re.search(postcode_pattern, address)
    return match.group(0) if match else None


def get_location_from_postcode(postcode: str | None) -> Location | None:
    if postcode is None:
        return None

    url = (
        f"https://nominatim.openstreetmap.org/search"
        f"?q={quote(postcode)}&format=json"
        f"&polygon_kml=1&addressdetails=1"
    )
    headers = {
        # Required by Nominatim's usage policy
        "User-Agent": "EventDisqualifierApp/1.0",
    }
    try:
        result = httpx.get(url=url, headers=headers)
        if result.text.strip():
            result_json = result.json()
            if result_json and len(result_json) > 0:
                return Location(
                    latitude=float(result_json[0]["lat"]),
                    longitude=float(result_json[0]["lon"]),
                    country=result_json[0]["address"]["country"],
                    city=result_json[0]["address"]["city"],
                    country_code=result_json[0]["address"]["country_code"],
                    area=result_json[0]["address"]["suburb"]
                    or result_json[0]["address"]["district"],
                )
        else:
            logger.info("Empty response received")
        return None
    except Exception as e:
        logger.error(f"Error getting address coordinates: {e}")
        logger.error(f"Error type: {type(e)}")
        return None


def calculate_distance(
    loc1: Coordinates, loc2: Coordinates, distance_unit: DistanceUnit
) -> float:
    """
    Calculate the distance between two locations using the Haversine formula.
    Returns the distance in kilometers.
    """
    # Earth's radius in kilometers
    R = 6371.0

    lat1 = loc1.latitude
    lon1 = loc1.longitude
    lat2 = loc2.latitude
    lon2 = loc2.longitude

    if None in (lat1, lon1, lat2, lon2):
        return float("inf")

    assert (
        lat1 is not None and lon1 is not None and lat2 is not None and lon2 is not None
    )

    lat1_rad = math.radians(lat1)
    lon1_rad = math.radians(lon1)
    lat2_rad = math.radians(lat2)
    lon2_rad = math.radians(lon2)

    # Difference in coordinates
    dlat = lat2_rad - lat1_rad
    dlon = lon2_rad - lon1_rad

    # Haversine formula
    a = (
        math.sin(dlat / 2) ** 2
        + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon / 2) ** 2
    )
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    distance = R * c

    if distance_unit == "km":
        return distance
    else:
        return distance * 0.621371

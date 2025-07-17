from typing import Literal, TypedDict

from models.bias_options import (
    event_format_options,
    gender_bias_options,
    relationship_status_bias_options,
    sexual_orientation_bias_options,
)
from models.coordinates_model import Coordinates


class LocationOfEvent(Coordinates):
    full_address: str | None


class AgeRange(TypedDict):
    min_age: int | None
    max_age: int | None


class EventDetails(TypedDict):
    title: str
    age_range: AgeRange | None
    gender_bias: list[gender_bias_options] | None
    sexual_orientation_bias: list[sexual_orientation_bias_options] | None
    relationship_status_bias: list[relationship_status_bias_options] | None
    date_of_event: str | None
    start_time: str | None
    end_time: str | None
    location_of_event: LocationOfEvent
    price_of_event: float | int
    event_format: Literal[event_format_options] | None
    is_sold_out: bool | None


class EventResult(TypedDict):
    event_details: EventDetails
    event_url: str
    relevance: float

from typing import Literal, Optional, Union

from pydantic import BaseModel

from models.bias_options import (
    event_format_options,
    gender_bias_options,
    relationship_status_bias_options,
    sexual_orientation_bias_options,
)
from models.coordinates_model import Coordinates


class LocationOfEvent(Coordinates):
    full_address: Optional[str] = None


class AgeRange(BaseModel):
    min_age: Optional[int] = None
    max_age: Optional[int] = None


class EventDetails(BaseModel):
    title: str
    age_range: Optional[AgeRange] = None
    gender_bias: Optional[list[gender_bias_options]] = None
    sexual_orientation_bias: Optional[list[sexual_orientation_bias_options]] = None
    relationship_status_bias: Optional[list[relationship_status_bias_options]] = None
    date_of_event: Optional[str] = None
    start_time: Optional[str] = None
    end_time: Optional[str] = None
    location_of_event: LocationOfEvent
    price_of_event: Union[float, int]
    event_format: Optional[list[Literal[event_format_options]]] = None
    is_sold_out: Optional[bool] = None


class EventResult(BaseModel):
    event_details: EventDetails
    event_url: str
    relevance: float

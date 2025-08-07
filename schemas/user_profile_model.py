from datetime import datetime
from typing import Literal, Optional

from pydantic import BaseModel, Field

from schemas.bias_options import (
    gender_bias_options,
    relationship_status_bias_options,
    sexual_orientation_bias_options,
)
from schemas.coordinates_model import Coordinates

DistanceUnit = Literal["km", "miles"]


class DistanceThreshold(BaseModel):
    distance_threshold: int = Field(..., ge=0, description="Distance threshold value")
    unit: DistanceUnit = Field(..., description="Distance unit (km or miles)")


class Location(Coordinates):
    country: Optional[str] = Field(None, description="Country")
    city: Optional[str] = Field(None, description="City")
    country_code: Optional[str] = Field(None, description="Country code")


class StartEndTime(BaseModel):
    start: Optional[str] = Field(None, description="Start time in HH:MM format")
    end: Optional[str] = Field(None, description="End time in HH:MM format")


class AcceptableTimes(BaseModel):
    weekdays: StartEndTime = Field(..., description="Acceptable times for weekdays")
    weekends: StartEndTime = Field(..., description="Acceptable times for weekends")


class UserProfile(BaseModel):
    interests: list[str] = Field(..., description="List of user interests")
    goals: list[str] = Field(..., description="List of user goals")
    occupation: str = Field(..., description="User's occupation")
    email: str = Field(..., description="User's email address")
    birth_date: datetime = Field(..., description="User's birth date")
    gender: gender_bias_options = Field(..., description="User's gender")
    sexual_orientation: sexual_orientation_bias_options = Field(
        ..., description="User's sexual orientation"
    )
    relationship_status: relationship_status_bias_options = Field(
        ..., description="User's relationship status"
    )
    willingness_to_pay: bool = Field(
        ..., description="Whether user is willing to pay for events"
    )
    budget: Literal[0, 10, 20, 50, 100, 200, 500, 1000] = Field(
        ..., description="User's budget for events"
    )
    willingness_for_online: bool = Field(
        ..., description="Whether user is willing to attend online events"
    )
    acceptable_times: AcceptableTimes = Field(
        ..., description="User's acceptable times for events"
    )
    location: Location = Field(..., description="User's location")
    distance_threshold: DistanceThreshold = Field(
        ..., description="User's distance threshold for events"
    )
    time_commitment_in_minutes: int = Field(
        ..., ge=0, le=1440, description="User's time commitment in minutes"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "interests": ["technology", "hiking", "cooking"],
                "goals": ["make new friends", "learn new skills"],
                "occupation": "Software Engineer",
                "email": "user@example.com",
                "birth_date": "1990-01-01T00:00:00",
                "gender": "male",
                "sexual_orientation": "straight",
                "relationship_status": "single",
                "willingness_to_pay": True,
                "budget": 50,
                "willingness_for_online": False,
                "acceptable_times": {
                    "weekdays": {"start": "18:00", "end": "22:00"},
                    "weekends": {"start": "10:00", "end": "23:00"},
                },
                "location": {"latitude": 40.7128, "longitude": -74.0060},
                "distance_threshold": {"distance_threshold": 25, "unit": "km"},
                "time_commitment_in_minutes": 120,
            }
        }

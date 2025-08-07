from typing import Optional

from pydantic import BaseModel, Field


class Coordinates(BaseModel):
    latitude: Optional[float] = Field(
        None, ge=-90, le=90, description="Latitude coordinate"
    )
    longitude: Optional[float] = Field(
        None, ge=-180, le=180, description="Longitude coordinate"
    )

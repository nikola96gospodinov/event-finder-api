from pydantic import BaseModel

from models.user_profile_model import Location

from .common import ErrorResponse


class AddressDetailsResponse(BaseModel):
    """Response model for get address details endpoint"""

    location: Location | None


__all__ = ["AddressDetailsResponse", "ErrorResponse"]

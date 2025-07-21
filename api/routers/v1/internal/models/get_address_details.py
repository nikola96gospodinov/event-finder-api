from pydantic import BaseModel

from api.routers.v1.models.common import ErrorResponse
from models.user_profile_model import Location


class AddressDetailsResponse(BaseModel):
    """Response model for get address details endpoint"""

    location: Location | None


__all__ = ["AddressDetailsResponse", "ErrorResponse"]

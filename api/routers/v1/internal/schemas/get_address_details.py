from pydantic import BaseModel

from api.routers.v1.schemas.common import ErrorResponse
from schemas.user_profile_model import Location


class AddressDetailsResponse(BaseModel):
    """Response model for get address details endpoint"""

    location: Location | None


__all__ = ["AddressDetailsResponse", "ErrorResponse"]

from pydantic import BaseModel

from api.routers.v1.models.common import ErrorResponse
from models.event_model import EventResult


class PostCheckEventResponse(BaseModel):
    """Response model for search keywords endpoint"""

    event_result: EventResult | None


__all__ = ["PostCheckEventResponse", "ErrorResponse"]

from pydantic import BaseModel

from api.routers.v1.schemas.common import ErrorResponse
from schemas.event_model import EventResult


class PostCheckEventResponse(BaseModel):
    """Response model for search keywords endpoint"""

    event_result: EventResult | None


__all__ = ["PostCheckEventResponse", "ErrorResponse"]

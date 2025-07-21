from pydantic import BaseModel

from models.event_model import EventResult

from .common import ErrorResponse


class PostCheckEventResponse(BaseModel):
    """Response model for search keywords endpoint"""

    event_result: EventResult | None


__all__ = ["PostCheckEventResponse", "ErrorResponse"]

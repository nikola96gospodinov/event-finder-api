from typing import List

from pydantic import BaseModel

from .common import ErrorResponse


class EventLinksResponse(BaseModel):
    """Response model for get event links endpoint"""

    event_links: List[str]


__all__ = ["EventLinksResponse", "ErrorResponse"]

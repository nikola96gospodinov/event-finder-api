from typing import List

from pydantic import BaseModel

from api.routers.v1.models.common import ErrorResponse


class SearchKeywordsResponse(BaseModel):
    """Response model for search keywords endpoint"""

    keywords: List[str]


__all__ = ["SearchKeywordsResponse", "ErrorResponse"]

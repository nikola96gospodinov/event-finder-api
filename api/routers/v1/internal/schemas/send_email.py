from pydantic import BaseModel

from api.routers.v1.schemas.common import ErrorResponse


class SendEmailResponse(BaseModel):
    """Response model for search keywords endpoint"""

    message: str


__all__ = ["SendEmailResponse", "ErrorResponse"]

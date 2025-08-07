from pydantic import BaseModel


class ErrorResponse(BaseModel):
    """Common error response model"""

    detail: str

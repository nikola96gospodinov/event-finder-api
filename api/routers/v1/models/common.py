from pydantic import BaseModel


class ErrorResponse(BaseModel):
    """Common error response model"""

    detail: str


class SuccessResponse(BaseModel):
    """Common success response model"""

    message: str

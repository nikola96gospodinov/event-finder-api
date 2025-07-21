from pydantic import BaseModel

from api.routers.v1.models.common import ErrorResponse


class PostRunAgentResponse(BaseModel):
    """Response model for run agent endpoint"""

    task_id: int
    status: str


__all__ = ["PostRunAgentResponse", "ErrorResponse"]

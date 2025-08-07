from fastapi import APIRouter, HTTPException

from core.llm import gemma_3_27b
from schemas.user_profile_model import UserProfile
from services.event_processing.check_event import check_event as check_event_service

from ..schemas.post_check_event import ErrorResponse, PostCheckEventResponse

router = APIRouter()


@router.post(
    "/check-event",
    response_model=PostCheckEventResponse,
    responses={
        400: {"model": ErrorResponse, "description": "Bad Request"},
        500: {"model": ErrorResponse, "description": "Internal Server Error"},
    },
)
async def check_event(event_link: str, user_profile: UserProfile):
    try:
        event_result = await check_event_service(event_link, user_profile, gemma_3_27b)
        return PostCheckEventResponse(event_result=event_result)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to check event: {str(e)}")

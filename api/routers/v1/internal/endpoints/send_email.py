from fastapi import APIRouter, HTTPException

from models.event_model import EventResult
from models.user_profile_model import UserProfile
from services.email.send_email import post_message
from utils.email_utils import format_events_for_email

from ..models.send_email import ErrorResponse, SendEmailResponse

router = APIRouter()


@router.post(
    "/send-email",
    response_model=SendEmailResponse,
    responses={
        400: {"model": ErrorResponse, "description": "Bad Request"},
        500: {"model": ErrorResponse, "description": "Internal Server Error"},
    },
)
async def send_email(events: list[EventResult], user_profile: UserProfile):
    try:
        html = format_events_for_email(events, user_profile)
        post_message(
            user_profile.email,
            "Events specifically picked for you! 🤩",
            html,
        )
        return SendEmailResponse(message="Email sent successfully")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to send email: {str(e)}")

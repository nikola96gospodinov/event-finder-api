from fastapi import APIRouter, Depends, HTTPException, Query

from models.user_profile_model import UserProfile
from services.auth.supabase_auth import get_current_user, get_current_user_profile
from services.runs.user_runs_service import user_run_service

from ..models.post_run_agent import ErrorResponse, PostRunAgentResponse

router = APIRouter()


@router.post(
    "/run-agent",
    response_model=PostRunAgentResponse,
    responses={
        400: {"model": ErrorResponse, "description": "Bad Request"},
        429: {"model": ErrorResponse, "description": "Too Many Requests"},
        500: {"model": ErrorResponse, "description": "Internal Server Error"},
    },
)
async def run_agent(
    only_highly_relevant: bool = Query(
        False, description="Event only highly relevant to the user or not"
    ),
    user: dict = Depends(get_current_user),
    user_profile: UserProfile = Depends(get_current_user_profile),
):
    """Run agent endpoint"""
    try:
        user_id = user.get("id")
        if not user_id:
            raise ValueError("User ID not found in token")

        can_run = await user_run_service.check_user_run_limit(user_id)
        if not can_run:
            raise HTTPException(
                status_code=429,
                detail=(
                    "Monthly run limit exceeded. "
                    "You can only run the agent 2 times per calendar month."
                ),
            )

        # TODO: The run should be recorded after it's been successful
        # but for now we'll record it before the agent runs
        run_recorded = await user_run_service.record_user_run(user_id)
        if not run_recorded:
            raise HTTPException(
                status_code=500, detail="Failed to record run. Please try again."
            )

        # TODO: Create a task to run the agent
        return PostRunAgentResponse(task_id=1, status="Task submitted")

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except HTTPException as e:
        raise HTTPException(status_code=429, detail=f"Too Many Requests: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to run agent: {str(e)}")

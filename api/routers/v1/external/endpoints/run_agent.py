from fastapi import APIRouter, Depends, HTTPException, Query

from schemas.user_profile_model import UserProfile
from services.auth.supabase_auth import get_current_user, get_current_user_profile
from services.cloud_run_jobs import cloud_run_service
from services.runs.user_runs_service import user_run_service
from utils.user_profile_utils import serialize_user_profile

from ..schemas.post_run_agent import ErrorResponse, PostRunAgentResponse

router = APIRouter()


@router.post(
    "/run-agent",
    response_model=PostRunAgentResponse,
    responses={
        400: {"model": ErrorResponse, "description": "Bad Request"},
        401: {"model": ErrorResponse, "description": "Unauthorized"},
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
    print(user_profile)
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

        try:
            parameters = {
                "only_highly_relevant": str(only_highly_relevant),
                "user_profile": serialize_user_profile(user_profile),
                "user_id": user_id,
            }

            task_id = await cloud_run_service.execute_job(parameters=parameters)

            return PostRunAgentResponse(
                task_id=task_id, status="Task submitted to Cloud Run Jobs successfully"
            )
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to submit job to Cloud Run Jobs: {str(e)}",
            )

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except HTTPException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to run agent: {str(e)}")

from typing import Dict

from fastapi import APIRouter

from .endpoints.run_agent import router as run_agent_router

router = APIRouter()

router.include_router(run_agent_router)


@router.get("/")
def get_external_info() -> Dict[str, str]:
    """Get external API information"""
    return {"message": "External API v1", "access": "public"}

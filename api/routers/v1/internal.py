from typing import Dict

from fastapi import APIRouter

from .endpoints.search import router as search_router

router = APIRouter()

router.include_router(search_router)


@router.get("/")
def get_internal_info() -> Dict[str, str]:
    """Get internal API information"""
    return {"message": "Internal API v1", "access": "internal"}

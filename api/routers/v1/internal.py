from typing import Dict

from fastapi import APIRouter

from .endpoints.get_address_details import router as get_address_details_router
from .endpoints.get_event_links import router as get_event_links_router
from .endpoints.get_search_keywords import router as get_search_keywords_router

router = APIRouter()

router.include_router(get_search_keywords_router)
router.include_router(get_event_links_router)
router.include_router(get_address_details_router)


@router.get("/")
def get_internal_info() -> Dict[str, str]:
    """Get internal API information"""
    return {"message": "Internal API v1", "access": "internal"}

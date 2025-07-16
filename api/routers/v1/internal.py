from typing import Dict

from fastapi import APIRouter

router = APIRouter()


@router.get("/")
def get_internal_info() -> Dict[str, str]:
    """Get internal API information"""
    return {"message": "Internal API v1", "access": "internal"}


@router.get("/search-keywords")
def get_search_keywords() -> Dict[str, str]:
    """Get search keywords"""
    return {"message": "Internal API v1", "access": "internal"}

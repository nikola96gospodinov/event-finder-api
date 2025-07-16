from typing import Dict

from fastapi import APIRouter

router = APIRouter()


@router.get("/")
def get_internal_info() -> Dict[str, str]:
    """Get internal API information"""
    return {"message": "Internal API v1", "access": "internal"}

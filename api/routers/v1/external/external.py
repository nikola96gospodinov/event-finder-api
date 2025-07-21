from typing import Dict

from fastapi import APIRouter

router = APIRouter()


@router.get("/")
def get_external_info() -> Dict[str, str]:
    """Get external API information"""
    return {"message": "External API v1", "access": "public"}

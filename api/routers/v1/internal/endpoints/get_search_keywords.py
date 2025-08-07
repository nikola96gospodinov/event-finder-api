from fastapi import APIRouter, HTTPException

from core.llm import gemma_3_27b
from schemas.user_profile_model import UserProfile
from services.search_words.get_search_words_for_event_sites import (
    get_search_keywords_for_event_sites,
)

from ..schemas.get_search_keywords import ErrorResponse, SearchKeywordsResponse

router = APIRouter()


@router.post(
    "/search-keywords",
    response_model=SearchKeywordsResponse,
    responses={
        400: {"model": ErrorResponse, "description": "Bad Request"},
        500: {"model": ErrorResponse, "description": "Internal Server Error"},
    },
)
def get_search_keywords(user_profile: UserProfile) -> SearchKeywordsResponse:
    """Get search keywords based on user profile"""
    try:
        keywords = get_search_keywords_for_event_sites(user_profile, gemma_3_27b)
        return SearchKeywordsResponse(keywords=keywords)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception:
        raise HTTPException(
            status_code=500, detail="Failed to generate search keywords"
        )

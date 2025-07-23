from typing import List

from fastapi import APIRouter, HTTPException

from services.scrapping.scrappers import get_event_links as get_event_links_service

from ..models.get_event_links import ErrorResponse, EventLinksResponse

router = APIRouter()


@router.post(
    "/event-links",
    response_model=EventLinksResponse,
    responses={
        400: {"model": ErrorResponse, "description": "Bad Request"},
        500: {"model": ErrorResponse, "description": "Internal Server Error"},
    },
)
async def get_event_links(
    keywords: List[str],
    eventbrite: bool = True,
    meetup: bool = True,
    luma: bool = True,
    country: str = "United Kingdom",
    city: str = "London",
    country_code: str = "gb",
) -> EventLinksResponse:
    try:
        event_links = await get_event_links_service(
            keywords, eventbrite, meetup, luma, country, city, country_code
        )
        return EventLinksResponse(event_links=event_links)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception:
        raise HTTPException(status_code=500, detail="Failed to get event links")

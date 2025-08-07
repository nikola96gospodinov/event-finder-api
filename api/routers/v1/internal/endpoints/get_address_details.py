from fastapi import APIRouter, HTTPException

from utils.address_utils import get_location_from_query

from ..schemas.get_address_details import AddressDetailsResponse, ErrorResponse

router = APIRouter()


@router.get(
    "/address-details",
    response_model=AddressDetailsResponse,
    responses={
        400: {"model": ErrorResponse, "description": "Bad Request"},
        404: {"model": ErrorResponse, "description": "Not Found"},
        500: {"model": ErrorResponse, "description": "Internal Server Error"},
    },
)
async def get_address_details(postcode: str) -> AddressDetailsResponse:
    try:
        location = get_location_from_query(postcode)
        if location is None:
            raise HTTPException(status_code=404, detail="Postcode not found")

        return AddressDetailsResponse(location=location)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception:
        raise HTTPException(status_code=500, detail="Failed to get address details")

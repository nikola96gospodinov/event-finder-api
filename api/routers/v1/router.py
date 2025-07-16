from fastapi import APIRouter

from api.routers.v1 import external, internal

router = APIRouter()

# Include internal and external routers
router.include_router(internal.router, prefix="/internal", tags=["internal"])
router.include_router(external.router, prefix="/external", tags=["external"])

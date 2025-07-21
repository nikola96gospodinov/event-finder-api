from fastapi import APIRouter

from api.routers.v1.external import external
from api.routers.v1.internal import internal

v1_router = APIRouter()

# Include internal and external routers
v1_router.include_router(internal.router, prefix="/internal", tags=["internal"])
v1_router.include_router(external.router, prefix="/external", tags=["external"])

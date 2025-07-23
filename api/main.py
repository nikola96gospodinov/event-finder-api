from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.routers.v1.v1_router import v1_router
from core.cors_middleware import (
    OriginRestrictionMiddleware,
    get_cors_middleware_config,
    get_origin_restriction_middleware_config,
)
from core.logging_config import get_logger, setup_logging

setup_logging(log_level="INFO")

logger = get_logger(__name__)


app = FastAPI(
    title="Event Finder API",
    description="API for finding and managing events",
    version="1.0.0",
)
cors_config = get_cors_middleware_config()
app.add_middleware(CORSMiddleware, **cors_config)

origin_restriction_config = get_origin_restriction_middleware_config()
if origin_restriction_config:
    app.add_middleware(OriginRestrictionMiddleware, **origin_restriction_config)

app.include_router(v1_router, prefix="/v1", tags=["v1"])


@app.get("/")
def read_root() -> dict[str, str]:
    logger.info("Root endpoint accessed")
    return {"message": "Event Finder API", "version": "1.0.0"}

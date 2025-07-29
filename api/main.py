from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.routers.v1.v1_router import v1_router
from core.cors_middleware import get_cors_middleware_config
from core.logging_config import get_logger

logger = get_logger(__name__)

app = FastAPI(
    title="Event Finder API",
    description="API for finding events based on user preferences",
    version="1.0.0",
)

app.add_middleware(CORSMiddleware, **get_cors_middleware_config())

app.include_router(v1_router, prefix="/api/v1")


@app.get("/health")
async def health_check():
    """Health check endpoint to verify FastAPI is running"""
    try:
        return {
            "status": "healthy",
            "service": "event-finder-api",
            "version": "1.0.0",
        }
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return {
            "status": "unhealthy",
            "service": "event-finder-api",
            "error": f"error: {str(e)}",
        }


@app.get("/")
async def root():
    """Root endpoint"""
    return {"message": "Event Finder API is running"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)

from fastapi import FastAPI

from api.routers.v1.v1_router import v1_router

app = FastAPI(
    title="Event Finder API",
    description="API for finding and managing events",
    version="1.0.0",
)

app.include_router(v1_router, prefix="/v1", tags=["v1"])


@app.get("/")
def read_root() -> dict[str, str]:
    return {"message": "Event Finder API", "version": "1.0.0"}

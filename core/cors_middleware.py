from typing import List, Optional

from fastapi import HTTPException, Request
from starlette.middleware.base import BaseHTTPMiddleware

from core.config import settings
from core.logging_config import get_logger

logger = get_logger(__name__)


class OriginRestrictionMiddleware(BaseHTTPMiddleware):
    """Middleware to restrict API access based on origin in production."""

    def __init__(self, app, allowed_origins: List[str], is_production: bool = False):
        super().__init__(app)
        self.allowed_origins = allowed_origins
        self.is_production = is_production

    async def dispatch(self, request: Request, call_next):
        if not self.is_production:
            return await call_next(request)

        origin = request.headers.get("origin")
        user_agent = request.headers.get("user-agent", "")

        if not origin:
            logger.warning(
                f"Blocking request without origin - User-Agent: {user_agent}"
            )
            raise HTTPException(
                status_code=403,
                detail="Access denied: Origin header required in production",
            )

        # Validate origin format and check against allowed origins
        if self._is_valid_origin(origin) and origin in self.allowed_origins:
            logger.info(f"Allowing request from origin: {origin}")
            return await call_next(request)

        logger.warning(f"Blocking request from unauthorized origin: {origin}")
        raise HTTPException(
            status_code=403, detail="Access denied: Origin not allowed in production"
        )

    def _is_valid_origin(self, origin: str) -> bool:
        """Validate origin format."""
        if not origin:
            return False

        # Basic origin validation
        if not origin.startswith(("http://", "https://")):
            return False

        # Check for common attack patterns
        suspicious_patterns = [
            "javascript:",
            "data:",
            "file:",
            "about:",
            "chrome:",
            "chrome-extension:",
        ]

        for pattern in suspicious_patterns:
            if pattern in origin.lower():
                return False

        return True


def get_cors_middleware_config() -> dict:
    """Get CORS middleware configuration based on environment."""
    from core.config import settings

    is_production = settings.ENVIRONMENT.lower() == "production"

    if is_production:
        allowed_origins = [
            "https://event-finder-ui.vercel.app",
        ]
        logger.info(f"Production mode: CORS restricted to {allowed_origins}")
    else:
        allowed_origins = ["*"]
        logger.info("Development mode: CORS allows all origins")

    return {
        "allow_origins": allowed_origins,
        "allow_credentials": True,
        "allow_methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": [
            "Authorization",
            "Content-Type",
            "Accept",
            "Origin",
            "X-Requested-With",
        ],
        "expose_headers": ["Content-Length"],
    }


def get_origin_restriction_middleware_config() -> Optional[dict]:
    """Get origin restriction middleware configuration based on environment."""

    is_production = settings.ENVIRONMENT.lower() == "production"

    if is_production:
        allowed_origins = [
            "https://event-finder-ui.vercel.app",
        ]
        logger.info(
            f"Production mode: Origin restriction enabled for {allowed_origins}"
        )
        return {"allowed_origins": allowed_origins, "is_production": True}
    else:
        logger.info("Development mode: Origin restriction disabled")
        return None

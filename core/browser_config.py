from .config import settings


class BrowserConfig:
    """Configuration for browser pool settings."""

    MAX_BROWSERS: int = settings.BROWSER_POOL_SIZE
    HEADLESS: bool = settings.BROWSER_HEADLESS
    NAVIGATION_TIMEOUT: int = settings.BROWSER_NAVIGATION_TIMEOUT
    PAGE_TIMEOUT: int = settings.BROWSER_PAGE_TIMEOUT
    BROWSER_ARGS: list[str] = [
        "--disable-blink-features=AutomationControlled",
        "--disable-extensions",
        "--disable-infobars",
        "--enable-automation",
        "--no-first-run",
        "--enable-webgl",
    ]
    USER_AGENT: str = (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    )

    @classmethod
    def get_browser_args(cls) -> list[str]:
        """Get browser launch arguments."""
        return cls.BROWSER_ARGS.copy()

    @classmethod
    def get_context_options(cls) -> dict:
        """Get browser context options."""
        return {
            "user_agent": cls.USER_AGENT,
            "viewport": {"width": 1920, "height": 1080},
            "ignore_https_errors": True,
        }

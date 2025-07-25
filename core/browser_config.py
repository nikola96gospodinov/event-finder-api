from .config import settings


class BrowserConfig:
    """Configuration for browser pool settings."""

    MAX_BROWSERS: int = settings.BROWSER_POOL_SIZE
    HEADLESS: bool = settings.BROWSER_HEADLESS
    NAVIGATION_TIMEOUT: int = settings.BROWSER_NAVIGATION_TIMEOUT
    PAGE_TIMEOUT: int = settings.BROWSER_PAGE_TIMEOUT
    BROWSER_ARGS: list[str] = [
        "--no-sandbox",
        "--disable-dev-shm-usage",
        "--disable-gpu",
        "--disable-gpu-sandbox",
        "--disable-software-rasterizer",
        "--disable-web-security",
        "--disable-features=VizDisplayCompositor",
        "--disable-background-timer-throttling",
        "--disable-backgrounding-occluded-windows",
        "--disable-renderer-backgrounding",
        "--disable-features=TranslateUI,BlinkGenPropertyTrees",
        "--disable-ipc-flooding-protection",
        "--disable-hang-monitor",
        "--disable-prompt-on-repost",
        "--disable-client-side-phishing-detection",
        "--disable-component-extensions-with-background-pages",
        "--disable-default-apps",
        "--disable-extensions",
        "--disable-sync",
        "--disable-translate",
        "--hide-scrollbars",
        "--mute-audio",
        "--no-first-run",
        "--safebrowsing-disable-auto-update",
        "--disable-blink-features=AutomationControlled",
        "--disable-features=site-per-process",
        "--memory-pressure-off",
        "--max_old_space_size=4096",
        "--single-process",
        "--disable-background-networking",
        "--metrics-recording-only",
        "--disable-component-update",
        "--disable-domain-reliability",
        "--disable-features=AudioServiceOutOfProcess",
        "--enable-features=NetworkService,NetworkServiceLogging",
        "--force-color-profile=srgb",
        "--password-store=basic",
        "--use-mock-keychain",
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

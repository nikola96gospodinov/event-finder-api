from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Base
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "AI Agent for Event Discovery"

    # Environment
    ENVIRONMENT: str = "development"  # development, production, staging

    # Logging
    LOG_LEVEL: str = "INFO"

    # Supabase
    SUPABASE_URL: str = ""
    SUPABASE_ANON_KEY: str = ""
    SUPABASE_SERVICE_ROLE_KEY: str = ""

    # LLM/Gemini
    GEMINI_API_KEY: str = ""

    # Email (Mailgun)
    MAILGUN_API_KEY: str = ""
    MAILGUN_DOMAIN: str = ""

    # Upstash Redis
    UPSTASH_REDIS_REST_URL: str = ""
    UPSTASH_REDIS_REST_TOKEN: str = ""

    # Browser Configuration
    BROWSER_POOL_SIZE: int = 1
    BROWSER_HEADLESS: bool = True
    BROWSER_NAVIGATION_TIMEOUT: int = 30000
    BROWSER_PAGE_TIMEOUT: int = 10000

    class Config:
        case_sensitive = True
        env_file = ".env"
        extra = "allow"


settings = Settings()

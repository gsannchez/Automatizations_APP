from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    PROJECT_NAME: str = "Auto Video Maker"

    # Database configuration
    DATABASE_URL: str = "postgresql://autovideouser:autovideopass@localhost:5432/autovideodb"

    # Storage configuration
    STORAGE_TYPE: str = "local"  # local or s3

    # Gemini AI configuration
    GEMINI_API_KEY: str | None = None
    GEMINI_MODEL: str = "gemini-2.0-flash"

    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"

    # JWT authentication
    JWT_SECRET_KEY: str = "change-me-in-production"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30          # short-lived access token
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7             # long-lived refresh token

    class Config:
        env_file = ".env"


settings = Settings()

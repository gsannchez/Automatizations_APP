from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "Auto Video Maker"
    DATABASE_URL: str = "sqlite:///./database.db"

    # Añadir variables de Gemini
    GEMINI_API_KEY: str | None = None
    GEMINI_MODEL: str = "gemini-2.0-flash"

    class Config:
        env_file = ".env"

settings = Settings()

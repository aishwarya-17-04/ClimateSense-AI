from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore"
    )

    PROJECT_NAME: str = "ClimateSense AI Backend"
    FRONTEND_URL: str = "http://localhost:5173"

    DATABASE_URL: str
    SECRET_KEY: str

    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7

    GOOGLE_API_KEY: str = ""
    GEMINI_API_KEY: str = ""
    GEMINI_MODEL: str = "gemini-2.5-flash"

settings = Settings()

if not settings.GOOGLE_API_KEY and settings.GEMINI_API_KEY:
    settings.GOOGLE_API_KEY = settings.GEMINI_API_KEY

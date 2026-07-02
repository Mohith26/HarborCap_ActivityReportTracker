from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DATABASE_URL: str = "sqlite:///./harborcap.db"
    JWT_SECRET: str = "change-this-to-a-random-secret-key"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRE_HOURS: int = 24
    OPENAI_API_KEY: str = ""
    OPENAI_MODEL: str = "gpt-4o"
    UPLOAD_DIR: str = "uploads"
    # Comma-separated list of allowed CORS origins (env-driven for deploy;
    # never combine "*" with allow_credentials=True).
    CORS_ORIGINS: str = "http://localhost:3000"

    class Config:
        env_file = ".env"


settings = Settings()

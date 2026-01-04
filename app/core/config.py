# app/core/config.py
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8"
    )

    APP_NAME: str
    ENV: str

    MONGO_URI: str
    MONGO_DB_NAME: str

    JWT_SECRET: str
    JWT_ALGORITHM: str = "HS256"

    CACHE_ENABLED: bool = True
    CACHE_TTL_SECONDS: int = 60


settings = Settings()

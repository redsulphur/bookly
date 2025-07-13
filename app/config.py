import os

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # Define your configuration fields here, for example:
    # app_name: str = Field(default="MyApp")
    # debug: bool = Field(default=False)
    DATABASE_URL: str
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_SECONDS: int = 3600
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    ENABLE_REDIS_BLOCKLIST: bool = True

    model_config = SettingsConfigDict(
        env_file="app/.env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


# importable
config = Settings()

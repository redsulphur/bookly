import os

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
	# Define your configuration fields here, for example:
	# app_name: str = Field(default="MyApp")
	# debug: bool = Field(default=False)
    DATABASE_URL: str  # No default - must be set in .env
    JWT_SECRET_KEY: str  # No default - must be set in .env  
    JWT_ALGORITHM: str = "HS256"  # Algorithm for JWT encoding
    JWT_ACCESS_TOKEN_EXPIRE_SECONDS: int = 3600  # Token expiration time in seconds
    
    model_config = SettingsConfigDict(
        env_file="app/.env",  # Look for .env in the app folder
        env_file_encoding="utf-8",
        extra="ignore",  # Ignore extra fields not defined in the model
    )

config = Settings()

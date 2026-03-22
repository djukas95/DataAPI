from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    api_token: str = Field(
        default="dev-token-change-in-prod",
        validation_alias="API_TOKEN",
        description="Bearer token for curator endpoints (POST/PATCH/DELETE on /exhibits).",
    )


def get_settings() -> Settings:
    return Settings()

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_env: str = "dev"
    aws_region: str = "ap-south-1"
    public_api_base_url: str = "https://api.yashhonda.com"
    database_url: str = "sqlite:///./yash_honda.db"
    quote_document_bucket: str = "yash-honda-quote-docs-dev"
    aws_secrets_manager_id: str = "yash-honda/dev/backend"
    # When True, `create_all` runs on startup (dev convenience). Prefer Alembic in shared envs.
    auto_create_db: bool = True


@lru_cache
def get_settings() -> Settings:
    return Settings()

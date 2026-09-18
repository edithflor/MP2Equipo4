from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Configuración validada exclusivamente desde variables de entorno."""

    model_config = SettingsConfigDict(env_file=".env", extra="ignore", case_sensitive=False)

    app_env: str = "development"
    app_host: str = "0.0.0.0"
    app_port: int = Field(default=8000, ge=1, le=65535)

    db_host: str = "mariadb"
    db_port: int = Field(default=3306, ge=1, le=65535)
    db_name: str = "dataset_quality"
    db_user: str = "dataset_app"
    db_password: str = Field(min_length=1)

    minio_endpoint: str = "minio:9000"
    minio_access_key: str = Field(min_length=1)
    minio_secret_key: str = Field(min_length=1)
    minio_secure: bool = False
    minio_bucket: str = "dataset-dev"
    copilot_api_key: str | None = None
    copilot_provider: str = "local"


@lru_cache
def get_settings() -> Settings:
    return Settings()  # type: ignore[call-arg]

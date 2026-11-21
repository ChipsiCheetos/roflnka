import logging

from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    FILE_CHUNK_SIZE: int = Field(1_048_576, gt=0, le=104_857_600)
    DATABASE_URL: SecretStr
    JWT_SECRET_KEY: SecretStr = Field(..., min_length=32)
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(30, ge=1, le=1440)
    S3_ENDPOINT_URL: str
    S3_BUCKET_NAME: str
    S3_ACCESS_KEY_ID: str
    S3_SECRET_ACCESS_KEY: SecretStr
    S3_REGION_NAME: str = "garage"

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )


def setup_logging() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        handlers=[logging.StreamHandler()],
    )


settings = Settings()

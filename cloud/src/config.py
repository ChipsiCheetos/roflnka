from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict
import logging

class Settings(BaseSettings):
    FILE_CHUNK_SIZE: int = 1_048_576
    DATABASE_URL: str = Field(..., alias="DATABASE_URL")
    JWT_SECRET_KEY: str = Field(..., alias="JWT_SECRET_KEY")
    JWT_ALGORITHM: str = Field("HS256", alias="JWT_ALGORITHM")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(30, alias="ACCESS_TOKEN_EXPIRE_MINUTES")
    S3_ENDPOINT_URL: str = Field(..., alias="S3_ENDPOINT_URL")
    S3_BUCKET_NAME: str = Field(..., alias="S3_BUCKET_NAME")
    S3_ACCESS_KEY_ID: str = Field(..., alias="S3_ACCESS_KEY_ID")
    S3_SECRET_ACCESS_KEY: str = Field(..., alias="S3_SECRET_ACCESS_KEY")
    S3_REGION_NAME: str = Field("garage", alias="S3_REGION_NAME")

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("app.log")

    ]
)

settings = Settings()
logger = logging.getLogger(__name__)
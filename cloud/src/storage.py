import logging
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

import aioboto3
from botocore.exceptions import ClientError
from src.config import settings

logger = logging.getLogger(__name__)


class S3Storage:
    def __init__(self) -> None:
        self.session = aioboto3.Session()
        self.bucket_name = settings.S3_BUCKET_NAME

    async def upload_file(self, file_bytes: bytes, object_key: str) -> None:
        async with self.session.client(
            "s3",
            endpoint_url=settings.S3_ENDPOINT_URL,
            region_name=settings.S3_REGION_NAME,
            aws_access_key_id=settings.S3_ACCESS_KEY_ID,
            aws_secret_access_key=settings.S3_SECRET_ACCESS_KEY,
        ) as client:
            await client.put_object(
                Body=file_bytes, Bucket=self.bucket_name, Key=object_key
            )

    @asynccontextmanager
    async def download_file(self, object_key: str) -> AsyncGenerator[any, None]:
        async with self.session.client(
            "s3",
            endpoint_url=settings.S3_ENDPOINT_URL,
            region_name=settings.S3_REGION_NAME,
            aws_access_key_id=settings.S3_ACCESS_KEY_ID,
            aws_secret_access_key=settings.S3_SECRET_ACCESS_KEY,
        ) as client:
            response = await client.get_object(Bucket=self.bucket_name, Key=object_key)
            async with response["Body"] as stream:
                yield stream

    async def create_presigned_url(
        self,
        object_key: str,
        fields: dict | None = None,
        conditions: list | None = None,
        expiration: int = 3600,
    ) -> str | None:
        async with self.session.client(
            "s3",
            endpoint_url=settings.S3_ENDPOINT_URL,
            region_name=settings.S3_REGION_NAME,
            aws_access_key_id=settings.S3_ACCESS_KEY_ID,
            aws_secret_access_key=settings.S3_SECRET_ACCESS_KEY,
        ) as client:
            try:
                response = await client.generate_presigned_url(
                    "get_object",
                    Params={
                        "Bucket": self.bucket_name,
                        "Key": object_key,
                    },
                    ExpiresIn=expiration,
                )
            except ClientError:
                logger.exception("Ошибка при работе с S3: %s")
                return None
            return response

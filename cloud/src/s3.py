import aioboto3
from src.config import settings
from contextlib import asynccontextmanager
from collections.abc import AsyncGenerator
from typing import Any

class S3Storage():
    def __init__(self) -> None:
        self.session = aioboto3.Session()
        self.bucket_name = settings.S3_BUCKET_NAME
    
    async def upload_file(self, file_bytes: bytes, object_key: str) -> None:
        async with self.session.client(
            "s3",
            endpoint_url=settings.S3_ENDPOINT_URL, 
            region_name=settings.S3_REGION_NAME,
            aws_access_key_id=settings.S3_ACCESS_KEY_ID,
            aws_secret_access_key=settings.S3_SECRET_ACCESS_KEY
            ) as client:
               await client.put_object(
                    Body=file_bytes,
                    Bucket=self.bucket_name,
                    Key=object_key
               )

    @asynccontextmanager
    async def download_file(self, object_key: str) -> AsyncGenerator[Any, None]:
                async with self.session.client("s3",
                    endpoint_url=settings.S3_ENDPOINT_URL, 
                    region_name=settings.S3_REGION_NAME,
                    aws_access_key_id=settings.S3_ACCESS_KEY_ID,
                    aws_secret_access_key=settings.S3_SECRET_ACCESS_KEY
                    ) as client:
                        response = await client.get_object(Bucket=self.bucket_name, Key=object_key)
                        yield response["Body"]



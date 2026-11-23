import hashlib
from typing import Annotated
from uuid import UUID

from fastapi import Depends, HTTPException, UploadFile
from pwdlib import PasswordHash
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from src.config import settings
from src.database import get_db
from src.models import File
from src.storage import S3Storage

password_hasher = PasswordHash.recommended()


class FileService:
    def __init__(self, db: Annotated[AsyncSession, Depends(get_db)]) -> None:
        self.db = db
        self.storage = S3Storage()

    def _verify_password(
        self, plain_password: str, hashed_password: str | None
    ) -> bool:
        if not hashed_password:
            return False
        return password_hasher.verify(plain_password, hashed_password)

    async def _calculate_hash_and_size(self, file: UploadFile) -> tuple[str, int]:
        sha256_hash = hashlib.sha256()
        size_bytes = 0
        while chunk := await file.read(settings.FILE_CHUNK_SIZE):
            sha256_hash.update(chunk)
            size_bytes += len(chunk)
        await file.seek(0)
        return sha256_hash.hexdigest(), size_bytes

    async def register_file(
        self,
        file: UploadFile,
        max_downloads: int | None,
        password: str | None,
    ) -> File:
        file_hash, size_bytes = await self._calculate_hash_and_size(file)
        statement = select(File).where(File.sha256 == file_hash)
        result = await self.db.execute(statement)
        existing_file = result.scalars().first()

        uploaded_to_s3 = False
        if not existing_file:
            file_bytes = await file.read()
            await self.storage.upload_file(file_bytes, file_hash)
            uploaded_to_s3 = True

        new_file_record = File(
            original_name=file.filename,
            sha256=file_hash,
            size_bytes=size_bytes,
            mime_type=file.content_type,
            max_downloads=max_downloads,
            password_hash=password_hasher.hash(password) if password else None,
        )

        self.db.add(new_file_record)
        try:
            await self.db.commit()
            await self.db.refresh(new_file_record)
        except Exception:
            await self.db.rollback()
            if uploaded_to_s3:
                await self.storage.delete_file(file_hash)
            raise
        return new_file_record

    async def get_download_url(self, file_id: UUID, password: str | None = None) -> str:
        statement = select(File).where(File.id == file_id)
        result = await self.db.execute(statement)
        file_record = result.scalars().first()

        if file_record is None:
            raise HTTPException(status_code=404, detail="File not found")

        if file_record.is_password_protected and (
            not password
            or not self._verify_password(password, file_record.password_hash)
        ):
            raise HTTPException(status_code=401, detail="invalid password")

        if file_record.max_downloads is not None:
            dec_statement = (
                update(File)
                .where(
                    File.id == file_id,
                    File.download_count < File.max_downloads,
                )
                .values(download_count=File.download_count + 1)
            )
            result = await self.db.execute(dec_statement)
            if result.rowcount == 0:
                raise HTTPException(status_code=403, detail="Download limit reached")
            await self.db.commit()

        presigned_url = await self.storage.create_presigned_url(
            object_key=file_record.sha256,
            filename=file_record.original_name,
            expiration=60,
        )

        if presigned_url is None:
            raise HTTPException(
                status_code=502, detail="Unable to generate download link"
            )
        return presigned_url

    async def get_single(self, file_id: UUID) -> File:
        statement = select(File).where(File.id == file_id)
        result = await self.db.execute(statement)
        file_search = result.scalar_one_or_none()

        if file_search is None:
            raise HTTPException(status_code=404, detail="File not found")

        return file_search

    async def file_deletion(
        self, file_id: UUID, password: str | None = None
    ) -> dict[str, str]:
        statement = select(File).where(File.id == file_id)
        result = await self.db.execute(statement)
        file_record = result.scalars().first()

        if file_record is None:
            raise HTTPException(status_code=404, detail="File not found")

        if file_record.is_password_protected and (
            not password
            or not self._verify_password(password, file_record.password_hash)
        ):
            raise HTTPException(status_code=401, detail="invalid password")

        await self.db.delete(file_record)
        await self.db.flush()
        await self.storage.delete_file(file_record.sha256)
        await self.db.commit()
        return {"status": "deleted"}

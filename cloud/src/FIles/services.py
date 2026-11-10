import hashlib
from fastapi import UploadFile, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from src.database import get_db
from src.models import File
from src.storage import S3Storage
from src.config import settings

class FileService:
    def __init__(self, db: AsyncSession = Depends(get_db)) -> None:
        self.db = db
        self.storage = S3Storage()

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
                 
         if not existing_file:
            file_bytes = await file.read()
            await self.storage.upload_file(file_bytes, file_hash)
         
         new_file_record = File(
            original_name=file.filename,
            sha256=file_hash,
            size_bytes=size_bytes,
            mime_type=file.content_type,
            max_downloads=max_downloads ,
            is_password_protected=bool(password),
        )
         
         self.db.add(new_file_record)
         await self.db.commit()
         await self.db.refresh(new_file_record)
         return new_file_record
    
import hashlib
from fastapi import APIRouter, Depends, UploadFile, Form
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from src.database import get_db
from auth.schemas import FileResponse
from src.s3 import S3Storage 
from src.models import File


router = APIRouter(prefix="/files", tags=["files"])

@router.post("/", response_model=FileResponse)
async def create_file(
    file: UploadFile = File(),
    max_downloads: int | None = Form(None),
    password: str | None = Form(None),
    db: AsyncSession = Depends(get_db)
):
    file_bytes = await file.read()
    hash = hashlib.sha256(file_bytes).hexdigest()
    statement = select(File).where(File.sha256 == hash)
    result = await db.execute(statement)
    existing_file = result.scalars().first()
    
    if not existing_file:
        storage = S3Storage()
        await storage.upload_file(file_bytes, hash)

    new_file_record = File(
        original_name=file.filename,
        sha256=hash,
        size_bytes=len(file_bytes),
        mime_type=file.content_type,
        max_downloads=max_downloads,
        is_password_protected=True if password else False,
    )

    db.add(new_file_record)
    await db.commit()
    await db.refresh(new_file_record)
    return new_file_record



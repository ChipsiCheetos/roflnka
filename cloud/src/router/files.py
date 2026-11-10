from fastapi import APIRouter, Depends, UploadFile, Form, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from src.database import get_db
from auth.schemas import FileResponseSchema
from src.models import File
from src.FIles.services import FileService
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/files", tags=["files"])

@router.post("/")
async def create_file(
    file: UploadFile = File(),
    max_downloads: int | None = Form(None),
    password: str | None = Form(None),
    db: AsyncSession = Depends(get_db)
) -> FileResponseSchema:
    try:
        file_service = FileService(db)
        return await file_service.register_file(file, max_downloads, password)
    except Exception as e:
        logger.exception(f"Error creating file resource: {file.filename}")
        raise HTTPException(
            status_code=500,
            detail="An internal error occurred during file upload."
        )

@router.get("/{file_id}")
async def download(file_id: int, db: AsyncSession = Depends(get_db)):
    pass


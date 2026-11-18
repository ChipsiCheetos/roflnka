import logging
from typing import Annotated

from auth.schemas import FileResponseSchema
from fastapi import APIRouter, Depends, Form, HTTPException, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession
from src.database import Dbsession
from src.FIles.services import FileService
from src.models import File

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/files", tags=["files"])


@router.post("/")
async def create_file(
    db: Annotated[AsyncSession, Depends(Dbsession)],
    file: Annotated[UploadFile, File()],
    max_downloads: Annotated[int | None, Form()] = None,
    password: Annotated[str | None, Form()] = None,
) -> FileResponseSchema:
    try:
        file_service = FileService(db)
        return await file_service.register_file(file, max_downloads, password)
    except Exception:
        logger.exception(f"Error creating file resource: {file.filename}")
        raise HTTPException(
            status_code=500,
            detail="An internal error occurred during file upload.",
        )


@router.get("/{file_id}")
async def download_file(file_id: int, db: Dbsession):
    pass

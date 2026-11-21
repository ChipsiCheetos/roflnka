import logging
from typing import Annotated
from uuid import UUID

from auth.schemas import FileResponseSchema
from fastapi import APIRouter, Form, Header, HTTPException, UploadFile
from fastapi.responses import RedirectResponse
from src.database import Dbsession
from src.FIles.services import FileService
from src.models import File

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/files", tags=["files"])


@router.post("/")
async def create_file(
    db: Dbsession,
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
async def download_file(
    db: Dbsession,
    file_id: UUID,
    password: Annotated[str | None, Header(alias="X-File-Password")] = None,
) -> RedirectResponse:
    try:
        file_service = FileService(db)
        presigned_url = await file_service.get_download_url(file_id, password)
        return RedirectResponse(url=presigned_url, status_code=307)
    except HTTPException:
        raise
    except Exception:
        logger.exception(f"Error getting url for file_id: {file_id}")
        raise HTTPException(
            status_code=500, detail="An internal error occurred during generating url"
        )


@router.get("/{file_id}/info")
async def get_file_info(file_id: UUID, db: Dbsession) -> FileResponseSchema:
    file_service = FileService(db)
    return await file_service.get_single(file_id)

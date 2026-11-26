import logging
from typing import Annotated
from uuid import UUID

from auth.schemas import FileResponseSchema, StatusResponseSchema
from fastapi import APIRouter, File, Form, Header, UploadFile
from fastapi.responses import RedirectResponse
from src.database import DbSession
from src.files.services import FileService

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/files", tags=["files"])


# TODO Сделать фабрики как в users.py
@router.post("/")
async def create_file(
    db: DbSession,
    file: Annotated[UploadFile, File()],
    max_downloads: Annotated[int | None, Form()] = None,
    password: Annotated[str | None, Form()] = None,
) -> FileResponseSchema:
    file_service = FileService(db)
    return await file_service.register_file(file, max_downloads, password)


@router.get("/{file_id}")
async def download_file(
    db: DbSession,
    file_id: UUID,
    password: Annotated[str | None, Header(alias="X-File-Password")] = None,
) -> RedirectResponse:
    file_service = FileService(db)
    presigned_url = await file_service.get_download_url(file_id, password)
    return RedirectResponse(url=presigned_url, status_code=307)


@router.get("/{file_id}/info")
async def get_file_info(file_id: UUID, db: DbSession) -> FileResponseSchema:
    file_service = FileService(db)
    return await file_service.get_single(file_id)


@router.delete("/{file_id}")
async def delete_file(
    db: DbSession,
    file_id: UUID,
    password: Annotated[str | None, Header(alias="X-File-Password")] = None,
) -> StatusResponseSchema:
    file_service = FileService(db)
    return await file_service.file_deletion(file_id, password)

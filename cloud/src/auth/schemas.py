import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UserCreateSchema(BaseModel):
    email: EmailStr
    password: str

    model_config = ConfigDict(from_attributes=True)


class UserResponseSchema(BaseModel):
    id: uuid.UUID
    email: EmailStr

    model_config = ConfigDict(from_attributes=True)


class UserInProductSchema(BaseModel):
    id: int
    email: EmailStr

    model_config = ConfigDict(from_attributes=True)


class FileResponseSchema(BaseModel):
    id: uuid.UUID
    checksum: str = Field(validation_alias="sha256")
    expires_at: datetime | None
    max_downloads: int | None = 0
    download_count: int
    is_password_protected: bool
    owner: UserInProductSchema | str | None = (
        None  # ВРЕМЕННЫЙ ВАРИАНТ КОГДА ДОБАВЯТ АУТЕНТИФИКАЦИЮ УБРАТЬ!!!
    )


class StatusResponseSchema(BaseModel):
    status: str = "ok"

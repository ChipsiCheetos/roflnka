import uuid
from datetime import datetime
from pydantic import BaseModel, EmailStr

class UserCreateSchema(BaseModel):
    email: EmailStr
    password: str

class UserResponseSchema(BaseModel):
    id: int
    email: EmailStr

    model_config = {"from_attributes": True}

class UserInProductSchema(BaseModel):
    id: int
    email: EmailStr

    model_config = {"from_attributes": True}

class FIleCreateSchema(BaseModel):
    name: str
    size: int
    mimetype: str
    checksum: str
    duration_seconds: int | None = None
    max_downloads: int | None
    password: str | None

class FileResponseSchema(BaseModel):
    id: uuid.UUID
    checksum: str
    expires_at: datetime | None
    max_downloads: int
    download_count: int
    is_password_protected: bool
    owner: UserInProductSchema
    
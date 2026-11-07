import uuid
from datetime import datetime
from pydantic import BaseModel, EmailStr

class UserCreate:
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    id: int
    email: EmailStr

    model_config = {"from_attributes": True}

class UserInProduct(BaseModel):
    id: int
    email: EmailStr

    model_config = {"from_attributes": True}

class FIleCreate(BaseModel):
    name: str
    size: int
    mimetype: str
    checksum: str
    duration_seconds: int | None = None
    max_downloads: int | None
    password: str | None

class FileResponse(BaseModel):
    id: uuid.UUID
    checksum: str
    expires_at: datetime | None
    max_downloads: int
    download_count: int
    is_password_protected: bool
    owner: UserInProduct
    
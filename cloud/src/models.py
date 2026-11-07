from src.database import Base
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import Integer, String, DateTime, Boolean
from datetime import datetime
from uuid import UUID, uuid4

class File(Base):
    __tablename__ = "files"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    original_name: Mapped[str] = mapped_column(String(255))
    sha256: Mapped[str] = mapped_column(String(64), index=True)
    size_bytes: Mapped[int] = mapped_column(Integer)
    mime_type: Mapped[str] = mapped_column(String(255), index=True)
    expires_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    password_hash: Mapped[str | None] = mapped_column(String(255), nullable=True)
    max_downloads: Mapped[int | None] = mapped_column(Integer, nullable=True)
    download_count: Mapped[int] = mapped_column(Integer, default=0)
    is_password_protected: Mapped[bool] = mapped_column(Boolean, default=False)

    

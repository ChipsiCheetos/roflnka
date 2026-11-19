from collections.abc import AsyncGenerator
from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase
from src.config import settings

DATABASE_URL = settings.DATABASE_URL

engine = create_async_engine(DATABASE_URL)

asyncSession = async_sessionmaker(
    bind=engine, class_=AsyncSession, expire_on_commit=False
)


class Base(DeclarativeBase):
    pass


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with asyncSession() as session:
        yield session


async def init_model() -> None:
    async with engine.begin() as conn:
        from src.models import Base

        await conn.run_sync(Base.metadata.create_all)


Dbsession = Annotated[AsyncSession, Depends(get_db)]

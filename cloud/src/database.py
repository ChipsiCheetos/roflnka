from src.config import settings
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from collections.abc import AsyncGenerator

DATABASE_URL = settings.DATABASE_URL

engine = create_async_engine(DATABASE_URL)

asyncSession = async_sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)

class Base(DeclarativeBase): pass

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with asyncSession() as session:
        yield session

async def init_model() -> None:
    async with engine.begin() as conn:
        from src.models import Base
        await conn.run_sync(Base.metadata.create_all)
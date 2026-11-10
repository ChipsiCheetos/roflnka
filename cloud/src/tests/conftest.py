import os
import pytest
from httpx import AsyncClient, ASGITransport
from collections.abc import AsyncGenerator
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from collections.abc import AsyncGenerator

os.environ["JWT_SECRET_KEY"] = "mock_secret_key_for_testing"
os.environ["S3_ENDPOINT_URL"] = "http://localhost:9000"
os.environ["S3_BUCKET_NAME"] = "test-bucket"
os.environ["S3_ACCESS_KEY_ID"] = "mock_access_key"
os.environ["S3_SECRET_ACCESS_KEY"] = "mock_secret_key"

from src.main import app
from src.database import get_db, Base

TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"
engine = create_async_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = async_sessionmaker(autocommit=False, autoflush=False, bind=engine, class_=AsyncSession)

@pytest.fixture(autouse=True)
async def init_model() -> AsyncGenerator[None, None]:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

async def test_get_db() -> AsyncGenerator[AsyncSession, None]:
    async with TestingSessionLocal() as session:
            yield session

@pytest.fixture
async def client() -> AsyncGenerator[any, None]:
    app.dependency_overrides[get_db] = test_get_db
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test"
    ) as ac:
        yield ac
    app.dependency_overrides.clear()

@pytest.fixture(autouse=True)
def mock_s3_upload(monkeypatch) -> None:
    from src.storage import S3Storage 
    async def mock_upload(*args, **kwargs) -> None:
         return None
    monkeypatch.setattr(S3Storage, "upload_file", mock_upload)

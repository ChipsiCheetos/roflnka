import os
from collections.abc import AsyncGenerator

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

os.environ["JWT_SECRET_KEY"] = "mock_secret_key_for_testing"
os.environ["S3_ENDPOINT_URL"] = "http://localhost:9000"
os.environ["S3_BUCKET_NAME"] = "test-bucket"
os.environ["S3_ACCESS_KEY_ID"] = "mock_access_key"
os.environ["S3_SECRET_ACCESS_KEY"] = "mock_secret_key"

from src.database import Base, get_db
from src.main import app

TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"
engine = create_async_engine(
    TEST_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = async_sessionmaker(
    autocommit=False, autoflush=False, bind=engine, class_=AsyncSession
)


@pytest.fixture(autouse=True)
async def init_model() -> AsyncGenerator[None, None]:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


async def override_get_db() -> AsyncGenerator[AsyncSession, None]:
    async with TestingSessionLocal() as session:
        yield session


@pytest.fixture
async def client() -> AsyncGenerator[any, None]:
    app.dependency_overrides[get_db] = override_get_db
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        yield ac
    app.dependency_overrides.clear()


@pytest.fixture(autouse=True)
def mock_s3_upload(monkeypatch) -> None:
    from src.storage import S3Storage

    async def mock_upload(*args, **kwargs) -> None:
        return None

    async def mock_presigned_url(*args, **kwargs) -> str:
        return "https://s3.test"

    monkeypatch.setattr(S3Storage, "upload_file", mock_upload)
    monkeypatch.setattr(S3Storage, "create_presigned_url", mock_presigned_url)


@pytest.fixture
async def uploaded_file(client: AsyncClient) -> dict:
    file_payload = {"file": ("test.mp4", b"fake video content", "video/mp4")}
    response = await client.post("/files/", files=file_payload)
    assert response.status_code == 200
    return response.json()

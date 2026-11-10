import pytest
from httpx import AsyncClient
from src.auth.schemas import FileResponseSchema

pytestmark = pytest.mark.asyncio

async def test_create_file_success(client: AsyncClient) -> None:
    file_payload = {"file": ("test.mp4", b"fake video content", "video/mp4")}
    response = await client.post("/files/", files=file_payload)
    assert response.status_code == 200
    data = response.json()
    expected_keys = {
        "id",
        "checksum",
        "expires_at",
        "max_downloads",
        "download_count",
        "owner"
    }
    assert expected_keys.issubset(data.keys())
    assert data["is_password_protected"] is False
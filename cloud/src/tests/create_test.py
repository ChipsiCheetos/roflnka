import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
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
        "owner",
    }
    assert expected_keys.issubset(data.keys())
    assert data["is_password_protected"] is False


@pytest.mark.asyncio
async def test_get_download_url_success(client: AsyncClient) -> None:
    file_payload = {"file": ("test.mp4", b"fake video content", "video/mp4")}
    create_response = await client.post("/files/", files=file_payload)
    assert create_response.status_code == 200
    file_id = create_response.json()["id"]

    response = await client.get(f"/files/{file_id}")

    assert response.status_code == 307
    assert "location" in response.headers


@pytest.mark.asyncio
async def test_get_single(client: AsyncClient) -> None:
    file_payload = {"file": ("test.mp4", b"fake video content", "video/mp4")}
    create_response = await client.post("/files/", files=file_payload)
    assert create_response.status_code == 200
    file_id = create_response.json()["id"]

    response = await client.get(f"/files/{file_id}/info")
    assert response.status_code == 200

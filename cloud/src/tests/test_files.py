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
async def test_get_download_url_success(
    client: AsyncClient, uploaded_file: dict
) -> None:
    response = await client.get(f"/files/{uploaded_file['id']}")
    assert response.status_code == 307
    assert response.headers["location"] == "https://s3.test"


@pytest.mark.asyncio
async def test_get_single(client: AsyncClient, uploaded_file: dict) -> None:
    response = await client.get(f"/files/{uploaded_file['id']}/info")
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_delete_file_success(client: AsyncClient, uploaded_file: dict) -> None:
    response = await client.delete(f"/files/{uploaded_file['id']}")
    assert response.status_code == 200
    get_response = await client.get(f"/files/{uploaded_file['id']}")
    assert get_response.status_code == 404


# TODO сделать тесты регистрации и логина
@pytest.mark.asyncio
async def test_user_registration_success(client: AsyncClient) -> None:
    pass


@pytest.mark.asyncio
async def test_user_login_success(client: AsyncClient) -> None:
    pass

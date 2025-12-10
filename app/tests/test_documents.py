import os
import shutil
import io

import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.db.base import Base
from app.main import create_application
from app.db.session import get_session
from app.core.config import settings


@pytest_asyncio.fixture(scope="function")
async def async_client():
    # usar storage aislado para pruebas
    storage_test = "./storage_test"
    original_storage = settings.storage_path
    settings.storage_path = storage_test
    os.makedirs(storage_test, exist_ok=True)

    engine = create_async_engine("sqlite+aiosqlite:///:memory:", future=True)
    async_session = async_sessionmaker(engine, expire_on_commit=False)

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async def override_get_session():
        async with async_session() as session:
            yield session

    app = create_application()
    app.dependency_overrides[get_session] = override_get_session
    transport = ASGITransport(app=app)

    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()
    shutil.rmtree(storage_test, ignore_errors=True)
    settings.storage_path = original_storage


@pytest.mark.asyncio
async def test_upload_and_download_document(async_client: AsyncClient):
    user_payload = {"email": "docuser@example.com", "password": "Secret123!", "full_name": "Doc User"}
    await async_client.post("/api/auth/register", json=user_payload)
    login = await async_client.post(
        "/api/auth/login",
        json={"email": user_payload["email"], "password": user_payload["password"]},
    )
    token = login.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    file_content = b"dummy pdf content"
    files = {
        "file": ("test.pdf", io.BytesIO(file_content), "application/pdf"),
    }
    data = {"link_type": "user", "ref_id": 1, "description": "Test", "is_public": "false"}
    resp_upload = await async_client.post("/api/documents", files=files, data=data, headers=headers)
    assert resp_upload.status_code == 201
    doc_id = resp_upload.json()["id"]

    resp_download = await async_client.get(f"/api/documents/{doc_id}", headers=headers)
    assert resp_download.status_code == 200
    assert resp_download.content == file_content


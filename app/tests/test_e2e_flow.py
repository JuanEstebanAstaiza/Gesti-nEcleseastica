import io
import os
import shutil

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
    # storage aislado para la prueba
    storage_test = "./storage_e2e"
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


@pytest.mark.e2e
@pytest.mark.asyncio
async def test_full_flow(async_client: AsyncClient):
    # 1) Registrar miembro y admin
    member = {"email": "member@example.com", "password": "Member123!", "full_name": "Member"}
    admin = {"email": "admin@example.com", "password": "Admin123!", "full_name": "Admin", "role": "admin"}
    await async_client.post("/api/auth/register", json=member)
    await async_client.post("/api/auth/register", json=admin)

    # 2) Login miembro y admin
    member_login = await async_client.post("/api/auth/login", json={"email": member["email"], "password": member["password"]})
    admin_login = await async_client.post("/api/auth/login", json={"email": admin["email"], "password": admin["password"]})
    member_token = member_login.json()["access_token"]
    admin_token = admin_login.json()["access_token"]

    # 3) Crear donación (miembro)
    donation_payload = {
        "donor_name": "Juan",
        "donor_document": "123",
        "donation_type": "diezmo",
        "amount": "150.00",
        "payment_method": "efectivo",
        "note": "E2E",
        "donation_date": "2025-01-02",
    }
    headers_member = {"Authorization": f"Bearer {member_token}"}
    donation_resp = await async_client.post("/api/donations", json=donation_payload, headers=headers_member)
    assert donation_resp.status_code == 201
    donation_id = donation_resp.json()["id"]

    # 4) Subir comprobante
    file_content = b"e2e content"
    files = {"file": ("recibo.pdf", io.BytesIO(file_content), "application/pdf")}
    data = {"link_type": "donation", "ref_id": str(donation_id), "description": "Recibo E2E"}
    upload_resp = await async_client.post("/api/documents", files=files, data=data, headers=headers_member)
    assert upload_resp.status_code == 201
    doc_id = upload_resp.json()["id"]

    # 5) Descargar comprobante
    download_resp = await async_client.get(f"/api/documents/{doc_id}", headers=headers_member)
    assert download_resp.status_code == 200
    assert download_resp.content == file_content

    # 6) Reporte admin
    headers_admin = {"Authorization": f"Bearer {admin_token}"}
    summary_resp = await async_client.get("/api/reports/summary", headers=headers_admin)
    assert summary_resp.status_code == 200
    summary = summary_resp.json()
    assert summary["total_donations"] == 1
    assert summary["total_amount"] == 150.0
    assert summary["by_type"]["diezmo"] == 1


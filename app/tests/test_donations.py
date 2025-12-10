import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.db.base import Base
from app.main import create_application
from app.db.session import get_session


@pytest_asyncio.fixture(scope="function")
async def async_client():
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


@pytest.mark.asyncio
async def test_member_can_create_and_view_own_donations_but_not_list_all(async_client: AsyncClient):
    member_payload = {"email": "member@example.com", "password": "Member123!", "full_name": "Member"}
    admin_payload = {"email": "admin@example.com", "password": "Admin123!", "full_name": "Admin", "role": "admin"}

    # Crear usuarios
    await async_client.post("/api/auth/register", json=member_payload)
    await async_client.post("/api/auth/register", json=admin_payload)

    # Login member
    resp_login_member = await async_client.post(
        "/api/auth/login", json={"email": member_payload["email"], "password": member_payload["password"]}
    )
    member_token = resp_login_member.json()["access_token"]
    member_headers = {"Authorization": f"Bearer {member_token}"}

    donation_payload = {
        "donor_name": "Juan",
        "donor_document": "123",
        "donation_type": "diezmo",
        "amount": "100.00",
        "payment_method": "efectivo",
        "note": "Test",
        "donation_date": "2025-01-01",
    }
    resp_create = await async_client.post("/api/donations", json=donation_payload, headers=member_headers)
    assert resp_create.status_code == 201

    resp_my = await async_client.get("/api/donations/me", headers=member_headers)
    assert resp_my.status_code == 200
    assert len(resp_my.json()) == 1

    # Member no puede listar todas
    resp_list_all = await async_client.get("/api/donations", headers=member_headers)
    assert resp_list_all.status_code == 403

    # Admin puede listar todas
    resp_login_admin = await async_client.post(
        "/api/auth/login", json={"email": admin_payload["email"], "password": admin_payload["password"]}
    )
    admin_headers = {"Authorization": f"Bearer {resp_login_admin.json()['access_token']}"}
    resp_list_admin = await async_client.get("/api/donations", headers=admin_headers)
    assert resp_list_admin.status_code == 200
    assert len(resp_list_admin.json()) == 1


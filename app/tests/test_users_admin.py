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
async def test_admin_can_manage_users_and_member_cannot(async_client: AsyncClient):
    admin_payload = {"email": "admin@example.com", "password": "Admin123!", "full_name": "Admin", "role": "admin"}
    member_payload = {"email": "member@example.com", "password": "Member123!", "full_name": "Member"}

    # Crear admin y member
    resp_admin = await async_client.post("/api/auth/register", json=admin_payload)
    assert resp_admin.status_code == 201
    resp_member = await async_client.post("/api/auth/register", json=member_payload)
    assert resp_member.status_code == 201

    # Login admin
    resp_login_admin = await async_client.post(
        "/api/auth/login", json={"email": admin_payload["email"], "password": admin_payload["password"]}
    )
    tokens_admin = resp_login_admin.json()
    admin_headers = {"Authorization": f"Bearer {tokens_admin['access_token']}"}

    # Login member
    resp_login_member = await async_client.post(
        "/api/auth/login", json={"email": member_payload["email"], "password": member_payload["password"]}
    )
    tokens_member = resp_login_member.json()
    member_headers = {"Authorization": f"Bearer {tokens_member['access_token']}"}

    # Admin puede listar
    resp_list_admin = await async_client.get("/api/users", headers=admin_headers)
    assert resp_list_admin.status_code == 200
    assert len(resp_list_admin.json()) >= 2

    # Member no puede listar
    resp_list_member = await async_client.get("/api/users", headers=member_headers)
    assert resp_list_member.status_code == 403

    # Admin actualiza role de member
    resp_patch = await async_client.patch(
        "/api/users/2",
        json={"role": "admin", "full_name": "Member Updated"},
        headers=admin_headers,
    )
    assert resp_patch.status_code == 200
    data_patch = resp_patch.json()
    assert data_patch["role"] == "admin"
    assert data_patch["full_name"] == "Member Updated"

    # Admin elimina usuario (id 2)
    resp_delete = await async_client.delete("/api/users/2", headers=admin_headers)
    assert resp_delete.status_code == 204


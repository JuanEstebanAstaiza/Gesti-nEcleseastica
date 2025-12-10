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
async def test_events_admin_vs_public(async_client: AsyncClient):
    admin_payload = {"email": "admin@example.com", "password": "Admin123!", "full_name": "Admin", "role": "admin"}
    public_payload = {"email": "public@example.com", "password": "Public123!", "full_name": "Public", "role": "public"}

    await async_client.post("/api/auth/register", json=admin_payload)
    await async_client.post("/api/auth/register", json=public_payload)

    login_admin = await async_client.post("/api/auth/login", json={"email": admin_payload["email"], "password": admin_payload["password"]})
    admin_headers = {"Authorization": f"Bearer {login_admin.json()['access_token']}"}

    # Public user cannot create event
    login_public = await async_client.post("/api/auth/login", json={"email": public_payload["email"], "password": public_payload["password"]})
    public_headers = {"Authorization": f"Bearer {login_public.json()['access_token']}"}

    resp_forbidden = await async_client.post(
        "/api/events",
        json={"name": "Campaña", "description": "Test"},
        headers=public_headers,
    )
    assert resp_forbidden.status_code == 403

    # Admin creates event
    resp_create = await async_client.post(
        "/api/events",
        json={"name": "Campaña", "description": "Test", "capacity": 1},
        headers=admin_headers,
    )
    assert resp_create.status_code == 201
    event_id = resp_create.json()["id"]

    # List events (open)
    resp_list = await async_client.get("/api/events")
    assert resp_list.status_code == 200
    assert len(resp_list.json()) == 1

    # Register one attendee
    resp_reg1 = await async_client.post(
        f"/api/events/{event_id}/registrations",
        json={"event_id": event_id, "attendee_name": "Uno", "attendee_email": "u@x.com"},
    )
    assert resp_reg1.status_code == 201

    # Duplicate email should fail
    resp_reg_dup = await async_client.post(
        f"/api/events/{event_id}/registrations",
        json={"event_id": event_id, "attendee_name": "Uno", "attendee_email": "u@x.com"},
    )
    assert resp_reg_dup.status_code == 400

    # Capacity reached should fail
    resp_reg_full = await async_client.post(
        f"/api/events/{event_id}/registrations",
        json={"event_id": event_id, "attendee_name": "Dos", "attendee_email": "dos@x.com"},
    )
    assert resp_reg_full.status_code == 400

    # Cancel registration (admin) frees capacity
    resp_cancel = await async_client.delete(f"/api/events/{event_id}/registrations/1", headers=admin_headers)
    assert resp_cancel.status_code == 204

    # Now another attendee can register
    resp_reg_after_cancel = await async_client.post(
        f"/api/events/{event_id}/registrations",
        json={"event_id": event_id, "attendee_name": "Tres", "attendee_email": "tres@x.com"},
    )
    assert resp_reg_after_cancel.status_code == 201


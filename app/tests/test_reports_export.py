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
async def test_export_csv(async_client: AsyncClient):
    admin = {"email": "admin@example.com", "password": "Admin123!", "full_name": "Admin", "role": "admin"}
    member = {"email": "member@example.com", "password": "Member123!", "full_name": "Member"}
    await async_client.post("/api/auth/register", json=admin)
    await async_client.post("/api/auth/register", json=member)

    admin_login = await async_client.post("/api/auth/login", json={"email": admin["email"], "password": admin["password"]})
    member_login = await async_client.post("/api/auth/login", json={"email": member["email"], "password": member["password"]})
    admin_headers = {"Authorization": f"Bearer {admin_login.json()['access_token']}"}
    member_headers = {"Authorization": f"Bearer {member_login.json()['access_token']}"}

    payload = {
        "donor_name": "X",
        "donor_document": "1",
        "donation_type": "diezmo",
        "amount": "10.00",
        "payment_method": "efectivo",
        "note": "",
        "donation_date": "2025-01-01",
    }
    await async_client.post("/api/donations", json=payload, headers=member_headers)

    resp = await async_client.get("/api/reports/export", headers=admin_headers)
    assert resp.status_code == 200
    assert "text/csv" in resp.headers.get("content-type", "")
    content = resp.text.strip().splitlines()
    assert len(content) == 2  # header + 1 row



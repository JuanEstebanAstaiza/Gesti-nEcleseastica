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
async def test_report_filters(async_client: AsyncClient):
    admin = {"email": "admin@example.com", "password": "Admin123!", "full_name": "Admin", "role": "admin"}
    member = {"email": "member@example.com", "password": "Member123!", "full_name": "Member"}
    await async_client.post("/api/auth/register", json=admin)
    await async_client.post("/api/auth/register", json=member)

    admin_login = await async_client.post("/api/auth/login", json={"email": admin["email"], "password": admin["password"]})
    member_login = await async_client.post("/api/auth/login", json={"email": member["email"], "password": member["password"]})
    admin_headers = {"Authorization": f"Bearer {admin_login.json()['access_token']}"}
    member_headers = {"Authorization": f"Bearer {member_login.json()['access_token']}"}

    donations = [
        {"donation_type": "diezmo", "amount": "50.00", "donation_date": "2025-01-01"},
        {"donation_type": "ofrenda", "amount": "30.00", "donation_date": "2025-02-01"},
    ]
    for d in donations:
        payload = {
            "donor_name": "X",
            "donor_document": "1",
            "payment_method": "efectivo",
            "note": "",
            **d,
        }
        await async_client.post("/api/donations", json=payload, headers=member_headers)

    resp_all = await async_client.get("/api/reports/summary", headers=admin_headers)
    assert resp_all.status_code == 200
    assert resp_all.json()["total_donations"] == 2

    resp_filtered = await async_client.get("/api/reports/summary?donation_type=diezmo", headers=admin_headers)
    assert resp_filtered.status_code == 200
    data = resp_filtered.json()
    assert data["total_donations"] == 1
    assert data["by_type"]["diezmo"] == 1


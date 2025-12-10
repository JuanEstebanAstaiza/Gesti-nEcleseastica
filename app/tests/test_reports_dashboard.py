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
async def test_dashboard_by_month_and_payment_method(async_client: AsyncClient):
    admin = {"email": "admin@example.com", "password": "Admin123!", "full_name": "Admin", "role": "admin"}
    member = {"email": "member@example.com", "password": "Member123!", "full_name": "Member"}
    await async_client.post("/api/auth/register", json=admin)
    await async_client.post("/api/auth/register", json=member)

    admin_login = await async_client.post(
        "/api/auth/login", json={"email": admin["email"], "password": admin["password"]}
    )
    member_login = await async_client.post(
        "/api/auth/login", json={"email": member["email"], "password": member["password"]}
    )
    admin_token = admin_login.json()["access_token"]
    member_token = member_login.json()["access_token"]
    admin_headers = {"Authorization": f"Bearer {admin_token}"}
    member_headers = {"Authorization": f"Bearer {member_token}"}

    # Nuevo formato de donaciones
    donations = [
        {
            "donor_name": "Donante 1",
            "donor_document": "123",
            "amount_tithe": 50.00,
            "amount_offering": 0,
            "amount_missions": 0,
            "amount_special": 0,
            "cash_amount": 50.00,  # Efectivo
            "transfer_amount": 0,
            "donation_date": "2025-01-01",
            "note": "",
            "is_anonymous": False,
        },
        {
            "donor_name": "Donante 2",
            "donor_document": "456",
            "amount_tithe": 0,
            "amount_offering": 30.00,
            "amount_missions": 0,
            "amount_special": 0,
            "cash_amount": 0,
            "transfer_amount": 30.00,  # Transferencia
            "donation_date": "2025-02-01",
            "note": "",
            "is_anonymous": False,
        },
    ]
    for d in donations:
        await async_client.post("/api/donations", json=d, headers=member_headers)

    resp_dash = await async_client.get("/api/reports/dashboard", headers=admin_headers)
    assert resp_dash.status_code == 200
    data = resp_dash.json()
    assert "2025-01" in data["by_month"]
    assert "2025-02" in data["by_month"]
    assert data["by_payment_method"]["efectivo"] == 50.0
    assert data["by_payment_method"]["transferencia"] == 30.0

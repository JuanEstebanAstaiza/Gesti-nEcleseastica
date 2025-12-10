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
async def test_register_login_and_me(async_client: AsyncClient):
    payload = {"email": "demo@example.com", "password": "Secret123!", "full_name": "Demo"}

    resp_register = await async_client.post("/api/auth/register", json=payload)
    assert resp_register.status_code == 201
    data_register = resp_register.json()
    assert data_register["email"] == payload["email"]

    resp_login = await async_client.post(
        "/api/auth/login",
        json={"email": payload["email"], "password": payload["password"]},
    )
    assert resp_login.status_code == 200
    tokens = resp_login.json()
    assert tokens["access_token"]

    headers = {"Authorization": f"Bearer {tokens['access_token']}"}
    resp_me = await async_client.get("/api/users/me", headers=headers)
    assert resp_me.status_code == 200
    me = resp_me.json()
    assert me["email"] == payload["email"]
    assert me["role"] == "member"


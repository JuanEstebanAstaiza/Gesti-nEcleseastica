"""
Pruebas de integración para los endpoints de reportes de donaciones.
"""
import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from datetime import date

from app.main import create_application
from app.db.base import Base
from app.db.session import get_session
from app.core.security import get_password_hash, create_access_token


@pytest_asyncio.fixture(scope="function")
async def test_db():
    """Create a test database with SQLite."""
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    yield async_session
    
    await engine.dispose()


@pytest_asyncio.fixture(scope="function")
async def async_client(test_db):
    """Create async HTTP client."""
    async def override_get_session():
        async with test_db() as session:
            yield session
    
    app = create_application()
    app.dependency_overrides[get_session] = override_get_session
    
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client
    
    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def admin_headers(async_client):
    """Create admin user and get headers."""
    # Register admin
    await async_client.post("/api/auth/register", json={
        "email": "admin@test.com",
        "password": "Admin123!",
        "full_name": "Admin Test",
        "role": "admin"
    })
    
    # Login
    resp = await async_client.post("/api/auth/login", json={
        "email": "admin@test.com",
        "password": "Admin123!"
    })
    token = resp.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest_asyncio.fixture
async def sample_donation(async_client, admin_headers):
    """Create a sample donation."""
    donation_payload = {
        "donor_name": "Test Donor",
        "donor_document": "12345678",
        "amount_tithe": 100000,
        "amount_offering": 50000,
        "amount_missions": 25000,
        "amount_special": 0,
        "cash_amount": 175000,
        "transfer_amount": 0,
        "donation_date": str(date.today()),
        "is_anonymous": False,
    }
    
    resp = await async_client.post("/api/donations", json=donation_payload, headers=admin_headers)
    return resp.json() if resp.status_code == 201 else None


class TestMonthlyReport:
    """Tests for monthly donation reports."""
    
    @pytest.mark.asyncio
    async def test_get_monthly_report_success(self, async_client, admin_headers, sample_donation):
        """Test getting monthly report as admin."""
        today = date.today()
        response = await async_client.get(
            f"/api/reports/donations/monthly?month={today.month}&year={today.year}",
            headers=admin_headers,
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "church_name" in data
        assert data["month"] == today.month
        assert data["year"] == today.year
        assert "donations" in data
        assert "summary" in data
    
    @pytest.mark.asyncio
    async def test_get_monthly_report_unauthorized(self, async_client):
        """Test that monthly report requires authentication."""
        response = await async_client.get(
            "/api/reports/donations/monthly?month=11&year=2024"
        )
        assert response.status_code == 401
    
    @pytest.mark.asyncio
    async def test_export_monthly_csv(self, async_client, admin_headers, sample_donation):
        """Test exporting monthly report as CSV."""
        today = date.today()
        response = await async_client.get(
            f"/api/reports/donations/monthly/csv?month={today.month}&year={today.year}",
            headers=admin_headers,
        )
        
        assert response.status_code == 200
        assert "text/csv" in response.headers.get("content-type", "")


class TestWeeklyReport:
    """Tests for weekly accountant reports."""
    
    @pytest.mark.asyncio
    async def test_get_weekly_report(self, async_client, admin_headers, sample_donation):
        """Test getting weekly report."""
        today = date.today()
        week_number = today.isocalendar()[1]
        
        response = await async_client.get(
            f"/api/reports/donations/weekly/{week_number}?year={today.year}",
            headers=admin_headers,
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "church_name" in data
        assert data["semana"] == week_number
        assert "diezmos_efectivo" in data
        assert "diezmo_de_diezmos" in data
    
    @pytest.mark.asyncio
    async def test_export_weekly_csv(self, async_client, admin_headers, sample_donation):
        """Test exporting weekly report as CSV."""
        today = date.today()
        week_number = today.isocalendar()[1]
        
        response = await async_client.get(
            f"/api/reports/donations/weekly/{week_number}/csv?year={today.year}",
            headers=admin_headers,
        )
        
        assert response.status_code == 200
        assert "text/csv" in response.headers.get("content-type", "")
    
    @pytest.mark.asyncio
    async def test_close_weekly_summary(self, async_client, admin_headers, sample_donation):
        """Test closing weekly summary."""
        today = date.today()
        week_number = today.isocalendar()[1]
        
        payload = {
            "summary_date": str(today),
            "week_number": week_number,
            "year": today.year,
            "witness_1_name": "Juan Pérez",
            "witness_2_name": "María García",
            "notes": "Cierre semanal de prueba",
        }
        
        response = await async_client.post(
            "/api/reports/donations/weekly/close",
            headers=admin_headers,
            json=payload,
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["is_closed"] == True
        assert data["week_number"] == week_number


class TestDonationFormat:
    """Tests for donation format (separated amounts)."""
    
    @pytest.mark.asyncio
    async def test_create_donation_with_separated_amounts(self, async_client, admin_headers):
        """Test creating a donation with separated amounts."""
        payload = {
            "donor_name": "New Donor",
            "donor_document": "987654321",
            "amount_tithe": 200000,
            "amount_offering": 100000,
            "amount_missions": 50000,
            "amount_special": 0,
            "cash_amount": 350000,
            "transfer_amount": 0,
            "donation_date": str(date.today()),
            "is_anonymous": False,
        }
        
        response = await async_client.post(
            "/api/donations",
            headers=admin_headers,
            json=payload,
        )
        
        assert response.status_code == 201
        data = response.json()
        assert float(data["amount_total"]) == 350000.0
        assert data["is_cash"] == True
        assert data["is_transfer"] == False

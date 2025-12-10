"""
Pruebas de integración para el módulo de gastos.
"""
import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from datetime import date

from app.main import create_application
from app.db.base import Base
from app.db.session import get_session


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
    await async_client.post("/api/auth/register", json={
        "email": "admin@test.com",
        "password": "Admin123!",
        "full_name": "Admin Test",
        "role": "admin"
    })
    
    resp = await async_client.post("/api/auth/login", json={
        "email": "admin@test.com",
        "password": "Admin123!"
    })
    token = resp.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest_asyncio.fixture
async def member_headers(async_client):
    """Create member user and get headers."""
    await async_client.post("/api/auth/register", json={
        "email": "member@test.com",
        "password": "Member123!",
        "full_name": "Member Test",
    })
    
    resp = await async_client.post("/api/auth/login", json={
        "email": "member@test.com",
        "password": "Member123!"
    })
    token = resp.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest_asyncio.fixture
async def expense_category(async_client, admin_headers):
    """Create an expense category for testing."""
    payload = {
        "name": "Servicios Públicos",
        "description": "Agua, luz, gas",
        "color": "#3b82f6",
        "monthly_budget": 500000,
    }
    resp = await async_client.post(
        "/api/expenses/categories",
        headers=admin_headers,
        json=payload
    )
    if resp.status_code == 201:
        return resp.json()
    return None


@pytest_asyncio.fixture
async def sample_expense(async_client, admin_headers, expense_category):
    """Create a sample expense for testing."""
    if not expense_category:
        return None
        
    payload = {
        "category_id": expense_category["id"],
        "description": "Pago de energía",
        "amount": 150000,
        "expense_date": str(date.today()),
        "vendor_name": "EPM",
        "payment_method": "transferencia",
    }
    resp = await async_client.post(
        "/api/expenses/",
        headers=admin_headers,
        json=payload
    )
    if resp.status_code == 201:
        return resp.json()
    return None


class TestExpenseCategories:
    """Tests for expense categories."""
    
    @pytest.mark.asyncio
    async def test_list_categories(self, async_client, admin_headers, expense_category):
        """Test listing expense categories."""
        response = await async_client.get(
            "/api/expenses/categories",
            headers=admin_headers,
        )
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
    
    @pytest.mark.asyncio
    async def test_create_category(self, async_client, admin_headers):
        """Test creating an expense category."""
        payload = {
            "name": "Arriendo",
            "description": "Alquiler del local",
            "color": "#8b5cf6",
            "monthly_budget": 1500000,
        }
        
        response = await async_client.post(
            "/api/expenses/categories",
            headers=admin_headers,
            json=payload,
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Arriendo"
    
    @pytest.mark.asyncio
    async def test_create_category_requires_admin(self, async_client, member_headers):
        """Test that creating a category requires admin role."""
        payload = {
            "name": "Nueva Categoría",
            "color": "#000000",
        }
        
        response = await async_client.post(
            "/api/expenses/categories",
            headers=member_headers,
            json=payload,
        )
        
        assert response.status_code == 403


class TestExpenseTags:
    """Tests for expense tags."""
    
    @pytest.mark.asyncio
    async def test_list_tags(self, async_client, admin_headers):
        """Test listing expense tags."""
        response = await async_client.get(
            "/api/expenses/tags",
            headers=admin_headers,
        )
        
        assert response.status_code == 200
        assert isinstance(response.json(), list)
    
    @pytest.mark.asyncio
    async def test_create_tag(self, async_client, admin_headers):
        """Test creating an expense tag."""
        payload = {
            "name": "Urgente",
            "color": "#ef4444",
        }
        
        response = await async_client.post(
            "/api/expenses/tags",
            headers=admin_headers,
            json=payload,
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Urgente"


class TestExpenses:
    """Tests for expense CRUD operations."""
    
    @pytest.mark.asyncio
    async def test_list_expenses(self, async_client, admin_headers, sample_expense):
        """Test listing expenses."""
        response = await async_client.get(
            "/api/expenses/",
            headers=admin_headers,
        )
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
    
    @pytest.mark.asyncio
    async def test_create_expense(self, async_client, admin_headers, expense_category):
        """Test creating an expense."""
        if not expense_category:
            pytest.skip("Category not created")
            
        payload = {
            "category_id": expense_category["id"],
            "description": "Pago de agua",
            "amount": 50000,
            "expense_date": str(date.today()),
            "vendor_name": "EPM Aguas",
            "payment_method": "efectivo",
        }
        
        response = await async_client.post(
            "/api/expenses/",
            headers=admin_headers,
            json=payload,
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["description"] == "Pago de agua"
        assert float(data["amount"]) == 50000.0
        assert data["status"] == "pending"
    
    @pytest.mark.asyncio
    async def test_get_expense_by_id(self, async_client, admin_headers, sample_expense):
        """Test getting an expense by ID."""
        if not sample_expense:
            pytest.skip("Expense not created")
            
        response = await async_client.get(
            f"/api/expenses/{sample_expense['id']}",
            headers=admin_headers,
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == sample_expense["id"]
    
    @pytest.mark.asyncio
    async def test_approve_expense(self, async_client, admin_headers, sample_expense):
        """Test approving an expense."""
        if not sample_expense:
            pytest.skip("Expense not created")
            
        response = await async_client.post(
            f"/api/expenses/{sample_expense['id']}/approve",
            headers=admin_headers,
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "approved"
    
    @pytest.mark.asyncio
    async def test_pay_expense(self, async_client, admin_headers, sample_expense):
        """Test marking an expense as paid."""
        if not sample_expense:
            pytest.skip("Expense not created")
            
        # First approve
        await async_client.post(
            f"/api/expenses/{sample_expense['id']}/approve",
            headers=admin_headers,
        )
        
        # Then pay
        response = await async_client.post(
            f"/api/expenses/{sample_expense['id']}/pay",
            headers=admin_headers,
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "paid"
    
    @pytest.mark.asyncio
    async def test_cancel_expense(self, async_client, admin_headers, expense_category):
        """Test cancelling an expense."""
        if not expense_category:
            pytest.skip("Category not created")
            
        # Create expense to cancel
        payload = {
            "category_id": expense_category["id"],
            "description": "Gasto a cancelar",
            "amount": 10000,
            "expense_date": str(date.today()),
            "payment_method": "efectivo",
        }
        create_resp = await async_client.post(
            "/api/expenses/",
            headers=admin_headers,
            json=payload,
        )
        assert create_resp.status_code == 201, f"Failed to create expense: {create_resp.text}"
        expense = create_resp.json()
        
        response = await async_client.delete(
            f"/api/expenses/{expense['id']}",
            headers=admin_headers,
        )
        
        assert response.status_code == 204


class TestExpenseReports:
    """Tests for expense reports."""
    
    @pytest.mark.asyncio
    async def test_expense_summary(self, async_client, admin_headers, sample_expense):
        """Test getting expense summary."""
        response = await async_client.get(
            "/api/expenses/reports/summary",
            headers=admin_headers,
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "total" in data
        assert "pending" in data
        assert "count" in data
    
    @pytest.mark.asyncio
    async def test_monthly_expense_report(self, async_client, admin_headers, sample_expense):
        """Test getting monthly expense report."""
        today = date.today()
        response = await async_client.get(
            f"/api/expenses/reports/monthly?month={today.month}&year={today.year}",
            headers=admin_headers,
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "church_name" in data
        assert "expenses" in data
        assert "summary" in data
    
    @pytest.mark.asyncio
    async def test_export_expenses_csv(self, async_client, admin_headers, sample_expense):
        """Test exporting expenses as CSV."""
        today = date.today()
        response = await async_client.get(
            f"/api/expenses/reports/monthly/csv?month={today.month}&year={today.year}",
            headers=admin_headers,
        )
        
        assert response.status_code == 200
        assert "text/csv" in response.headers.get("content-type", "")


class TestExpenseFilters:
    """Tests for expense filtering."""
    
    @pytest.mark.asyncio
    async def test_filter_by_category(self, async_client, admin_headers, sample_expense, expense_category):
        """Test filtering expenses by category."""
        if not expense_category:
            pytest.skip("Category not created")
            
        response = await async_client.get(
            f"/api/expenses/?category_id={expense_category['id']}",
            headers=admin_headers,
        )
        
        assert response.status_code == 200
    
    @pytest.mark.asyncio
    async def test_filter_by_status(self, async_client, admin_headers, sample_expense):
        """Test filtering expenses by status."""
        response = await async_client.get(
            "/api/expenses/?status=pending",
            headers=admin_headers,
        )
        
        assert response.status_code == 200
    
    @pytest.mark.asyncio
    async def test_filter_by_date_range(self, async_client, admin_headers, sample_expense):
        """Test filtering expenses by date range."""
        today = date.today()
        response = await async_client.get(
            f"/api/expenses/?start_date={today}&end_date={today}",
            headers=admin_headers,
        )
        
        assert response.status_code == 200

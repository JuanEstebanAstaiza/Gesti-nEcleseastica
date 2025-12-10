# Estrategia de Testing

## Estructura de Tests

```
tests/
├── test_health.py              # Tests unitarios de health
├── test_security.py            # Tests de hashing y JWT
├── test_auth_flow.py           # Tests de autenticación
├── test_users_admin.py         # Tests de gestión de usuarios
├── test_donations.py           # Tests de donaciones básicas
├── test_donation_reports.py    # Tests de reportes de donaciones (nuevo)
├── test_expenses.py            # Tests del módulo de gastos (nuevo)
├── test_documents.py           # Tests de documentos
├── test_events.py              # Tests de eventos e inscripciones
├── test_reports.py             # Tests de reportes legacy
├── test_reports_dashboard.py   # Tests del dashboard
├── test_reports_export.py      # Tests de exportación
├── test_e2e_flow.py            # Test end-to-end completo
└── test_integration_endpoints.py # Tests de integración frontend-backend
```

## Tipos de Tests

### 1. Tests Unitarios

Prueban funciones aisladas sin dependencias externas.

```python
# test_security.py
def test_password_hash():
    password = "testpass123"
    hashed = get_password_hash(password)
    assert verify_password(password, hashed)
    assert not verify_password("wrong", hashed)
```

### 2. Tests de Integración

Prueban la interacción entre componentes usando SQLite en memoria.

```python
# test_auth_flow.py
@pytest.mark.asyncio
async def test_register_and_login():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # Registrar usuario
        response = await client.post("/api/auth/register", json={...})
        assert response.status_code == 201
        
        # Login
        response = await client.post("/api/auth/login", json={...})
        assert response.status_code == 200
```

### 3. Tests de Reportes de Donaciones (Nuevo)

Prueban el formato actualizado de donaciones con montos separados y reportes para contadora.

```python
# test_donation_reports.py
class TestMonthlyReport:
    @pytest.mark.asyncio
    async def test_get_monthly_report_success(self, async_client, admin_token, sample_donations):
        """Test getting monthly report as admin."""
        response = await async_client.get(
            "/api/reports/donations/monthly?month=11&year=2024",
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "donations" in data
        assert "summary" in data

class TestWeeklyReport:
    @pytest.mark.asyncio
    async def test_get_weekly_report(self, async_client, admin_token, sample_donations):
        """Test getting weekly report for accountant."""
        response = await async_client.get(
            "/api/reports/donations/weekly/45?year=2024",
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "diezmos_efectivo" in data
        assert "diezmo_de_diezmos" in data
```

### 4. Tests del Módulo de Gastos (Nuevo)

Prueban el módulo completo de gastos con categorías, etiquetas y flujo de aprobación.

```python
# test_expenses.py
class TestExpenseCategories:
    @pytest.mark.asyncio
    async def test_create_category(self, async_client, admin_token):
        payload = {
            "name": "Servicios Públicos",
            "color": "#3b82f6",
            "monthly_budget": 500000,
        }
        
        response = await async_client.post(
            "/api/expenses/categories",
            headers={"Authorization": f"Bearer {admin_token}"},
            json=payload,
        )
        
        assert response.status_code == 201

class TestExpenses:
    @pytest.mark.asyncio
    async def test_expense_approval_flow(self, async_client, admin_token, sample_expense):
        # 1. Aprobar gasto pendiente
        response = await async_client.post(
            f"/api/expenses/{sample_expense.id}/approve",
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        assert response.json()["status"] == "approved"
        
        # 2. Marcar como pagado
        response = await async_client.post(
            f"/api/expenses/{sample_expense.id}/pay",
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        assert response.json()["status"] == "paid"
```

### 5. Tests End-to-End

Prueban flujos completos de usuario.

```python
# test_e2e_flow.py
@pytest.mark.e2e
async def test_complete_donation_flow():
    # 1. Registrar usuario
    # 2. Login
    # 3. Crear donación con montos separados
    # 4. Subir documento
    # 5. Ver reporte mensual
    # 6. Exportar CSV
```

## Ejecutar Tests

### Requisitos

```bash
pip install pytest pytest-asyncio httpx aiosqlite
```

### Comandos

```bash
# Todos los tests
pytest -v

# Solo tests de donaciones y reportes
pytest app/tests/test_donation_reports.py -v

# Solo tests de gastos
pytest app/tests/test_expenses.py -v

# Solo tests unitarios
pytest app/tests/test_security.py app/tests/test_health.py -v

# Tests de integración
pytest app/tests/test_auth_flow.py app/tests/test_donations.py -v

# Tests E2E (requiere DB)
pytest app/tests/test_e2e_flow.py -v

# Con cobertura
pytest --cov=app --cov-report=html -v

# Tests específicos por marca
pytest -m "not e2e" -v  # Excluir E2E
pytest -m "e2e" -v      # Solo E2E
```

### En Docker

```bash
# Ejecutar dentro del contenedor
docker exec -it ekklesia_backend pytest -v

# Con salida detallada
docker exec -it ekklesia_backend pytest -v --tb=short

# Solo tests nuevos
docker exec -it ekklesia_backend pytest app/tests/test_donation_reports.py app/tests/test_expenses.py -v
```

## Configuración

### pytest.ini

```ini
[pytest]
asyncio_mode = auto
asyncio_default_fixture_loop_scope = function
testpaths = tests app/tests
python_files = test_*.py
python_functions = test_*
markers =
    e2e: marks tests as end-to-end (may require running services)
```

### Fixtures Comunes

```python
# conftest.py
@pytest_asyncio.fixture
async def test_db():
    """Create a test database with SQLite."""
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    async_session = async_sessionmaker(engine, class_=AsyncSession)
    
    async def override_get_session():
        async with async_session() as session:
            yield session
    
    app.dependency_overrides[get_session] = override_get_session
    yield async_session
    app.dependency_overrides.clear()

@pytest_asyncio.fixture
async def admin_token(admin_user):
    """Generate JWT token for admin user."""
    return create_access_token(admin_user.id)
```

## Tests de Nuevos Módulos

### Reportes de Donaciones

| Test | Descripción | Estado |
|------|-------------|--------|
| `test_get_monthly_report_success` | Obtener reporte mensual | ✅ |
| `test_get_monthly_report_summary` | Verificar cálculos del resumen | ✅ |
| `test_export_monthly_csv` | Exportar CSV mensual | ✅ |
| `test_get_weekly_report` | Obtener reporte semanal | ✅ |
| `test_export_weekly_csv` | Exportar CSV semanal | ✅ |
| `test_close_weekly_summary` | Cerrar semana con testigos | ✅ |

### Módulo de Gastos

| Test | Descripción | Estado |
|------|-------------|--------|
| `test_list_categories` | Listar categorías | ✅ |
| `test_create_category` | Crear categoría | ✅ |
| `test_create_tag` | Crear etiqueta | ✅ |
| `test_create_expense` | Crear gasto | ✅ |
| `test_approve_expense` | Aprobar gasto | ✅ |
| `test_pay_expense` | Marcar pagado | ✅ |
| `test_cancel_expense` | Cancelar gasto | ✅ |
| `test_expense_summary` | Resumen de gastos | ✅ |
| `test_monthly_expense_report` | Reporte mensual | ✅ |
| `test_export_expenses_csv` | Exportar CSV | ✅ |

## Prevención de Falsos Positivos

### 1. Aislamiento de Tests

```python
@pytest.fixture(autouse=True)
async def clean_database():
    """Limpiar DB antes de cada test"""
    async with AsyncSessionLocal() as session:
        for table in reversed(Base.metadata.sorted_tables):
            await session.execute(table.delete())
        await session.commit()
```

### 2. Datos Únicos

```python
def unique_email():
    return f"test_{uuid.uuid4().hex[:8]}@test.com"
```

### 3. Timeouts

```python
@pytest.mark.timeout(10)
async def test_slow_operation():
    # Test que podría colgar
```

## Cobertura de Tests

### Generar Reporte

```bash
pytest --cov=app --cov-report=html --cov-report=term-missing
```

### Objetivos de Cobertura

| Módulo | Objetivo | Estado |
|--------|----------|--------|
| Routes | 90% | ✅ |
| Services | 85% | ✅ |
| Repositories | 80% | ✅ |
| Models | 70% | ✅ |
| Core | 90% | ✅ |
| Donation Reports | 85% | ✅ |
| Expenses | 85% | ✅ |

## Checklist de Tests

### Antes de Commit

- [ ] Todos los tests pasan localmente
- [ ] No hay tests con `@pytest.mark.skip` sin razón
- [ ] Nuevas funcionalidades tienen tests
- [ ] Tests de integración verifican respuestas completas

### Antes de Release

- [ ] Tests E2E pasan con contenedores reales
- [ ] Tests de integración frontend-backend pasan
- [ ] Cobertura >= 80%
- [ ] No hay warnings de deprecation

## Ejecutar Suite Completa

```bash
# 1. Levantar contenedores
docker-compose up -d

# 2. Esperar a que estén listos
sleep 10

# 3. Ejecutar todos los tests
docker exec -it ekklesia_backend pytest -v --tb=short

# 4. Ver resultados
echo "Tests completados"
```

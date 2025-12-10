# Estrategia de Testing

## Estructura de Tests

```
tests/
├── test_health.py              # Tests unitarios de health
├── test_security.py            # Tests de hashing y JWT
├── test_auth_flow.py           # Tests de autenticación
├── test_users_admin.py         # Tests de gestión de usuarios
├── test_donations.py           # Tests de donaciones
├── test_documents.py           # Tests de documentos
├── test_events.py              # Tests de eventos e inscripciones
├── test_reports.py             # Tests de reportes
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

### 3. Tests End-to-End

Prueban flujos completos de usuario.

```python
# test_e2e_flow.py
@pytest.mark.e2e
async def test_complete_donation_flow():
    # 1. Registrar usuario
    # 2. Login
    # 3. Crear donación
    # 4. Subir documento
    # 5. Descargar documento
    # 6. Ver reporte
```

### 4. Tests de Integración Frontend-Backend

Prueban la conexión real entre contenedores.

```python
# test_integration_endpoints.py
class TestFrontendConnection:
    @pytest.mark.asyncio
    async def test_frontend_loads(self):
        async with httpx.AsyncClient() as client:
            response = await client.get("http://localhost:3000")
            assert response.status_code == 200
```

## Ejecutar Tests

### Requisitos

```bash
pip install pytest pytest-asyncio httpx
```

### Comandos

```bash
# Todos los tests
pytest -v

# Solo tests unitarios
pytest tests/test_security.py tests/test_health.py -v

# Solo tests de integración
pytest tests/test_auth_flow.py tests/test_donations.py -v

# Tests E2E (requiere DB)
pytest tests/test_e2e_flow.py -v

# Tests de integración frontend-backend (requiere contenedores)
pytest tests/test_integration_endpoints.py -v

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
@pytest.fixture
async def async_client():
    """Cliente HTTP para tests de API"""
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test"
    ) as client:
        yield client

@pytest.fixture
async def auth_headers(async_client):
    """Headers con token de autenticación"""
    # Registrar y login
    await async_client.post("/api/auth/register", json=TEST_USER)
    response = await async_client.post("/api/auth/login", json=LOGIN_DATA)
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}
```

## Base de Datos de Tests

### SQLite en Memoria

Para tests unitarios y de integración:

```python
# Override de sesión para tests
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

@pytest.fixture(autouse=True)
async def setup_database():
    engine = create_async_engine(TEST_DATABASE_URL)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
```

### PostgreSQL de Tests

Para tests E2E con Docker:

```yaml
# docker-compose.test.yml
services:
  test_db:
    image: postgres:15-alpine
    environment:
      POSTGRES_DB: ekklesia_test
```

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

### 4. Retries para Flaky Tests

```python
@pytest.mark.flaky(reruns=3, reruns_delay=1)
async def test_potentially_flaky():
    # Test que puede fallar por timing
```

## Cobertura de Tests

### Generar Reporte

```bash
pytest --cov=app --cov-report=html --cov-report=term-missing
```

### Objetivos de Cobertura

| Módulo | Objetivo | Actual |
|--------|----------|--------|
| Routes | 90% | ✅ |
| Services | 85% | ✅ |
| Repositories | 80% | ✅ |
| Models | 70% | ✅ |
| Core | 90% | ✅ |

## CI/CD Integration

### GitHub Actions

```yaml
# .github/workflows/ci.yml
jobs:
  test:
    runs-on: ubuntu-latest
    services:
      postgres:
        image: postgres:15-alpine
        env:
          POSTGRES_USER: test
          POSTGRES_PASSWORD: test
          POSTGRES_DB: test
    steps:
      - uses: actions/checkout@v3
      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - name: Install dependencies
        run: pip install -r requirements.txt
      - name: Run tests
        run: pytest -v --tb=short
```

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

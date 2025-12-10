# Guía de Contribución

## Configuración del Entorno de Desarrollo

### Requisitos

- Python 3.11+
- Docker y Docker Compose
- Git

### Setup Local

```bash
# Clonar repositorio
git clone <repository-url>
cd GestionEcleseastica

# Crear entorno virtual
python -m venv venv
source venv/bin/activate  # Linux/Mac
.\venv\Scripts\activate   # Windows

# Instalar dependencias
pip install -r requirements.txt

# Levantar servicios
docker-compose up -d
```

## Estructura del Código

```
app/
├── api/
│   ├── routes/      # Endpoints HTTP
│   ├── schemas/     # Esquemas Pydantic
│   ├── services/    # Lógica de negocio
│   └── repositories/# Acceso a datos
├── core/            # Config, security, deps
├── db/              # Sesión y SQL
└── models/          # Modelos SQLAlchemy
```

## Convenciones

### Código Python

- **Estilo**: PEP 8
- **Formateo**: Black
- **Imports**: isort
- **Type hints**: Obligatorios en funciones públicas

```python
# ✅ Correcto
async def create_donation(
    session: AsyncSession,
    data: DonationCreate
) -> Donation:
    ...

# ❌ Incorrecto
async def create_donation(session, data):
    ...
```

### Commits

Formato: `<tipo>: <descripción>`

Tipos:
- `feat`: Nueva funcionalidad
- `fix`: Corrección de bug
- `docs`: Documentación
- `style`: Formateo (sin cambio de lógica)
- `refactor`: Refactorización
- `test`: Tests
- `chore`: Tareas de mantenimiento

```bash
git commit -m "feat: agregar endpoint de exportación CSV"
git commit -m "fix: corregir validación de email duplicado"
git commit -m "docs: actualizar API_SPEC con nuevos endpoints"
```

### Branches

- `main`: Producción
- `develop`: Desarrollo
- `feature/<nombre>`: Nuevas funcionalidades
- `fix/<nombre>`: Correcciones
- `docs/<nombre>`: Documentación

## Flujo de Desarrollo

### 1. Crear Branch

```bash
git checkout develop
git pull origin develop
git checkout -b feature/mi-funcionalidad
```

### 2. Desarrollar

```bash
# Hacer cambios
# Ejecutar tests
pytest -v

# Verificar linting
# black app/
# isort app/
```

### 3. Commit y Push

```bash
git add .
git commit -m "feat: descripción del cambio"
git push origin feature/mi-funcionalidad
```

### 4. Pull Request

1. Crear PR hacia `develop`
2. Descripción clara del cambio
3. Esperar revisión
4. Merge tras aprobación

## Testing

### Ejecutar Tests

```bash
# Todos los tests
pytest -v

# Con cobertura
pytest --cov=app --cov-report=html

# Test específico
pytest tests/test_donations.py -v
```

### Escribir Tests

```python
# tests/test_mi_feature.py
import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_mi_funcionalidad(async_client):
    response = await async_client.post("/api/endpoint", json={...})
    assert response.status_code == 201
    assert response.json()["campo"] == "valor"
```

## Documentación

### Actualizar Docs

Al agregar nuevas funcionalidades, actualizar:

1. `API_SPEC.md` - Nuevos endpoints
2. `DATABASE_SCHEMA.md` - Cambios en DB
3. `CHANGELOG.md` - Registro del cambio
4. Docstrings en código

### Formato de Docstrings

```python
async def create_donation(
    session: AsyncSession,
    user_id: int,
    data: dict
) -> Donation:
    """
    Crea una nueva donación.

    Args:
        session: Sesión de base de datos
        user_id: ID del usuario que registra
        data: Datos de la donación

    Returns:
        Donación creada

    Raises:
        HTTPException: Si los datos son inválidos
    """
    ...
```

## Código de Conducta

- Respeto mutuo
- Comunicación constructiva
- Enfoque en soluciones
- Documentar decisiones importantes

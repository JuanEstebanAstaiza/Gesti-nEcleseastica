# Issues Encontrados y Resueltos

## Resumen

| Categoría | Encontrados | Resueltos | Pendientes |
|-----------|-------------|-----------|------------|
| Errores de Código | 10 | 10 | 0 |
| Warnings | 4 | 4 | 0 |
| Mejoras | 6 | 6 | 0 |

---

## Errores Resueltos

### 1. ModuleNotFoundError: No module named 'app'

**Descripción**: Al ejecutar pytest, no encontraba el módulo `app`.

**Causa**: El directorio raíz no estaba en el PYTHONPATH durante los tests.

**Solución**: Agregar `conftest.py` con manipulación de `sys.path`:

```python
# app/tests/conftest.py
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
```

**Estado**: ✅ Resuelto

---

### 2. SQLAlchemy ArgumentError con Pydantic URL

**Descripción**: `Expected string or URL object, got Url(...)`

**Causa**: Pydantic `AnyUrl` no es directamente compatible con SQLAlchemy.

**Solución**: Convertir explícitamente a string:

```python
engine = create_async_engine(str(settings.database_url), ...)
```

**Estado**: ✅ Resuelto

---

### 3. async_generator object has no attribute 'post'

**Descripción**: Error al usar fixture async_client en tests.

**Causa**: Scope mismatch entre fixture y event loop.

**Solución**: Cambiar scope de fixture a `function` y configurar pytest.ini:

```ini
asyncio_default_fixture_loop_scope = function
```

**Estado**: ✅ Resuelto

---

### 4. Endpoint de documentos retornaba 404

**Descripción**: POST /documents retornaba 404.

**Causa**: Router no incluido en el agregador.

**Solución**: Agregar router en `app/api/routes/__init__.py`:

```python
router.include_router(documents.router)
```

**Estado**: ✅ Resuelto

---

### 5. NameError: datetime not defined

**Descripción**: Error en schema de registration.

**Causa**: Faltaba import de datetime.

**Solución**: Agregar import:

```python
from datetime import date, datetime
```

**Estado**: ✅ Resuelto

---

### 6. SyntaxError en test_reports_dashboard.py

**Descripción**: Paréntesis no coincidentes en definición de diccionario.

**Causa**: Error de sintaxis al editar el archivo.

**Solución**: Corregir la definición de `member_headers`.

**Estado**: ✅ Resuelto

---

### 7. ImportError: email-validator not installed

**Descripción**: Pydantic no podía validar EmailStr.

**Causa**: Faltaba dependencia email-validator.

**Solución**: Actualizar requirements.txt:

```
pydantic[email]==2.9.0
```

**Estado**: ✅ Resuelto

---

### 8. ValueError: password cannot be longer than 72 bytes

**Descripción**: Error al hashear contraseñas largas con bcrypt.

**Causa**: Problema de compatibilidad con python-jose y bcrypt.

**Solución**: Actualizar python-jose con cryptography:

```
python-jose[cryptography]==3.3.0
```

**Estado**: ✅ Resuelto

---

### 9. ProgrammingError: operator does not exist: integer = character varying

**Descripción**: Error al buscar usuario por ID en deps.py.

**Causa**: `user_id` del JWT era string, pero la columna es integer.

**Solución**: Castear explícitamente a int:

```python
user_id = int(payload.get("sub"))
```

**Estado**: ✅ Resuelto

---

### 10. Registration Status: 422

**Descripción**: Error al crear inscripciones a eventos.

**Causa**: `event_id` duplicado en schema y path parameter.

**Solución**: Remover `event_id` de `RegistrationCreate`:

```python
class RegistrationCreate(BaseModel):
    # event_id viene del path, no del body
    attendee_name: str
    attendee_email: str
    notes: str | None = None
```

**Estado**: ✅ Resuelto

---

## Warnings Resueltos

### 1. PytestDeprecationWarning: asyncio_default_fixture_loop_scope unset

**Solución**: Configurar en pytest.ini:

```ini
asyncio_default_fixture_loop_scope = function
```

**Estado**: ✅ Resuelto

---

### 2. DeprecationWarning: ASGITransport

**Descripción**: El shortcut `app=` está deprecado.

**Solución**: Usar forma explícita:

```python
transport = ASGITransport(app=app)
async with AsyncClient(transport=transport, ...) as client:
```

**Estado**: ✅ Resuelto

---

### 3. PydanticDeprecatedSince20: class Config

**Descripción**: `class Config` está deprecado en Pydantic V2.

**Solución**: Migrar a ConfigDict:

```python
model_config = ConfigDict(from_attributes=True)
```

**Estado**: ✅ Resuelto

---

### 4. PydanticDeprecatedSince20: dict() method

**Descripción**: `.dict()` está deprecado.

**Solución**: Usar `.model_dump()`:

```python
data = payload.model_dump()
```

**Estado**: ✅ Resuelto

---

## Mejoras Implementadas

### 1. Separación Frontend/Backend

**Problema**: Frontend y backend compartían puerto (brecha de seguridad).

**Mejora**: Contenedores separados con puertos distintos:
- Frontend: Nginx en puerto 3000
- Backend: FastAPI en puerto 6076

**Estado**: ✅ Implementado

---

### 2. Diseño del Frontend

**Problema**: Frontend básico sin estética moderna.

**Mejora**: Rediseño completo con:
- Tema oscuro elegante
- Componentes inspirados en Stripe/Instagram
- Responsive design
- Animaciones y transiciones

**Estado**: ✅ Implementado

---

### 3. Documentación Completa

**Problema**: Documentación desactualizada e incompleta.

**Mejora**: Actualización de todos los documentos:
- README con instrucciones claras
- ARCHITECTURE con diagramas
- API_SPEC completa
- Guías de testing y deployment

**Estado**: ✅ Implementado

---

### 4. Formato de Donaciones para Contaduría

**Problema**: Formato de donación no coincidía con el formato oficial de la iglesia.

**Mejora**: Modelo actualizado con:
- Montos separados (Diezmo, Ofrenda, Misiones, Especial)
- Datos completos del donante (Nombre, Cédula, Dirección, Teléfono)
- Soporte para efectivo y transferencia simultáneos
- Número de sobre y semana
- Donaciones anónimas (OSI)

**Estado**: ✅ Implementado

---

### 5. Reportes para Contadora

**Problema**: No existía un formato de reporte para la contadora de la iglesia.

**Mejora**: Implementación de reportes:
- Reporte mensual CSV con formato de Excel
- Reporte semanal con tabla CONCEPTO | EFECTIVO | TRANSFERENCIA | TOTAL
- Cálculo automático de "Diezmo de diezmos"
- Cierre semanal con testigos

**Estado**: ✅ Implementado

---

### 6. Módulo de Gastos

**Problema**: No existía gestión de gastos de la iglesia.

**Mejora**: Módulo completo con:
- Categorías y subcategorías personalizables
- Etiquetas para clasificación
- Flujo de aprobación (Pendiente → Aprobado → Pagado)
- Documentos de soporte
- Presupuesto mensual por categoría
- Reportes de gastos

**Estado**: ✅ Implementado

---

## Issues Conocidos (No Críticos)

### 1. Frontend pendiente de actualización

**Descripción**: El frontend necesita actualizarse para reflejar los nuevos módulos de donaciones y gastos.

**Impacto**: Medio - El backend está listo, falta la interfaz de usuario.

**Plan**: Actualizar formularios y vistas en próxima iteración.

---

### 2. Gráficos no implementados

**Descripción**: El dashboard muestra datos pero no gráficos visuales.

**Impacto**: Bajo - La funcionalidad existe, solo falta visualización.

**Plan**: Implementar con Chart.js en próxima iteración.

---

### 3. Paginación no implementada en frontend

**Descripción**: Listados grandes podrían ser lentos.

**Impacto**: Bajo - El backend soporta paginación, falta implementar en UI.

**Plan**: Agregar controles de paginación en próxima iteración.

---

### 4. Internacionalización pendiente

**Descripción**: Solo español, sin soporte para inglés.

**Impacto**: Bajo - Funcionalidad completa en español.

**Plan**: Implementar sistema i18n en futuras versiones.

---

### 5. Multi-tenant parcialmente implementado

**Descripción**: La arquitectura multi-tenant está diseñada pero no completamente funcional.

**Impacto**: Medio - Requerido para producción con múltiples iglesias.

**Plan**: Completar en Fase 9.

---

### 6. Panel de Super Admin pendiente

**Descripción**: Falta la interfaz para gestionar tenants y churches.

**Impacto**: Medio - Necesario para administración de la plataforma.

**Plan**: Implementar en Fase 9.

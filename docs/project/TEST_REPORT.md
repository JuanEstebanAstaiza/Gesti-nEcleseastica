# Reporte de Pruebas

## Fecha: 2024-12-10

## Resumen de Ejecución

| Categoría | Pasaron | Fallaron | Total |
|-----------|---------|----------|-------|
| Básicos (health, security) | 4 | 0 | 4 |
| Autenticación | 1 | 0 | 1 |
| Documentos | 1 | 0 | 1 |
| Eventos | 1 | 0 | 1 |
| Usuarios Admin | 1 | 0 | 1 |
| Donaciones | 0 | 2 | 2 |
| Reportes Donaciones | 1 | 6 | 7 |
| Gastos | 0 | 18 | 18 |
| E2E | 0 | 1 | 1 |
| Reportes Legacy | 0 | 2 | 2 |
| **TOTAL** | **9** | **29** | **38** |

## Tests que Pasaron ✅

### Unitarios
1. `test_health_returns_ok` - Verificación del endpoint de health
2. `test_password_hash_and_verify` - Hashing y verificación de contraseñas
3. `test_access_and_refresh_token_scopes` - Generación y scopes de tokens JWT

### Integración
4. `test_register_login_and_me` - Flujo completo de registro → login → perfil
5. `test_upload_and_download_document` - Subida y descarga de documentos
6. `test_events_admin_vs_public` - Permisos de admin vs público en eventos
7. `test_admin_can_manage_users_and_member_cannot` - RBAC de usuarios

### Reportes
8. `test_get_monthly_report_unauthorized` - Verificación de autenticación requerida

## Tests que Fallaron ❌

### Causa Principal: Endpoints No Implementados

Los siguientes endpoints aún no están implementados en el backend:

#### Reportes de Donaciones
- `GET /api/reports/donations/monthly` - Reporte mensual JSON
- `GET /api/reports/donations/monthly/csv` - Exportar CSV mensual
- `GET /api/reports/donations/weekly/{week}` - Reporte semanal
- `GET /api/reports/donations/weekly/{week}/csv` - Exportar CSV semanal
- `POST /api/reports/donations/weekly/close` - Cerrar semana

#### Módulo de Gastos
- `GET /api/expenses/categories` - Listar categorías
- `POST /api/expenses/categories` - Crear categoría
- `GET /api/expenses/tags` - Listar etiquetas
- `POST /api/expenses/tags` - Crear etiqueta
- `GET /api/expenses` - Listar gastos
- `POST /api/expenses` - Crear gasto
- `GET /api/expenses/{id}` - Obtener gasto
- `POST /api/expenses/{id}/approve` - Aprobar gasto
- `POST /api/expenses/{id}/pay` - Marcar pagado
- `DELETE /api/expenses/{id}` - Cancelar gasto
- `GET /api/expenses/reports/summary` - Resumen de gastos
- `GET /api/expenses/reports/monthly` - Reporte mensual
- `GET /api/expenses/reports/monthly/csv` - Exportar CSV

### Causa Secundaria: Formato de Payload Desactualizado

- `test_member_can_create_and_view_own_donations_but_not_list_all` - El payload de donaciones usa el formato antiguo (campo `amount`) en lugar del nuevo formato (campos separados).

## Errores y Advertencias Corregidos

### Durante la Sesión

1. **ModuleNotFoundError: aiosqlite**
   - Solución: Agregado `aiosqlite==0.20.0` a requirements.txt

2. **JSONB incompatible con SQLite**
   - Solución: Cambiado `JSONB` a `JSON` en modelo `Expense`

3. **AmbiguousForeignKeysError en User-Donation**
   - Solución: Especificado `foreign_keys` en la relación `User.donations`

### Advertencias Pendientes

1. **PytestDeprecationWarning: asyncio_default_fixture_loop_scope**
   - Acción: Agregar `asyncio_default_fixture_loop_scope = function` a pytest.ini

2. **DeprecationWarning: 'crypt' deprecated**
   - Acción: Actualizar passlib en futuras versiones (Python 3.13)

## Próximos Pasos

1. **Implementar endpoints de Reportes de Donaciones**
   - Crear `app/api/routes/donation_reports.py`
   - Crear `app/api/services/donation_report.py`
   - Crear `app/api/repositories/donation_report.py`

2. **Implementar endpoints de Gastos**
   - Crear `app/api/routes/expenses.py`
   - Crear `app/api/services/expense.py`
   - Crear `app/api/repositories/expense.py`

3. **Actualizar tests de donaciones**
   - Actualizar payload en `test_donations.py` con el nuevo formato

4. **Corregir advertencias de pytest**
   - Actualizar `pytest.ini` con la configuración de event loop

## Comandos de Ejecución

```bash
# Ejecutar todos los tests
docker exec ekklesia_backend pytest app/tests/ -v --tb=short

# Solo tests que pasan actualmente
docker exec ekklesia_backend pytest app/tests/test_health.py app/tests/test_security.py app/tests/test_auth_flow.py app/tests/test_documents.py app/tests/test_events.py app/tests/test_users_admin.py -v

# Con cobertura
docker exec ekklesia_backend pytest app/tests/ --cov=app --cov-report=term-missing
```

## Conclusión

Se ha completado:
- ✅ Actualización del frontend con nuevos formularios
- ✅ Modelos de donaciones y gastos actualizados
- ✅ Pruebas unitarias escritas (modelos y fixtures)
- ✅ Corrección de errores de compatibilidad SQLite/PostgreSQL
- ✅ Documentación de pruebas actualizada

Queda pendiente:
- ⏳ Implementación de endpoints de reportes y gastos
- ⏳ Actualización de tests legacy con nuevo formato
- ⏳ Multi-tenant (Fase 9)


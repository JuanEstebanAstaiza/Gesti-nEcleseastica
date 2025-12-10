# Testing

## Enfoque
- Unit tests: atómicos, sin depender de DB real (fixtures con SQLite/mocks).
- Integración: PostgreSQL de prueba (contenedor), limpiar estado por transacción o reconstrucción de schema.
- E2E: flujo completo (registro → login → crear donación con comprobante → descargar comprobante → reporte). Usar httpx + navegador headless o Playwright; incluir retries limitados en pasos frágiles.

## Comandos (fase actual)
- Unit/integración (usa SQLite en memoria vía overrides):
  ```bash
  pytest
  ```
- E2E (plan futuro):
  ```bash
  pytest -m e2e
  ```

## Setup de pruebas
- Variables: usar `.env.test` o inyectar vars en CI.
- DB test: contenedor PostgreSQL aislado; aplicar `app/db/sql/initial_schema.sql` antes de las pruebas de integración/E2E.

## Anti-flaky
- Healthcheck del servicio antes de iniciar E2E.
- Retries limitados con backoff en pasos dependientes de tiempo (ej. espera de subida).
- Asserts con tolerancia razonable en métricas.

## Estado actual
- Pruebas implementadas:
  - Healthcheck (`app/tests/test_health.py`).
  - Seguridad: hashing/JWT scopes (`app/tests/test_security.py`).
  - Flujo auth (register/login/me) con SQLite en memoria y override de sesión (`app/tests/test_auth_flow.py`).
  - Administración de usuarios (admin vs member) (`app/tests/test_users_admin.py`).
  - Donaciones: creación, listado propio y restricción admin para listado global (`app/tests/test_donations.py`).
  - Documentos: subida y descarga con storage aislado en pruebas (`app/tests/test_documents.py`).
  - Eventos e inscripciones básicas: creación admin y registro público, listado (`app/tests/test_events.py`).
  - E2E (`app/tests/test_e2e_flow.py`): registro → login → donación → carga/descarga de comprobante → reporte resumen admin.
  - Reportes: summary con filtros y dashboard, export CSV (`app/tests/test_reports.py`, `app/tests/test_reports_dashboard.py`, `app/tests/test_reports_export.py`).
- Ajustes anti-warning: httpx usa `ASGITransport` en tests; loop scope configurado en `pytest.ini`.
- Advertencias pendientes: migrar cualquier Config heredada a ConfigDict y usar `model_dump` en esquemas restantes.
- Próximos tests: E2E completos (registro → login → donación con comprobante → descarga → reporte) y flujo de inscripciones cuando se implemente.


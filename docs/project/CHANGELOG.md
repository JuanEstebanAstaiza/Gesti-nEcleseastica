- Suite de eventos/inscripciones añadida; reporte resumen admin disponible.
# Changelog

## [0.1.4] - 2025-12-10
- E2E básico agregado (registro → donación → comprobante → reporte admin).
- Inscripciones a eventos, reporte resumen y script `scripts/apply_schema.sh`.
- Suite total: 10 pruebas (incluye E2E y reglas de inscripciones).
- Frontend ahora usa token real tras login para acciones protegidas.

## [0.1.3] - 2025-12-10
- CRUD de usuarios protegido por rol admin (listar, ver, actualizar, eliminar).
- Nueva capa de dependencias con `require_admin` e inactividad bloqueada.
- Tests ampliados (8 en total) incluyendo flujo admin vs member, donaciones, documentos, eventos; uso de ASGITransport y scope de loop configurado.
- Pytest.ini añadido para control de loop scope.
- Frontend enriquecido con iconografía (Feather) y chips visuales.
- Donaciones: endpoints creados (crear, listar propias, listar todas solo admin) y prueba asociada.
- Documentos: subida/descarga con validación de tamaño/MIME, checksum, y prueba asociada.
- Eventos: creación (admin) y listado público; reporte resumen admin (`/reports/summary`).

## [0.1.2] - 2025-12-10
- Implementados endpoints de autenticación (register/login/refresh) y `/users/me`.
- Añadida capa de seguridad (hashing bcrypt, JWT access/refresh).
- Suite de pruebas inicial ampliada (health, seguridad, auth flow con SQLite in-memory) y ejecutada con éxito.
- Ajustes de config a `pydantic-settings`; fixes en URL de DB.
- Frontend moderno mantenido; puerto 6076 vigente.

## [0.1.1] - 2025-12-10
- Puerto del backend ajustado a 6076 (Dockerfile y docker-compose).
- Agregada prueba inicial de healthcheck (pytest).
- Frontend renovado con estilo moderno (sin frameworks pesados).
- Documentación reubicada bajo `docs/` y actualizada (puerto, tests).

## [0.1.0] - 2025-12-10
- Fase de diseño y setup inicial.
- Estructura base backend/frontend creada.
- Endpoint `/api/health`.
- Modelos iniciales: users, donations, documents, events.
- Eliminado Alembic; migraciones manuales vía SQL (`app/db/sql/initial_schema.sql`).
- Dockerfile y docker-compose listos para entorno local.


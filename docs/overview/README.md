# Ekklesia Admin

Plataforma web ligera para gestión administrativa eclesiástica: donaciones, eventos, inscripciones y trazabilidad documental, con frontend en HTML/CSS/JS puro y backend FastAPI sobre PostgreSQL.

## Requisitos
- Python 3.11+
- Docker y Docker Compose
- PostgreSQL (usado mediante `docker-compose`)

## Configuración rápida
1. Copia `.env.example` a `.env` y ajusta valores sensibles.
2. Levanta la base y el backend (expuesto en puerto 6076):
   ```bash
   docker-compose up --build
   ```
3. Aplica el esquema inicial (sin Alembic):
   ```bash
   docker exec -i ekklesia_db psql -U ${POSTGRES_USER:-ekklesia} -d ${POSTGRES_DB:-ekklesia} -f /code/app/db/sql/initial_schema.sql
   ```
4. Accede al frontend estático en `http://localhost:6076` (assets) y al backend en `http://localhost:6076/api/health`.

## Estructura principal
```
app/           # Backend FastAPI (routers, servicios, repos, modelos)
frontend/      # HTML/CSS/JS puro
app/db/sql/    # Scripts SQL de esquema inicial (sin Alembic)
docs/          # Documentación adicional
```

## Estado actual
- Backend con healthcheck, auth (register/login/refresh), `/users/me`, CRUD de usuarios (solo admin), donaciones (crear, mis donaciones, listar todas solo admin), documentos (subir/descargar/listar admin) con validación de tamaño/MIME y checksum, eventos (crear admin, listar público), inscripciones con cupo/duplicados/cancelación, reportes (summary, dashboard, export CSV) y WebSocket autenticado de notificaciones; modelos base (users, donations, documents, events).
- Frontend estático renovado (estilo glassy) con formularios demo y uso de token real tras login.
- Sin migraciones automáticas; se usan scripts SQL manuales.

## Próximos pasos
- Implementar autenticación JWT y CRUD de usuarios/donaciones/documentos/eventos.
- Añadir servicios, repositorios y rutas siguiendo la capa definida.
- Agregar pruebas unitarias, integración y E2E.

## Documentación relacionada
- Arquitectura: `docs/architecture/ARCHITECTURE.md`
- API: `docs/api/API_SPEC.md`
- Base de datos: `docs/db/DATABASE_SCHEMA.md`
- Seguridad: `docs/security/SECURITY.md`
- Testing: `docs/testing/TESTING.md`
- Despliegue: `docs/deployment/DEPLOYMENT.md`
- Proyecto/meta: `docs/project/PHASES.md`, `CHANGELOG.md`, `issues_found.md`, `CONTRIBUTING.md`, `GLOSSARY.md`, `LICENSE_INFO.md`


# Ekklesia Admin

Documentación organizada en `docs/`:
- `docs/overview/README.md` (guía principal)
- `docs/architecture/ARCHITECTURE.md`
- `docs/api/API_SPEC.md`
- `docs/db/DATABASE_SCHEMA.md`
- `docs/security/SECURITY.md`
- `docs/testing/TESTING.md`
- `docs/deployment/DEPLOYMENT.md`
- `docs/project/CHANGELOG.md`, `PHASES.md`, `issues_found.md`, etc.

Para empezar rápido, consulta `docs/overview/README.md`.
# Ekklesia Admin

Plataforma web ligera para gestión administrativa eclesiástica: donaciones, eventos, inscripciones y trazabilidad documental, con frontend en HTML/CSS/JS puro y backend FastAPI sobre PostgreSQL.

## Requisitos
- Python 3.11+
- Docker y Docker Compose
- PostgreSQL (usado mediante `docker-compose`)

## Configuración rápida
1. Copia `.env.example` a `.env` y ajusta valores sensibles.
2. Levanta la base y el backend:
   ```bash
   docker-compose up --build
   ```
3. Aplica el esquema inicial (sin Alembic):
   ```bash
   docker exec -i ekklesia_db psql -U ${POSTGRES_USER:-ekklesia} -d ${POSTGRES_DB:-ekklesia} -f /code/app/db/sql/initial_schema.sql
   ```
4. Accede al frontend estático en `http://localhost:8000` (serving simple assets) y al backend en `http://localhost:8000/api/health`.

## Estructura principal
```
app/           # Backend FastAPI (routers, servicios, repos, modelos)
frontend/      # HTML/CSS/JS puro
app/db/sql/    # Scripts SQL de esquema inicial (sin Alembic)
docs/          # Documentación adicional
```

## Estado actual
- Backend con endpoint de salud y modelos base (users, donations, documents, events).
- Frontend estático mínimo con formularios de login, donaciones y carga de documentos (modo demo).
- Sin migraciones automáticas; se usan scripts SQL manuales.

## Próximos pasos
- Implementar autenticación JWT y CRUD de usuarios/donaciones/documentos/eventos.
- Añadir servicios, repositorios y rutas siguiendo la capa definida.
- Agregar pruebas unitarias, integración y E2E.


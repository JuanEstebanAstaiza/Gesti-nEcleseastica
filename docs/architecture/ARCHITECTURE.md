# Arquitectura

## Visión general
Frontend ligero en HTML/CSS/JS (sin frameworks) que consume un backend FastAPI estructurado por capas: `routers -> services -> repositories -> models -> db`. Persistencia en PostgreSQL, orquestado con Docker Compose. Almacenamiento de archivos local (`./storage`) con opción futura S3-compatible.

## Diagrama ASCII
```
[Frontend JS] --HTTP--> [FastAPI Routers] --> [Services] --> [Repositories] --> [SQLAlchemy Models] --> [PostgreSQL]
                                             |
                                             --> [Storage: filesystem/S3]
```

## Decisiones clave
- FastAPI + SQLAlchemy async con asyncpg.
- Sin Alembic: migraciones manuales con scripts SQL (`app/db/sql/initial_schema.sql`).
- JWT (access/refresh) planificado; aún sin implementar.
- Validaciones con Pydantic en entrada/salida.
- Estructura modular y separada por capas para mantenibilidad.

## Módulos
- `app/api/routes`: puntos de entrada HTTP.
- `app/api/services`: lógica de negocio.
- `app/api/repositories`: acceso a datos.
- `app/models`: entidades ORM.
- `app/core`: configuración global.
- `app/db/sql`: scripts SQL manuales.
- `frontend`: assets estáticos.


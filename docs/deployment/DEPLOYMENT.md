# Despliegue

## Dependencias
- Docker y Docker Compose
- Archivo `.env` con credenciales y claves.

## Pasos básicos
1. Copiar `.env.example` a `.env` y ajustar.
2. Levantar servicios (web expone 6076):
   ```bash
   docker-compose up --build -d
   ```
3. Aplicar esquema inicial:
   ```bash
   docker exec -i ekklesia_db psql -U ${POSTGRES_USER:-ekklesia} -d ${POSTGRES_DB:-ekklesia} -f /code/app/db/sql/initial_schema.sql
   # o usar script helper
   POSTGRES_HOST=localhost POSTGRES_PORT=5432 ./scripts/apply_schema.sh
   ```
4. CI sugerido: usar `.github/workflows/ci.yml` para instalar deps, aplicar schema a servicio Postgres y correr `pytest`.

## Contenedores
- `db`: PostgreSQL 15.
- `web`: FastAPI + frontend estático, monta `./storage` para archivos, expuesto en `6076`.

## Volúmenes y backups
- `pgdata`: datos persistentes de PostgreSQL. Realizar backups periódicos (`pg_dump`) y almacenar fuera del host.
- `./storage`: soportes subidos. Respaldar y versionar según política.

## Red y seguridad
- Exponer 8000/tcp (backend) y 5432/tcp (DB) solo en redes controladas.
- Para producción, colocar reverse proxy con HTTPS (nginx/traefik) y deshabilitar `--reload`.

## Migraciones
- No se usa Alembic. Ejecutar scripts SQL versionados en `app/db/sql/`.

## CI/CD (esbozo)
- Jobs: lint + tests unitarios/integración + build de imagen.
- Publicar imagen versionada en registry privado.


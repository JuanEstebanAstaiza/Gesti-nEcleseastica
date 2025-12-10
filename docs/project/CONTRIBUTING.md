# Contribuir

## Flujo propuesto
- Crear rama feature/bugfix desde main.
- Mantener cambios pequeños y enfocados; preferir PRs cortos.
- Actualizar documentación relevante en cada cambio (README, API_SPEC, etc.).
- Añadir pruebas unitarias/integración para nuevas funcionalidades.

## Estilo
- Backend: tipado, Pydantic para DTOs, servicios/repositorios claros.
- Frontend: JS modular (ES6), sin frameworks.
- Commits: mensajes claros en español.

## Migraciones
- No usar Alembic. Versionar scripts SQL en `app/db/sql/` numerados o fechados.

## Revisiones
- Priorizar seguridad (JWT, permisos, manejo de archivos).
- Revisar que `.env` no se incluya en commits.


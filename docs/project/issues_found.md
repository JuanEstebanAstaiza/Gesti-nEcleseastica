# Issues encontrados (Fase 1-4)
- Pruebas actuales (10) pasan; falta dashboard/reportes avanzados y WS opcional. Acción: diseñar métricas adicionales.
- Migraciones manuales; automatización pendiente para CI (aplicar SQL antes de tests). Acción: usar `scripts/apply_schema.sh` en pipeline.
- Deprecaciones Pydantic: migrar ConfigDict/model_dump en cualquier esquema/flujos restantes (mínimas).


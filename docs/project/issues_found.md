# Issues encontrados (Fase 1-4)
- Pruebas actuales (11) pasan; quedan mejoras futuras (no bloqueantes): refinamiento de dashboard/reportes y WS con más eventos.
- Migraciones manuales; automatización parcialmente cubierta en CI (`apply_schema.sh`). Acciones futuras: extender pipeline a build de imagen/despliegue.
- Deprecaciones Pydantic: migrar ConfigDict/model_dump en cualquier esquema/flujos restantes (mínimas).


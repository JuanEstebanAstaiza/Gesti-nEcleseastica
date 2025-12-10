# Fases

## Fase 1 — Diseño & setup (en progreso)
- Objetivo: esqueleto del proyecto, contenedores, esquema inicial.
- Checklist: estructura creada ✅; esquema SQL inicial ✅; docs base ✅ (reubicadas en `docs/`); pruebas críticas ejecutadas ❌ (pendiente).

## Fase 2 — Autenticación y usuarios (casi completo)
- Objetivo: JWT access/refresh, roles, CRUD usuarios.
- Avances: endpoints auth/login/refresh/register, `/users/me`, CRUD de usuarios con requisito admin; 6 pruebas pasando; puerto 6076 operativo; frontend rediseñado base.
- Pendiente: autorización fina en otros módulos y CRUD documentos/eventos; extender pruebas E2E.

## Fase 3 — Donaciones, documentos y eventos (completado)
- Objetivo: CRUD donaciones con roles, carga de documentos y eventos/inscripciones.
- Avances: donaciones con roles, documentos con validación de MIME/tamaño, eventos (crear admin/listar público), inscripciones básicas y reportes resumen admin; 8 pruebas pasando.
- Pendiente: E2E completo y reportes avanzados; mejorar UX frontend consumiendo tokens reales.

## Fase 4 — E2E y automatización (en progreso)
- Objetivo: flujo completo E2E y script reproducible de schema.
- Avances: E2E básico agregado; script `scripts/apply_schema.sh`; frontend usa tokens tras login; inscripciones con cupo/duplicados/cancelación.
- Pendiente: reportes avanzados/dashboard y CI que ejecute apply_schema + tests.

## Fase 3 — Donaciones
- Objetivo: CRUD donaciones, filtros y export CSV.
- Hecho cuando: endpoints, validaciones, pruebas integración, actualización de dashboard inicial.

## Fase 4 — Documentos y almacenamiento
- Objetivo: subir/descargar soportes, trazabilidad, validaciones de tipo/tamaño.
- Hecho cuando: metadata en DB, almacenamiento seguro, tests, doc de seguridad.

## Fase 5 — Eventos e inscripciones
- Objetivo: CRUD eventos, inscripciones, vínculos con donaciones.
- Hecho cuando: endpoints y pruebas de flujo.

## Fase 6 — Dashboard y reportes
- Objetivo: métricas básicas, reportes por rango de fecha y tipo, internacionalización simple.
- Hecho cuando: endpoints/reportes y E2E de flujo principal.

## Fase 7 — E2E y performance
- Objetivo: flujos completos con soportes, backoff anti-flaky, pruebas de carga ligeras (opcional).
- Hecho cuando: suite E2E estable y documentación de ejecución en CI.

## Fase 8 — Endurecimiento y despliegue
- Objetivo: hardening, backups, monitoreo, checklist de producción.
- Hecho cuando: despliegue reproducible, SECURITY/DEPLOYMENT actualizados, backups probados.


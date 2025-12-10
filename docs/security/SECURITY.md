# Seguridad

## Autenticación y autorización
- JWT (access/refresh) implementado para `/auth/login`, `/auth/refresh` y protección de `/users/me`.
- Rutas de administración de usuarios, donaciones globales, documentos globales y reportes requieren rol `admin`.
- Roles mínimos: `public`, `member`, `admin`; autorización aplicada en usuarios/donaciones/documentos/reportes; pendiente extensiones futuras para inscripciones.
- Usuarios inactivos no pueden autenticarse (respuesta 403).
## Websocket
- Canal `/ws/notifications` requiere `token` (access JWT) en query; envía bienvenida y notificaciones `donation.created` y `event.created`. Usar solo en redes de confianza; considerar token corto/rotación si se expone.

## Manejo de archivos
- Tipos permitidos: PDF, JPG, PNG; tamaño máximo configurable (`MAX_UPLOAD_MB`).
- Almacenamiento local en `./storage` (montado en contenedor). Opcional S3-compatible vía variables.
- Metadata en `documents` (mime, tamaño, checksum, vínculos) guardada al subir.
- Validar MIME y extensión; checksum SHA-256 calculado; tamaños validados al subir.
- Acceso: admin o dueño; `is_public` permite acceso sin ser dueño pero requiere auth si no es público.

## Datos sensibles
- Variables en `.env`, nunca versionadas.
- `SECRET_KEY` y credenciales de DB deben cambiarse en cada entorno.

## Transporte
- Habilitar HTTPS en despliegue (reverse proxy recomendado; documentar en DEPLOYMENT).

## Logs y auditoría
- Registrar operaciones de carga/descarga de documentos y cambios de rol (pendiente instrumentación).
- Conservar número de documento y usuario asociado para auditoría.


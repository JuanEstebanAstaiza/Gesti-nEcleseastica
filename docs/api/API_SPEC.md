# Especificación de API

## Convenciones
- Base path backend: `/api` (servido en `http://localhost:6076`)
- Respuestas en JSON.
- Autenticación (planificada): JWT Bearer (access/refresh).

## Endpoints disponibles (Fase 2 parcial)

### Healthcheck
- `GET /api/health`
- 200 OK
```json
{ "status": "ok" }
```

### Autenticación
- `POST /api/auth/register`
  - body: `{ "email": "<email>", "password": "<str>", "full_name": "<str|null>", "role": "member|admin|public" }`
  - 201 Created → `UserRead`
- `POST /api/auth/login`
  - body: `{ "email": "<email>", "password": "<str>" }`
  - 200 OK → `{ "access_token": "<jwt>", "refresh_token": "<jwt>", "token_type": "bearer" }`
- `POST /api/auth/refresh`
  - body: `{ "refresh_token": "<jwt>" }`
  - 200 OK → tokens nuevos

### Usuarios
- `GET /api/users/me` (Bearer access token) → `UserRead`
- `GET /api/users` (admin) → `[UserRead]`
- `GET /api/users/{user_id}` (admin) → `UserRead`
- `PATCH /api/users/{user_id}` (admin)
  - body opcional: `full_name`, `role` (public|member|admin), `password`, `is_active`
  - 200 OK → `UserRead`
- `DELETE /api/users/{user_id}` (admin) → 204 No Content

### Donaciones
- `GET /api/donations` (admin) → `[DonationRead]`
- `GET /api/donations/me` (Bearer) → `[DonationRead]`
- `POST /api/donations` (Bearer)
  - body: `donor_name`, `donor_document?`, `donation_type (diezmo|ofrenda|misiones|especial)`, `amount`, `payment_method (efectivo|transferencia|tarjeta|otro)`, `note?`, `donation_date`, `event_id?`
  - 201 Created → `DonationRead`

### Documentos
- `POST /api/documents` (Bearer multipart/form-data)
  - fields: `file`, `link_type? (donation|user|event)`, `ref_id?`, `description?`, `is_public?`
  - 201 Created → `DocumentRead`
- `GET /api/documents/{id}` (Bearer si no es público; admin u owner) → archivo
- `GET /api/documents` (admin) → `[DocumentRead]`

### Eventos
- `POST /api/events` (admin) → `EventRead` (campos: name, description?, start_date?, end_date?, capacity?)
- `GET /api/events` → `[EventRead]`

### Inscripciones
- `POST /api/events/{event_id}/registrations` → `RegistrationRead` (valida duplicados por email y capacidad)
- `GET /api/events/{event_id}/registrations` (admin) → `[RegistrationRead]`

### Reportes
- `GET /api/reports/summary` (admin, filtros opcionales `start_date`, `end_date`, `donation_type`)
  - 200 OK → `{ "total_donations": int, "total_amount": float, "by_type": { "diezmo": n, ... }, "filters": {...} }`
- `GET /api/reports/dashboard` (admin) → agregados por mes y por tipo con filtros opcionales.
- `GET /api/reports/export` (admin) → CSV con filtros opcionales.

### Websocket
- `GET /api/ws/notifications?token=<access_token>` (Bearer en query). Eventos enviados: `welcome`, `donation.created`, `event.created`, `echo` (si el cliente envía mensajes).

## Endpoints planificados (no implementados aún)
- Dashboard/reportes avanzados: métricas por rango de fechas y tipo de donación.
- Websocket opcional para notificaciones internas.
# Especificación de API

## Convenciones
- Base path backend: `/api` (servido en `http://localhost:6076`)
- Respuestas en JSON.
- Autenticación (planificada): JWT Bearer (access/refresh).

## Endpoints disponibles (Fase 2 parcial)

### Healthcheck
- `GET /api/health`
- 200 OK
```json
{ "status": "ok" }
```

### Autenticación
- `POST /api/auth/register`
  - body: `{ "email": "<email>", "password": "<str>", "full_name": "<str|null>", "role": "member|admin|public" }`
  - 201 Created → `UserRead`
- `POST /api/auth/login`
  - body: `{ "email": "<email>", "password": "<str>" }`
  - 200 OK → `{ "access_token": "<jwt>", "refresh_token": "<jwt>", "token_type": "bearer" }`
- `POST /api/auth/refresh`
  - body: `{ "refresh_token": "<jwt>" }`
  - 200 OK → tokens nuevos

### Usuarios
- `GET /api/users/me` (Bearer access token) → `UserRead`
- `GET /api/users` (admin) → `[UserRead]`
- `GET /api/users/{user_id}` (admin) → `UserRead`
- `PATCH /api/users/{user_id}` (admin)
  - body opcional: `full_name`, `role` (public|member|admin), `password`, `is_active`
  - 200 OK → `UserRead`
- `DELETE /api/users/{user_id}` (admin) → 204 No Content

### Donaciones
- `GET /api/donations` (admin) → `[DonationRead]`
- `GET /api/donations/me` (Bearer) → `[DonationRead]`
- `POST /api/donations` (Bearer)
  - body: `donor_name`, `donor_document?`, `donation_type (diezmo|ofrenda|misiones|especial)`, `amount`, `payment_method (efectivo|transferencia|tarjeta|otro)`, `note?`, `donation_date`, `event_id?`
  - 201 Created → `DonationRead`

### Documentos
- `POST /api/documents` (Bearer multipart/form-data)
  - fields: `file`, `link_type? (donation|user|event)`, `ref_id?`, `description?`, `is_public?`
  - 201 Created → `DocumentRead`
- `GET /api/documents/{id}` (Bearer si no es público; admin u owner) → archivo
- `GET /api/documents` (admin) → `[DocumentRead]`

### Eventos
- `POST /api/events` (admin) → `EventRead`
- `GET /api/events` → `[EventRead]`

### Reportes
- `GET /api/reports/summary` (admin)
  - 200 OK → `{ "total_donations": int, "total_amount": float, "by_type": { "diezmo": n, ... } }`

## Endpoints planificados (no implementados aún)
- Inscripciones: agregar cancelación/confirmación y listados paginados.
- Dashboard/reportes avanzados: métricas por rango de fechas y tipo de donación.
- Websocket opcional para notificaciones internas.


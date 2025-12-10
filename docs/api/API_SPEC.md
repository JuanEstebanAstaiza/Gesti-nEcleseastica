# Especificación de la API

Base URL: `http://localhost:6076/api`

## Autenticación

La API utiliza JWT (JSON Web Tokens) para autenticación.

### Headers

```http
Authorization: Bearer <access_token>
```

---

## Endpoints

### Health Check

#### `GET /health`

Verifica el estado del servicio.

**Response** `200 OK`
```json
{
  "status": "ok"
}
```

---

### Autenticación (`/auth`)

#### `POST /auth/register`

Registra un nuevo usuario.

**Request Body**
```json
{
  "email": "usuario@ejemplo.com",
  "password": "contraseña123",
  "full_name": "Nombre Completo",
  "role": "member"  // "member" | "admin"
}
```

**Response** `201 Created`
```json
{
  "id": 1,
  "email": "usuario@ejemplo.com",
  "full_name": "Nombre Completo",
  "role": "member",
  "is_active": true
}
```

#### `POST /auth/login`

Inicia sesión y obtiene tokens.

**Request Body**
```json
{
  "email": "usuario@ejemplo.com",
  "password": "contraseña123"
}
```

**Response** `200 OK`
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer"
}
```

#### `POST /auth/refresh`

Renueva el access token usando el refresh token.

**Request Body**
```json
{
  "refresh_token": "eyJhbGciOiJIUzI1NiIs..."
}
```

**Response** `200 OK`
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer"
}
```

---

### Usuarios (`/users`)

#### `GET /users/me`

Obtiene el perfil del usuario autenticado.

**Auth Required**: ✅

**Response** `200 OK`
```json
{
  "id": 1,
  "email": "usuario@ejemplo.com",
  "full_name": "Nombre Completo",
  "role": "member",
  "is_active": true
}
```

#### `GET /users`

Lista todos los usuarios (solo admin).

**Auth Required**: ✅ Admin

**Response** `200 OK`
```json
[
  {
    "id": 1,
    "email": "usuario@ejemplo.com",
    "full_name": "Nombre",
    "role": "member",
    "is_active": true
  }
]
```

#### `GET /users/{user_id}`

Obtiene un usuario por ID (solo admin).

**Auth Required**: ✅ Admin

#### `PATCH /users/{user_id}`

Actualiza un usuario (solo admin).

**Auth Required**: ✅ Admin

**Request Body**
```json
{
  "full_name": "Nuevo Nombre",
  "role": "admin",
  "is_active": false
}
```

#### `DELETE /users/{user_id}`

Elimina un usuario (solo admin).

**Auth Required**: ✅ Admin

**Response** `204 No Content`

---

### Donaciones (`/donations`)

#### `POST /donations`

Crea una nueva donación.

**Auth Required**: ✅

**Request Body**
```json
{
  "donor_name": "Juan Pérez",
  "donor_document": "123456789",
  "donation_type": "diezmo",  // "diezmo" | "ofrenda" | "misiones" | "especial"
  "amount": 100000.00,
  "payment_method": "efectivo",  // "efectivo" | "transferencia" | "tarjeta" | "otro"
  "donation_date": "2024-01-15",
  "note": "Nota opcional",
  "event_id": null
}
```

**Response** `201 Created`
```json
{
  "id": 1,
  "donor_name": "Juan Pérez",
  "donor_document": "123456789",
  "donation_type": "diezmo",
  "amount": 100000.00,
  "payment_method": "efectivo",
  "donation_date": "2024-01-15",
  "note": "Nota opcional",
  "user_id": 1,
  "event_id": null
}
```

#### `GET /donations`

Lista todas las donaciones (solo admin).

**Auth Required**: ✅ Admin

#### `GET /donations/me`

Lista las donaciones del usuario autenticado.

**Auth Required**: ✅

---

### Documentos (`/documents`)

#### `POST /documents`

Sube un documento (multipart/form-data).

**Auth Required**: ✅

**Form Data**
| Campo | Tipo | Requerido | Descripción |
|-------|------|-----------|-------------|
| file | File | ✅ | PDF, PNG, JPG (máx 10MB) |
| link_type | string | ❌ | "donation", "user", "event" |
| ref_id | integer | ❌ | ID de referencia |
| description | string | ❌ | Descripción |
| is_public | boolean | ❌ | Default: false |

**Response** `201 Created`
```json
{
  "id": 1,
  "file_name": "recibo.pdf",
  "mime_type": "application/pdf",
  "size_bytes": 102400,
  "checksum": "abc123...",
  "description": "Recibo de donación",
  "is_public": false,
  "uploaded_at": "2024-01-15T10:30:00Z",
  "donation_id": 1,
  "user_id": 1,
  "event_id": null
}
```

#### `GET /documents/{doc_id}`

Descarga un documento.

**Auth Required**: ✅

**Response**: Archivo binario

#### `GET /documents`

Lista todos los documentos (solo admin).

**Auth Required**: ✅ Admin

---

### Eventos (`/events`)

#### `POST /events`

Crea un nuevo evento (solo admin).

**Auth Required**: ✅ Admin

**Request Body**
```json
{
  "name": "Conferencia de Jóvenes",
  "description": "Evento anual",
  "start_date": "2024-02-01",
  "end_date": "2024-02-03",
  "capacity": 100
}
```

**Response** `201 Created`
```json
{
  "id": 1,
  "name": "Conferencia de Jóvenes",
  "description": "Evento anual",
  "start_date": "2024-02-01",
  "end_date": "2024-02-03",
  "capacity": 100,
  "created_by_id": 1
}
```

#### `GET /events`

Lista todos los eventos (público).

**Auth Required**: ❌

---

### Inscripciones (`/events/{event_id}/registrations`)

#### `POST /events/{event_id}/registrations`

Inscribe a un asistente en un evento (público).

**Auth Required**: ❌

**Request Body**
```json
{
  "attendee_name": "María García",
  "attendee_email": "maria@ejemplo.com",
  "notes": "Notas opcionales"
}
```

**Response** `201 Created`
```json
{
  "id": 1,
  "event_id": 1,
  "attendee_name": "María García",
  "attendee_email": "maria@ejemplo.com",
  "notes": "Notas opcionales",
  "is_cancelled": false,
  "registered_at": "2024-01-15T10:30:00Z"
}
```

**Errores**:
- `404`: Evento no existe
- `400`: Email ya registrado en el evento
- `400`: Evento lleno (capacidad alcanzada)

#### `GET /events/{event_id}/registrations`

Lista inscripciones de un evento (solo admin).

**Auth Required**: ✅ Admin

**Query Params**:
- `limit`: int (default 50, max 200)
- `offset`: int (default 0)

#### `DELETE /events/{event_id}/registrations/{registration_id}`

Cancela una inscripción (solo admin).

**Auth Required**: ✅ Admin

**Response** `204 No Content`

---

### Reportes (`/reports`)

#### `GET /reports/summary`

Resumen de donaciones con filtros (solo admin).

**Auth Required**: ✅ Admin

**Query Params**:
- `start_date`: date (YYYY-MM-DD)
- `end_date`: date (YYYY-MM-DD)
- `donation_type`: string

**Response** `200 OK`
```json
{
  "total_donations": 150,
  "total_amount": 15000000.00,
  "by_type": {
    "diezmo": 80,
    "ofrenda": 50,
    "misiones": 15,
    "especial": 5
  },
  "filters": {
    "start_date": "2024-01-01",
    "end_date": "2024-01-31",
    "donation_type": null
  }
}
```

#### `GET /reports/dashboard`

Datos para dashboard con métricas por mes y tipo (solo admin).

**Auth Required**: ✅ Admin

**Response** `200 OK`
```json
{
  "by_month": {
    "2024-01": { "count": 50, "amount": 5000000.00 },
    "2024-02": { "count": 45, "amount": 4500000.00 }
  },
  "by_type": {
    "diezmo": { "count": 80, "amount": 8000000.00 },
    "ofrenda": { "count": 50, "amount": 3000000.00 }
  }
}
```

#### `GET /reports/export`

Exporta donaciones a CSV (solo admin).

**Auth Required**: ✅ Admin

**Query Params**: Mismos que `/reports/summary`

**Response**: `text/csv`
```csv
id,donor_name,donation_type,amount,payment_method,donation_date
1,Juan Pérez,diezmo,100000,efectivo,2024-01-15
```

---

### WebSocket (`/ws`)

#### `WS /ws/notifications`

Canal de notificaciones en tiempo real.

**Query Params**:
- `token`: JWT access token

**Mensajes recibidos**:
```json
{
  "type": "donation.created",
  "donation_id": 1,
  "amount": 100000.00,
  "donation_type": "diezmo"
}
```

```json
{
  "type": "event.created",
  "event_id": 1,
  "name": "Conferencia",
  "capacity": 100
}
```

---

## Códigos de Error

| Código | Descripción |
|--------|-------------|
| 400 | Bad Request - Datos inválidos |
| 401 | Unauthorized - Token inválido o expirado |
| 403 | Forbidden - Sin permisos suficientes |
| 404 | Not Found - Recurso no encontrado |
| 409 | Conflict - Recurso ya existe (ej: email duplicado) |
| 422 | Unprocessable Entity - Error de validación |
| 500 | Internal Server Error |

## Documentación Interactiva

- Swagger UI: http://localhost:6076/docs
- ReDoc: http://localhost:6076/redoc

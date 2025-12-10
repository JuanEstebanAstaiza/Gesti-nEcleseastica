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
  "role": "member"
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

---

### Usuarios (`/users`)

#### `GET /users/me`

Obtiene el perfil del usuario autenticado.

**Auth Required**: ✅

#### `GET /users`

Lista todos los usuarios (solo admin).

**Auth Required**: ✅ Admin

#### `GET /users/{user_id}`

Obtiene un usuario por ID (solo admin).

#### `PATCH /users/{user_id}`

Actualiza un usuario (solo admin).

#### `DELETE /users/{user_id}`

Elimina un usuario (solo admin).

---

## 💰 Donaciones (`/donations`)

### Crear Donación (Formato Actualizado)

#### `POST /donations`

Crea una nueva donación con montos separados por tipo.

**Auth Required**: ✅

**Request Body**
```json
{
  "donor_name": "Juan Pérez",
  "donor_document": "123456789",
  "donor_address": "Calle 123 #45-67",
  "donor_phone": "3001234567",
  "donor_email": "juan@email.com",
  "amount_tithe": 100000.00,
  "amount_offering": 50000.00,
  "amount_missions": 20000.00,
  "amount_special": 0,
  "cash_amount": 170000.00,
  "transfer_amount": 0,
  "payment_reference": null,
  "donation_date": "2024-11-15",
  "envelope_number": "001",
  "note": "Nota opcional",
  "is_anonymous": false,
  "event_id": null
}
```

**Response** `201 Created`
```json
{
  "id": 1,
  "donor_name": "Juan Pérez",
  "donor_document": "123456789",
  "amount_tithe": 100000.00,
  "amount_offering": 50000.00,
  "amount_missions": 20000.00,
  "amount_special": 0,
  "amount_total": 170000.00,
  "is_cash": true,
  "is_transfer": false,
  "donation_date": "2024-11-15",
  "week_number": 46,
  "receipt_number": "2024-001",
  "created_at": "2024-11-15T10:30:00Z"
}
```

#### `GET /donations`

Lista todas las donaciones (solo admin).

**Auth Required**: ✅ Admin

#### `GET /donations/me`

Lista las donaciones del usuario autenticado.

**Auth Required**: ✅

---

## 📊 Reportes de Donaciones (`/reports/donations`)

### Reporte Mensual

#### `GET /reports/donations/monthly`

Obtiene el reporte mensual en formato JSON.

**Auth Required**: ✅ Admin

**Query Params**:
- `month`: int (1-12) **Requerido**
- `year`: int **Requerido**

**Response** `200 OK`
```json
{
  "church_name": "Iglesia Comunidad Cristiana de Fe",
  "month": 11,
  "year": 2024,
  "period_label": "NOVIEMBRE 2024",
  "donations": [
    {
      "fecha": "01/11/2024",
      "nombre": "Carmen Elisa Rocha",
      "efectivo": 60000.00,
      "transferencia": 0,
      "documento": "123456789",
      "diezmo": 60000.00,
      "ofrenda": 0,
      "misiones": 0,
      "total": 60000.00
    },
    {
      "fecha": "01/11/2024",
      "nombre": "OSI",
      "efectivo": 0,
      "transferencia": 35000.00,
      "documento": "",
      "diezmo": 35000.00,
      "ofrenda": 0,
      "misiones": 0,
      "total": 35000.00
    }
  ],
  "summary": {
    "total_efectivo": 930000.00,
    "total_transferencia": 1471000.00,
    "total_diezmo": 800000.00,
    "total_ofrenda": 1421000.00,
    "total_misiones": 50000.00,
    "gran_total": 2401000.00,
    "cantidad_donaciones": 25
  }
}
```

#### `GET /reports/donations/monthly/csv`

Exporta el reporte mensual en formato CSV para Excel.

**Auth Required**: ✅ Admin

**Query Params**: Mismo que `/monthly`

**Response**: `text/csv`
```csv
NOVIEMBRE,NOMBRE,EFECTIVO,TRANSFERENCIA,DOCUMENTO,DIEZMO,OFRENDA,MISIONES,TOTAL
01/11/2024,Carmen Elisa Rocha,$60,000.00,,,,$60,000.00,,$60,000.00
01/11/2024,OSI,,$35,000.00,,$35,000.00,,,$35,000.00
...
TOTAL,,$930,000.00,,$1,421,000.00,$50,000.00,$2,401,000.00
```

### Reporte Semanal para Contadora

#### `GET /reports/donations/weekly/{week_number}`

Obtiene el reporte semanal para contadora.

**Auth Required**: ✅ Admin

**Query Params**:
- `year`: int **Requerido**

**Response** `200 OK`
```json
{
  "church_name": "Iglesia Comunidad Cristiana de Fe",
  "logo_url": null,
  "fecha": "15/11/2024",
  "semana": 46,
  "numero_sobres": 25,
  "diezmos_efectivo": 500000.00,
  "diezmos_transferencia": 300000.00,
  "diezmos_total": 800000.00,
  "ofrendas_efectivo": 200000.00,
  "ofrendas_transferencia": 100000.00,
  "ofrendas_total": 300000.00,
  "misiones_efectivo": 50000.00,
  "misiones_transferencia": 0,
  "misiones_total": 50000.00,
  "total_efectivo": 750000.00,
  "total_transferencia": 400000.00,
  "valor_total": 1150000.00,
  "diezmo_de_diezmos": 80000.00,
  "testigo_1": null,
  "testigo_2": null
}
```

#### `GET /reports/donations/weekly/{week_number}/csv`

Exporta el reporte semanal en CSV.

#### `POST /reports/donations/weekly/close`

Cierra el resumen semanal (no se pueden modificar donaciones después).

**Auth Required**: ✅ Admin

**Request Body**
```json
{
  "summary_date": "2024-11-15",
  "week_number": 46,
  "year": 2024,
  "witness_1_name": "María García",
  "witness_1_document": "987654321",
  "witness_2_name": "Pedro López",
  "witness_2_document": "456789123",
  "notes": "Semana sin novedades"
}
```

---

## 💸 Gastos (`/expenses`)

### Categorías

#### `GET /expenses/categories`

Lista todas las categorías de gastos.

**Auth Required**: ✅

**Query Params**:
- `include_inactive`: boolean (default false)

**Response** `200 OK`
```json
[
  {
    "id": 1,
    "name": "Servicios Públicos",
    "description": "Agua, luz, gas, internet",
    "color": "#3b82f6",
    "icon": "ri-lightbulb-line",
    "monthly_budget": 500000.00,
    "is_active": true,
    "sort_order": 1
  }
]
```

#### `POST /expenses/categories`

Crea una categoría de gasto.

**Auth Required**: ✅ Admin

**Request Body**
```json
{
  "name": "Nueva Categoría",
  "description": "Descripción",
  "color": "#8b5cf6",
  "icon": "ri-folder-line",
  "monthly_budget": 200000.00
}
```

#### `PATCH /expenses/categories/{category_id}`

Actualiza una categoría.

#### `DELETE /expenses/categories/{category_id}`

Desactiva una categoría (soft delete).

### Subcategorías

#### `GET /expenses/categories/{category_id}/subcategories`

Lista subcategorías de una categoría.

#### `POST /expenses/subcategories`

Crea una subcategoría.

### Etiquetas

#### `GET /expenses/tags`

Lista todas las etiquetas.

**Response** `200 OK`
```json
[
  {"id": 1, "name": "Urgente", "color": "#ef4444"},
  {"id": 2, "name": "Recurrente", "color": "#8b5cf6"},
  {"id": 3, "name": "Deducible", "color": "#22c55e"}
]
```

#### `POST /expenses/tags`

Crea una etiqueta.

#### `DELETE /expenses/tags/{tag_id}`

Elimina una etiqueta.

### Gastos

#### `GET /expenses`

Lista gastos con filtros.

**Auth Required**: ✅

**Query Params**:
- `category_id`: int
- `status`: string (`pending`, `approved`, `paid`, `cancelled`)
- `start_date`: date
- `end_date`: date
- `limit`: int (default 50, max 200)
- `offset`: int

**Response** `200 OK`
```json
[
  {
    "id": 1,
    "category_id": 1,
    "subcategory_id": 2,
    "description": "Pago de energía mes de noviembre",
    "amount": 150000.00,
    "expense_date": "2024-11-10",
    "vendor_name": "EPM",
    "vendor_document": "890904996",
    "payment_method": "transferencia",
    "payment_reference": "TRF-123456",
    "invoice_number": "FAC-001234",
    "status": "paid",
    "is_recurring": true,
    "recurrence_period": "monthly",
    "tags": [1, 2],
    "notes": null,
    "created_at": "2024-11-10T09:00:00Z",
    "category": {
      "id": 1,
      "name": "Servicios Públicos",
      "color": "#3b82f6"
    }
  }
]
```

#### `POST /expenses`

Crea un nuevo gasto.

**Auth Required**: ✅ Admin

**Request Body**
```json
{
  "category_id": 1,
  "subcategory_id": 2,
  "description": "Pago de energía mes de noviembre",
  "amount": 150000.00,
  "expense_date": "2024-11-10",
  "vendor_name": "EPM",
  "vendor_document": "890904996",
  "vendor_phone": "6044444444",
  "payment_method": "transferencia",
  "payment_reference": "TRF-123456",
  "bank_account": "Cuenta corriente 123456",
  "invoice_number": "FAC-001234",
  "is_recurring": true,
  "recurrence_period": "monthly",
  "tags": [1, 2],
  "notes": "Pago mensual"
}
```

#### `GET /expenses/{expense_id}`

Obtiene un gasto por ID.

#### `PATCH /expenses/{expense_id}`

Actualiza un gasto (no permitido si está pagado).

#### `POST /expenses/{expense_id}/approve`

Aprueba un gasto pendiente.

**Auth Required**: ✅ Admin

#### `POST /expenses/{expense_id}/pay`

Marca un gasto como pagado.

**Auth Required**: ✅ Admin

**Query Params**:
- `payment_reference`: string (opcional)

#### `DELETE /expenses/{expense_id}`

Cancela un gasto (no lo elimina).

### Documentos de Gastos

#### `GET /expenses/{expense_id}/documents`

Lista documentos de un gasto.

#### `POST /expenses/{expense_id}/documents`

Sube un documento de soporte.

**Auth Required**: ✅ Admin

**Form Data**:
- `file`: File (PDF, JPG, PNG)
- `document_type`: string (`invoice`, `receipt`, `quote`, `contract`, `other`)
- `description`: string

#### `GET /expenses/{expense_id}/documents/{doc_id}/download`

Descarga un documento.

### Carpetas

#### `GET /expenses/folders`

Lista carpetas de gastos.

**Query Params**:
- `parent_id`: int (null para raíz)

#### `POST /expenses/folders`

Crea una carpeta.

### Reportes de Gastos

#### `GET /expenses/reports/monthly`

Reporte mensual de gastos.

**Auth Required**: ✅ Admin

**Query Params**:
- `month`: int **Requerido**
- `year`: int **Requerido**

**Response** `200 OK`
```json
{
  "church_name": "Iglesia Comunidad Cristiana de Fe",
  "month": 11,
  "year": 2024,
  "period_label": "NOVIEMBRE 2024",
  "expenses": [...],
  "summary": {
    "total_gastos": 2500000.00,
    "por_categoria": {
      "Servicios Públicos": 500000.00,
      "Arriendo": 1500000.00,
      "Mantenimiento": 500000.00
    },
    "por_metodo_pago": {
      "efectivo": 800000.00,
      "transferencia": 1700000.00
    },
    "cantidad_gastos": 15,
    "presupuesto_usado": {
      "Servicios Públicos": {
        "presupuesto": 600000,
        "gastado": 500000,
        "porcentaje": 83.33
      }
    }
  }
}
```

#### `GET /expenses/reports/monthly/csv`

Exporta reporte de gastos en CSV.

#### `GET /expenses/reports/summary`

Resumen de gastos para dashboard.

**Query Params**:
- `start_date`: date
- `end_date`: date

**Response** `200 OK`
```json
{
  "total": 2500000.00,
  "pending": 300000.00,
  "approved": 500000.00,
  "paid": 1700000.00,
  "count": 15
}
```

---

### Documentos (`/documents`)

#### `POST /documents`

Sube un documento.

#### `GET /documents/{doc_id}`

Descarga un documento.

#### `GET /documents`

Lista todos los documentos (solo admin).

---

### Eventos (`/events`)

#### `POST /events`

Crea un nuevo evento (solo admin).

#### `GET /events`

Lista todos los eventos (público).

---

### Inscripciones (`/events/{event_id}/registrations`)

#### `POST /events/{event_id}/registrations`

Inscribe a un asistente (público).

#### `GET /events/{event_id}/registrations`

Lista inscripciones (solo admin).

#### `DELETE /events/{event_id}/registrations/{registration_id}`

Cancela una inscripción (solo admin).

---

### WebSocket (`/ws`)

#### `WS /ws/notifications`

Canal de notificaciones en tiempo real.

**Query Params**:
- `token`: JWT access token

**Mensajes recibidos**:
```json
{"type": "donation.created", "donation_id": 1, "amount": 100000.00}
{"type": "expense.created", "expense_id": 1, "amount": 150000.00}
{"type": "event.created", "event_id": 1, "name": "Conferencia"}
```

---

## Códigos de Error

| Código | Descripción |
|--------|-------------|
| 400 | Bad Request - Datos inválidos |
| 401 | Unauthorized - Token inválido o expirado |
| 403 | Forbidden - Sin permisos suficientes |
| 404 | Not Found - Recurso no encontrado |
| 409 | Conflict - Recurso ya existe |
| 422 | Unprocessable Entity - Error de validación |
| 500 | Internal Server Error |

## Documentación Interactiva

- Swagger UI: http://localhost:6076/docs
- ReDoc: http://localhost:6076/redoc

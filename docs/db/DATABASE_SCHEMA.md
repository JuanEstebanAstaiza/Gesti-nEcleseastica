# Esquema de Base de Datos

## Arquitectura Multi-Tenant

El sistema utiliza una arquitectura multi-tenant con bases de datos separadas:

```
┌─────────────────────────────────────────────────────────────────────────┐
│                           MASTER DATABASE                                │
│  ┌───────────────┐  ┌───────────────┐  ┌───────────────┐               │
│  │    tenants    │  │ super_admins  │  │  tenant_admins│               │
│  └───────────────┘  └───────────────┘  └───────────────┘               │
└─────────────────────────────────────────────────────────────────────────┘
                              │
         ┌────────────────────┼────────────────────┐
         ▼                    ▼                    ▼
┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐
│  TENANT DB 1    │  │  TENANT DB 2    │  │  TENANT DB N    │
│  (Iglesia A)    │  │  (Iglesia B)    │  │  (Iglesia N)    │
└─────────────────┘  └─────────────────┘  └─────────────────┘
```

---

## Diagrama de Entidades (Tenant DB)

```
┌──────────────────┐       ┌────────────────────────┐       ┌──────────────────┐
│      users       │       │       donations        │       │    documents     │
├──────────────────┤       ├────────────────────────┤       ├──────────────────┤
│ id (PK)          │───┐   │ id (PK)                │   ┌───│ id (PK)          │
│ email (UNIQUE)   │   │   │ donor_name             │   │   │ file_name        │
│ hashed_password  │   │   │ donor_document         │   │   │ stored_path      │
│ full_name        │   │   │ donor_address          │   │   │ mime_type        │
│ role             │   └──▶│ user_id (FK)           │   │   │ size_bytes       │
│ is_active        │       │ amount_tithe           │◀──┼───│ donation_id (FK) │
│ created_at       │       │ amount_offering        │   │   │ user_id (FK)     │
└──────────────────┘       │ amount_missions        │   │   │ checksum         │
        │                  │ amount_special         │   │   │ uploaded_at      │
        │                  │ amount_total           │   │   └──────────────────┘
        │                  │ is_cash / is_transfer  │   │
        │                  │ donation_date          │   │
        │                  │ week_number            │   │
        │                  │ receipt_number         │   │
        │                  └────────────────────────┘   │
        │                           │                   │
        │                           ▼                   │
        │                  ┌────────────────────────┐   │
        │                  │  donation_summaries    │   │
        │                  ├────────────────────────┤   │
        │                  │ id (PK)                │   │
        │                  │ summary_date           │   │
        │                  │ week_number            │   │
        │                  │ year                   │   │
        │                  │ tithe_cash/transfer    │   │
        │                  │ offering_cash/transfer │   │
        │                  │ missions_cash/transfer │   │
        │                  │ grand_total            │   │
        │                  │ tithe_of_tithes        │   │
        │                  │ witness_1/2_name       │   │
        │                  └────────────────────────┘   │
        │                                               │
        │                  ┌──────────────────┐         │
        │                  │      events      │         │
        │                  ├──────────────────┤         │
        │                  │ id (PK)          │◀────────┘
        └─────────────────▶│ created_by_id(FK)│
                           │ name             │
                           │ capacity         │
                           │ start_date       │
                           └──────────────────┘
                                    │
                                    ▼
                           ┌──────────────────┐
                           │  registrations   │
                           ├──────────────────┤
                           │ id (PK)          │
                           │ event_id (FK)    │
                           │ attendee_name    │
                           │ attendee_email   │
                           │ is_cancelled     │
                           └──────────────────┘

═══════════════════════════════════════════════════════════════════════════

                         MÓDULO DE GASTOS

┌────────────────────┐     ┌────────────────────┐     ┌────────────────────┐
│ expense_categories │     │      expenses      │     │ expense_documents  │
├────────────────────┤     ├────────────────────┤     ├────────────────────┤
│ id (PK)            │◀────│ category_id (FK)   │     │ id (PK)            │
│ name               │     │ subcategory_id(FK) │────▶│ expense_id (FK)    │
│ description        │     │ description        │     │ file_name          │
│ color              │     │ amount             │     │ stored_path        │
│ icon               │     │ expense_date       │     │ mime_type          │
│ monthly_budget     │     │ vendor_name        │     │ document_type      │
│ is_active          │     │ payment_method     │     │ uploaded_at        │
└────────────────────┘     │ status             │     └────────────────────┘
         │                 │ created_by_id (FK) │
         ▼                 │ approved_by_id(FK) │
┌────────────────────┐     │ tags (JSONB)       │
│expense_subcategories│     └────────────────────┘
├────────────────────┤
│ id (PK)            │     ┌────────────────────┐
│ category_id (FK)   │     │   expense_tags     │
│ name               │     ├────────────────────┤
│ is_active          │     │ id (PK)            │
└────────────────────┘     │ name (UNIQUE)      │
                           │ color              │
┌────────────────────┐     └────────────────────┘
│  expense_folders   │
├────────────────────┤
│ id (PK)            │
│ name               │
│ parent_id (FK)     │
│ folder_type        │
│ year / month       │
└────────────────────┘
```

---

## Tablas de Donaciones (Formato Actualizado)

### donations

| Columna | Tipo | Constraints | Descripción |
|---------|------|-------------|-------------|
| id | SERIAL | PRIMARY KEY | ID único |
| user_id | INTEGER | REFERENCES users(id) | Usuario donante (opcional) |
| event_id | INTEGER | REFERENCES events(id) | Evento relacionado |
| donor_name | VARCHAR(255) | NOT NULL | Nombre del donante |
| donor_document | VARCHAR(50) | | Cédula/NIT |
| donor_address | VARCHAR(500) | | Dirección |
| donor_phone | VARCHAR(50) | | Teléfono |
| donor_email | VARCHAR(255) | | Email |
| **amount_tithe** | NUMERIC(12,2) | DEFAULT 0 | **Monto de Diezmo** |
| **amount_offering** | NUMERIC(12,2) | DEFAULT 0 | **Monto de Ofrenda** |
| **amount_missions** | NUMERIC(12,2) | DEFAULT 0 | **Monto de Misiones** |
| **amount_special** | NUMERIC(12,2) | DEFAULT 0 | **Monto Especial** |
| **amount_total** | NUMERIC(12,2) | NOT NULL | **Total de la donación** |
| is_cash | BOOLEAN | DEFAULT TRUE | ¿Es efectivo? |
| is_transfer | BOOLEAN | DEFAULT FALSE | ¿Es transferencia? |
| payment_reference | VARCHAR(100) | | Referencia de pago |
| donation_date | DATE | NOT NULL | Fecha de la donación |
| week_number | INTEGER | | Número de semana |
| envelope_number | VARCHAR(50) | | Número de sobre |
| receipt_number | VARCHAR(50) | UNIQUE | Número de recibo |
| is_anonymous | BOOLEAN | DEFAULT FALSE | Donación anónima (OSI) |
| created_by_id | INTEGER | REFERENCES users(id) | Quien registró |
| created_at | TIMESTAMPTZ | DEFAULT NOW() | Fecha de registro |

**Índices**:
- `idx_donations_user` en `user_id`
- `idx_donations_date` en `donation_date`
- `idx_donations_week` en `week_number`

### donation_summaries

Resumen semanal para reportes a contaduría.

| Columna | Tipo | Constraints | Descripción |
|---------|------|-------------|-------------|
| id | SERIAL | PRIMARY KEY | ID único |
| summary_date | DATE | NOT NULL | Fecha del resumen |
| week_number | INTEGER | NOT NULL | Semana del año |
| year | INTEGER | NOT NULL | Año |
| envelope_count | INTEGER | DEFAULT 0 | Cantidad de sobres |
| tithe_cash | NUMERIC(12,2) | DEFAULT 0 | Diezmos en efectivo |
| tithe_transfer | NUMERIC(12,2) | DEFAULT 0 | Diezmos por transferencia |
| offering_cash | NUMERIC(12,2) | DEFAULT 0 | Ofrendas en efectivo |
| offering_transfer | NUMERIC(12,2) | DEFAULT 0 | Ofrendas por transferencia |
| missions_cash | NUMERIC(12,2) | DEFAULT 0 | Misiones en efectivo |
| missions_transfer | NUMERIC(12,2) | DEFAULT 0 | Misiones por transferencia |
| total_cash | NUMERIC(12,2) | DEFAULT 0 | Total efectivo |
| total_transfer | NUMERIC(12,2) | DEFAULT 0 | Total transferencias |
| grand_total | NUMERIC(12,2) | DEFAULT 0 | Gran total |
| **tithe_of_tithes** | NUMERIC(12,2) | DEFAULT 0 | **Diezmo de diezmos (10%)** |
| witness_1_name | VARCHAR(255) | | Nombre testigo 1 |
| witness_1_document | VARCHAR(50) | | Documento testigo 1 |
| witness_2_name | VARCHAR(255) | | Nombre testigo 2 |
| witness_2_document | VARCHAR(50) | | Documento testigo 2 |
| is_closed | BOOLEAN | DEFAULT FALSE | ¿Semana cerrada? |
| closed_at | TIMESTAMPTZ | | Fecha de cierre |

**Constraint único**: `(year, week_number)`

---

## Tablas de Gastos

### expense_categories

| Columna | Tipo | Constraints | Descripción |
|---------|------|-------------|-------------|
| id | SERIAL | PRIMARY KEY | ID único |
| name | VARCHAR(100) | NOT NULL | Nombre de categoría |
| description | TEXT | | Descripción |
| color | VARCHAR(7) | DEFAULT '#6b7280' | Color hex para UI |
| icon | VARCHAR(50) | | Icono (Remix Icons) |
| monthly_budget | NUMERIC(12,2) | | Presupuesto mensual |
| is_active | BOOLEAN | DEFAULT TRUE | Estado activo |
| sort_order | INTEGER | DEFAULT 0 | Orden de display |

**Categorías predeterminadas**:
- Servicios Públicos
- Arriendo
- Salarios
- Mantenimiento
- Suministros
- Eventos
- Transporte
- Misiones
- Otros

### expense_subcategories

| Columna | Tipo | Constraints | Descripción |
|---------|------|-------------|-------------|
| id | SERIAL | PRIMARY KEY | ID único |
| category_id | INTEGER | FK expense_categories | Categoría padre |
| name | VARCHAR(100) | NOT NULL | Nombre |
| description | TEXT | | Descripción |
| is_active | BOOLEAN | DEFAULT TRUE | Estado activo |

### expense_tags

| Columna | Tipo | Constraints | Descripción |
|---------|------|-------------|-------------|
| id | SERIAL | PRIMARY KEY | ID único |
| name | VARCHAR(50) | UNIQUE NOT NULL | Nombre de etiqueta |
| color | VARCHAR(7) | DEFAULT '#3b82f6' | Color hex |

**Etiquetas predeterminadas**:
- Urgente (rojo)
- Recurrente (violeta)
- Deducible (verde)
- Pendiente aprobación (amarillo)

### expenses

| Columna | Tipo | Constraints | Descripción |
|---------|------|-------------|-------------|
| id | SERIAL | PRIMARY KEY | ID único |
| category_id | INTEGER | FK NOT NULL | Categoría |
| subcategory_id | INTEGER | FK | Subcategoría |
| description | VARCHAR(500) | NOT NULL | Descripción del gasto |
| amount | NUMERIC(12,2) | NOT NULL | Monto |
| expense_date | DATE | NOT NULL | Fecha del gasto |
| vendor_name | VARCHAR(255) | | Proveedor |
| vendor_document | VARCHAR(50) | | NIT/Cédula proveedor |
| vendor_phone | VARCHAR(50) | | Teléfono proveedor |
| payment_method | VARCHAR(50) | DEFAULT 'efectivo' | Método de pago |
| payment_reference | VARCHAR(100) | | Referencia de pago |
| bank_account | VARCHAR(100) | | Cuenta bancaria |
| invoice_number | VARCHAR(50) | | Número de factura |
| receipt_number | VARCHAR(50) | | Número de recibo |
| status | VARCHAR(20) | DEFAULT 'pending' | Estado |
| is_recurring | BOOLEAN | DEFAULT FALSE | ¿Es recurrente? |
| recurrence_period | VARCHAR(20) | | Período (monthly, weekly) |
| tags | JSONB | | IDs de etiquetas |
| notes | TEXT | | Notas |
| created_by_id | INTEGER | FK NOT NULL | Creado por |
| approved_by_id | INTEGER | FK | Aprobado por |
| created_at | TIMESTAMPTZ | DEFAULT NOW() | Fecha creación |
| approved_at | TIMESTAMPTZ | | Fecha aprobación |

**Estados posibles**: `pending`, `approved`, `paid`, `cancelled`

### expense_documents

| Columna | Tipo | Constraints | Descripción |
|---------|------|-------------|-------------|
| id | SERIAL | PRIMARY KEY | ID único |
| expense_id | INTEGER | FK ON DELETE CASCADE | Gasto |
| file_name | VARCHAR(255) | NOT NULL | Nombre archivo |
| stored_path | VARCHAR(500) | NOT NULL | Ruta almacenamiento |
| mime_type | VARCHAR(100) | NOT NULL | Tipo MIME |
| size_bytes | INTEGER | NOT NULL | Tamaño |
| checksum | VARCHAR(64) | | SHA-256 |
| document_type | VARCHAR(50) | DEFAULT 'invoice' | Tipo documento |
| description | TEXT | | Descripción |
| uploaded_by_id | INTEGER | FK | Subido por |
| uploaded_at | TIMESTAMPTZ | DEFAULT NOW() | Fecha subida |

**Tipos de documento**: `invoice`, `receipt`, `quote`, `contract`, `other`

### expense_folders

| Columna | Tipo | Constraints | Descripción |
|---------|------|-------------|-------------|
| id | SERIAL | PRIMARY KEY | ID único |
| name | VARCHAR(100) | NOT NULL | Nombre carpeta |
| description | TEXT | | Descripción |
| parent_id | INTEGER | FK self | Carpeta padre |
| folder_type | VARCHAR(50) | DEFAULT 'general' | Tipo |
| year | INTEGER | | Año (para carpetas período) |
| month | INTEGER | | Mes (para carpetas período) |
| is_active | BOOLEAN | DEFAULT TRUE | Estado activo |

---

## Formato de Reportes

### Reporte Mensual de Donaciones (CSV)

```csv
NOVIEMBRE,NOMBRE,EFECTIVO,TRANSFERENCIA,DOCUMENTO,DIEZMO,OFRENDA,MISIONES,TOTAL
01/11/2025,Carmen Elisa Rocha,,,$60,000.00,,,$60,000.00
01/11/2025,OSI,,$35,000.00,,$35,000.00,,,$35,000.00
...
TOTAL,,$930,000.00,,$1,421,000.00,$50,000.00,$2,401,000.00
```

### Reporte Semanal para Contadora

```
RELACIÓN DE DIEZMOS Y OFRENDAS

FECHA: 15/11/2025    SEMANA: 46
NÚMERO DE SOBRES: 25

CONCEPTO      | EFECTIVO    | TRANSFERENCIA | TOTAL
DIEZMOS       | $500,000    | $300,000      | $800,000
OFRENDAS      | $200,000    | $100,000      | $300,000
MISIONES      | $50,000     | $0            | $50,000
VALOR TOTAL   | $750,000    | $400,000      | $1,150,000

DIEZMOS DE DIEZMOS: $80,000

TESTIGO 1: ________________
TESTIGO 2: ________________
```

---

## Migraciones

Los cambios al esquema se realizan mediante scripts SQL en `app/db/sql/`:

```bash
# Aplicar schema de tenant
docker exec ekklesia_db psql -U ekklesia -d ekklesia -f /code/app/db/sql/tenant_schema.sql

# Aplicar schema master
docker exec ekklesia_master_db psql -U ekklesia -d ekklesia_master -f /code/app/db/sql/master_schema.sql
```

## Backup y Restauración

```bash
# Backup
docker exec ekklesia_db pg_dump -U ekklesia ekklesia > backup_tenant.sql

# Restauración
cat backup_tenant.sql | docker exec -i ekklesia_db psql -U ekklesia -d ekklesia
```

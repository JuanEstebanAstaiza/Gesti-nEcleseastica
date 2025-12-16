# Esquema de Base de Datos

## Diagrama de Entidades

```
┌──────────────────┐       ┌──────────────────┐       ┌──────────────────┐
│      users       │       │    donations     │       │    documents     │
├──────────────────┤       ├──────────────────┤       ├──────────────────┤
│ id (PK)          │───┐   │ id (PK)          │   ┌───│ id (PK)          │
│ email (UNIQUE)   │   │   │ donor_name       │   │   │ file_name        │
│ hashed_password  │   │   │ donor_document   │   │   │ stored_path      │
│ full_name        │   │   │ donation_type    │   │   │ mime_type        │
│ role             │   └──▶│ user_id (FK)     │   │   │ size_bytes       │
│ is_active        │       │ amount           │◀──┼───│ donation_id (FK) │
│ created_at       │       │ payment_method   │   │   │ user_id (FK)     │
└──────────────────┘       │ donation_date    │   │   │ event_id (FK)    │
        │                  │ note             │   │   │ checksum         │
        │                  │ event_id (FK)    │───┼──▶│ description      │
        │                  │ created_at       │   │   │ is_public        │
        │                  └──────────────────┘   │   │ uploaded_at      │
        │                                         │   └──────────────────┘
        │                  ┌──────────────────┐   │
        │                  │      events      │   │
        │                  ├──────────────────┤   │
        │                  │ id (PK)          │◀──┘
        └─────────────────▶│ created_by_id(FK)│
                           │ name             │
                           │ description      │
                           │ start_date       │
                           │ end_date         │
                           │ capacity         │
                           │ created_at       │
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
                           │ notes            │
                           │ is_cancelled     │
                           │ registered_at    │
                           └──────────────────┘
```

## Tipos ENUM

### user_role

```sql
CREATE TYPE user_role AS ENUM ('public', 'member', 'admin');
```

### donation_type

```sql
CREATE TYPE donation_type AS ENUM ('diezmo', 'ofrenda', 'misiones', 'especial');
```

### payment_method

```sql
CREATE TYPE payment_method AS ENUM ('efectivo', 'transferencia', 'tarjeta', 'otro');
```

## Tablas

### users

| Columna | Tipo | Constraints | Descripción |
|---------|------|-------------|-------------|
| id | SERIAL | PRIMARY KEY | ID único |
| email | VARCHAR(255) | NOT NULL, UNIQUE | Correo electrónico |
| hashed_password | VARCHAR(255) | NOT NULL | Contraseña hasheada (bcrypt) |
| full_name | VARCHAR(255) | | Nombre completo |
| role | user_role | DEFAULT 'member' | Rol del usuario |
| is_active | BOOLEAN | DEFAULT TRUE | Estado activo |
| created_at | TIMESTAMPTZ | DEFAULT NOW() | Fecha de creación |

**Índices**:
- `users_email_key` (UNIQUE) en `email`

### donations

| Columna | Tipo | Constraints | Descripción |
|---------|------|-------------|-------------|
| id | SERIAL | PRIMARY KEY | ID único |
| donor_name | VARCHAR(255) | NOT NULL | Nombre del donante |
| donor_document | VARCHAR(50) | | Documento de identidad |
| donation_type | donation_type | NOT NULL | Tipo de donación |
| user_id | INTEGER | REFERENCES users(id) | Usuario que registró |
| amount | NUMERIC(12,2) | NOT NULL | Monto de la donación |
| payment_method | payment_method | NOT NULL | Método de pago |
| donation_date | DATE | NOT NULL | Fecha de la donación |
| note | TEXT | | Nota adicional |
| event_id | INTEGER | REFERENCES events(id) | Evento relacionado |
| created_at | TIMESTAMPTZ | DEFAULT NOW() | Fecha de registro |

**Índices**:
- `idx_donations_user_id` en `user_id`
- `idx_donations_donation_date` en `donation_date`
- `idx_donations_type` en `donation_type`

### documents

| Columna | Tipo | Constraints | Descripción |
|---------|------|-------------|-------------|
| id | SERIAL | PRIMARY KEY | ID único |
| file_name | VARCHAR(255) | NOT NULL | Nombre original del archivo |
| stored_path | VARCHAR(500) | NOT NULL | Ruta de almacenamiento |
| mime_type | VARCHAR(100) | NOT NULL | Tipo MIME |
| size_bytes | INTEGER | NOT NULL | Tamaño en bytes |
| checksum | VARCHAR(64) | | SHA-256 del archivo |
| description | TEXT | | Descripción |
| is_public | BOOLEAN | DEFAULT FALSE | Visibilidad pública |
| donation_id | INTEGER | REFERENCES donations(id) | Donación relacionada |
| user_id | INTEGER | REFERENCES users(id) | Usuario que subió |
| event_id | INTEGER | REFERENCES events(id) | Evento relacionado |
| uploaded_at | TIMESTAMPTZ | DEFAULT NOW() | Fecha de subida |

**Índices**:
- `idx_documents_donation_id` en `donation_id`
- `idx_documents_user_id` en `user_id`

### events

| Columna | Tipo | Constraints | Descripción |
|---------|------|-------------|-------------|
| id | SERIAL | PRIMARY KEY | ID único |
| name | VARCHAR(255) | NOT NULL | Nombre del evento |
| description | TEXT | | Descripción |
| start_date | DATE | | Fecha de inicio |
| end_date | DATE | | Fecha de fin |
| capacity | INTEGER | | Capacidad máxima |
| created_by_id | INTEGER | REFERENCES users(id) | Creador del evento |
| created_at | TIMESTAMPTZ | DEFAULT NOW() | Fecha de creación |

**Índices**:
- `idx_events_created_by` en `created_by_id`
- `idx_events_dates` en `start_date, end_date`

### registrations

| Columna | Tipo | Constraints | Descripción |
|---------|------|-------------|-------------|
| id | SERIAL | PRIMARY KEY | ID único |
| event_id | INTEGER | REFERENCES events(id) ON DELETE CASCADE | Evento |
| attendee_name | VARCHAR(255) | NOT NULL | Nombre del asistente |
| attendee_email | VARCHAR(255) | NOT NULL | Email del asistente |
| notes | TEXT | | Notas adicionales |
| is_cancelled | BOOLEAN | DEFAULT FALSE | Estado de cancelación |
| registered_at | TIMESTAMPTZ | DEFAULT NOW() | Fecha de registro |

**Índices**:
- `idx_registrations_event_id` en `event_id`
- `idx_registrations_email` en `attendee_email`

**Constraint único**:
- `uq_registration_event_email` en `(event_id, attendee_email)` WHERE `is_cancelled = FALSE`

## Script de Inicialización

El esquema se inicializa automáticamente desde `app/db/sql/initial_schema.sql`:

```sql
-- Tipos ENUM
CREATE TYPE user_role AS ENUM ('public', 'member', 'admin');
CREATE TYPE donation_type AS ENUM ('diezmo', 'ofrenda', 'misiones', 'especial');
CREATE TYPE payment_method AS ENUM ('efectivo', 'transferencia', 'tarjeta', 'otro');

-- Tabla users
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) NOT NULL UNIQUE,
    hashed_password VARCHAR(255) NOT NULL,
    full_name VARCHAR(255),
    role user_role DEFAULT 'member',
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Tabla events
CREATE TABLE IF NOT EXISTS events (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    start_date DATE,
    end_date DATE,
    capacity INTEGER,
    created_by_id INTEGER REFERENCES users(id),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Tabla donations
CREATE TABLE IF NOT EXISTS donations (
    id SERIAL PRIMARY KEY,
    donor_name VARCHAR(255) NOT NULL,
    donor_document VARCHAR(50),
    donation_type donation_type NOT NULL,
    user_id INTEGER REFERENCES users(id),
    amount NUMERIC(12,2) NOT NULL,
    payment_method payment_method NOT NULL,
    donation_date DATE NOT NULL,
    note TEXT,
    event_id INTEGER REFERENCES events(id),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Tabla documents
CREATE TABLE IF NOT EXISTS documents (
    id SERIAL PRIMARY KEY,
    file_name VARCHAR(255) NOT NULL,
    stored_path VARCHAR(500) NOT NULL,
    mime_type VARCHAR(100) NOT NULL,
    size_bytes INTEGER NOT NULL,
    checksum VARCHAR(64),
    description TEXT,
    is_public BOOLEAN DEFAULT FALSE,
    donation_id INTEGER REFERENCES donations(id),
    user_id INTEGER REFERENCES users(id),
    event_id INTEGER REFERENCES events(id),
    uploaded_at TIMESTAMPTZ DEFAULT NOW()
);

-- Tabla registrations
CREATE TABLE IF NOT EXISTS registrations (
    id SERIAL PRIMARY KEY,
    event_id INTEGER NOT NULL REFERENCES events(id) ON DELETE CASCADE,
    attendee_name VARCHAR(255) NOT NULL,
    attendee_email VARCHAR(255) NOT NULL,
    notes TEXT,
    is_cancelled BOOLEAN DEFAULT FALSE,
    registered_at TIMESTAMPTZ DEFAULT NOW()
);

-- Índices
CREATE INDEX IF NOT EXISTS idx_donations_user_id ON donations(user_id);
CREATE INDEX IF NOT EXISTS idx_donations_donation_date ON donations(donation_date);
CREATE INDEX IF NOT EXISTS idx_documents_donation_id ON documents(donation_id);
CREATE INDEX IF NOT EXISTS idx_documents_user_id ON documents(user_id);
CREATE INDEX IF NOT EXISTS idx_events_created_by ON events(created_by_id);
CREATE INDEX IF NOT EXISTS idx_registrations_event_id ON registrations(event_id);
```

## Migraciones

No se utiliza Alembic. Los cambios al esquema se realizan mediante:

1. Crear nuevo script SQL en `app/db/sql/`
2. Aplicar manualmente o en deploy:
   ```bash
   docker exec ekklesia_db psql -U ekklesia -d ekklesia -f /path/to/migration.sql
   ```

## Backup y Restauración

### Backup

  ```bash
docker exec ekklesia_db pg_dump -U ekklesia ekklesia > backup.sql
  ```

### Restauración

```bash
cat backup.sql | docker exec -i ekklesia_db psql -U ekklesia -d ekklesia
```

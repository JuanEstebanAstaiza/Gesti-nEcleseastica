# Arquitectura Multi-Tenant

## Visión General

Ekklesia es una plataforma SaaS multi-tenant donde cada iglesia tiene:
- Base de datos completamente independiente
- Configuración personalizada
- Usuarios y datos aislados

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           EKKLESIA PLATFORM                                  │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐                   │
│  │   Iglesia A  │    │   Iglesia B  │    │   Iglesia C  │    ...            │
│  │  (tenant_a)  │    │  (tenant_b)  │    │  (tenant_c)  │                   │
│  └──────┬───────┘    └──────┬───────┘    └──────┬───────┘                   │
│         │                   │                   │                            │
│         ▼                   ▼                   ▼                            │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐                   │
│  │   DB: ekk_   │    │   DB: ekk_   │    │   DB: ekk_   │                   │
│  │   tenant_a   │    │   tenant_b   │    │   tenant_c   │                   │
│  └──────────────┘    └──────────────┘    └──────────────┘                   │
│                                                                              │
├─────────────────────────────────────────────────────────────────────────────┤
│                           MASTER DATABASE                                    │
│  ┌──────────────────────────────────────────────────────────────────────┐   │
│  │  ekklesia_master                                                      │   │
│  │  • tenants (iglesias registradas)                                     │   │
│  │  • super_admins (administradores de plataforma)                       │   │
│  │  • subscription_plans (planes de suscripción)                         │   │
│  └──────────────────────────────────────────────────────────────────────┘   │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

## Flujo de Acceso

### 1. Resolución de Tenant

```
Usuario accede a: iglesia-ejemplo.ekklesia.app
                  ────────────────────────────
                           │
                           ▼
              ┌─────────────────────────┐
              │  Middleware de Tenant   │
              │  • Extrae slug/subdominio│
              │  • Busca en master DB   │
              │  • Obtiene config tenant│
              └────────────┬────────────┘
                           │
                           ▼
              ┌─────────────────────────┐
              │  Conexión a DB Tenant   │
              │  • ekk_iglesia_ejemplo  │
              └─────────────────────────┘
```

### 2. Tipos de Acceso

| Ruta | Tipo | Descripción |
|------|------|-------------|
| `/` | Público | Landing de la iglesia |
| `/eventos` | Público | Eventos públicos |
| `/donar` | Público | Información de donaciones |
| `/nosotros` | Público | Quiénes somos |
| `/transmision` | Público/Auth | Misa en vivo |
| `/app` | Auth (feligrés) | Panel del usuario |
| `/admin` | Auth (admin) | Panel administrativo |
| `/superadmin` | Auth (super) | Panel super administrador |

## Estructura de Bases de Datos

### Master Database (ekklesia_master)

```sql
-- Tabla de tenants (iglesias)
CREATE TABLE tenants (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    slug VARCHAR(100) UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    subdomain VARCHAR(100) UNIQUE,
    custom_domain VARCHAR(255),
    db_name VARCHAR(100) NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    plan_id INTEGER REFERENCES subscription_plans(id),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    expires_at TIMESTAMPTZ
);

-- Super administradores de plataforma
CREATE TABLE super_admins (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    full_name VARCHAR(255),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Planes de suscripción
CREATE TABLE subscription_plans (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    max_users INTEGER,
    max_storage_mb INTEGER,
    features JSONB,
    price_monthly NUMERIC(10,2),
    is_active BOOLEAN DEFAULT TRUE
);
```

### Tenant Database (ekk_{slug})

Incluye todas las tablas existentes más:

```sql
-- Configuración de la iglesia
CREATE TABLE church_config (
    id SERIAL PRIMARY KEY,
    church_name VARCHAR(255) NOT NULL,
    slogan VARCHAR(500),
    description TEXT,
    about_us TEXT,
    mission TEXT,
    vision TEXT,
    address TEXT,
    phone VARCHAR(50),
    email VARCHAR(255),
    website VARCHAR(255),
    logo_url VARCHAR(500),
    cover_image_url VARCHAR(500),
    primary_color VARCHAR(7) DEFAULT '#8b5cf6',
    secondary_color VARCHAR(7) DEFAULT '#06b6d4',
    social_facebook VARCHAR(255),
    social_instagram VARCHAR(255),
    social_youtube VARCHAR(255),
    social_twitter VARCHAR(255),
    donation_info TEXT,
    bank_info JSONB,
    paypal_email VARCHAR(255),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Transmisiones en vivo
CREATE TABLE live_streams (
    id SERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    stream_url VARCHAR(500),
    youtube_video_id VARCHAR(50),
    facebook_video_id VARCHAR(100),
    platform VARCHAR(50) DEFAULT 'youtube',
    is_live BOOLEAN DEFAULT FALSE,
    scheduled_at TIMESTAMPTZ,
    started_at TIMESTAMPTZ,
    ended_at TIMESTAMPTZ,
    thumbnail_url VARCHAR(500),
    created_by_id INTEGER REFERENCES users(id),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Contenido público
CREATE TABLE public_content (
    id SERIAL PRIMARY KEY,
    slug VARCHAR(100) UNIQUE NOT NULL,
    title VARCHAR(255) NOT NULL,
    content TEXT,
    content_type VARCHAR(50) DEFAULT 'page',
    is_published BOOLEAN DEFAULT TRUE,
    published_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);
```

## Roles del Sistema

### Nivel Plataforma (Master)
- **Super Admin**: Gestiona toda la plataforma, crea iglesias y administradores

### Nivel Tenant (Por Iglesia)
- **Admin**: Administrador de la iglesia (gestión total)
- **Member**: Feligrés registrado
- **Public**: Usuario sin autenticar

## API Endpoints

### Super Admin API (`/api/superadmin/`)

```
POST   /api/superadmin/auth/login
GET    /api/superadmin/tenants
POST   /api/superadmin/tenants
GET    /api/superadmin/tenants/{id}
PATCH  /api/superadmin/tenants/{id}
DELETE /api/superadmin/tenants/{id}
POST   /api/superadmin/tenants/{id}/admins
GET    /api/superadmin/stats
```

### Tenant API (`/api/`)

Existentes + nuevos:

```
GET    /api/public/config          # Configuración pública de iglesia
GET    /api/public/events          # Eventos públicos
GET    /api/public/streams         # Transmisiones
GET    /api/public/content/{slug}  # Contenido público

PATCH  /api/admin/config           # Actualizar config iglesia
POST   /api/admin/streams          # Crear transmisión
PATCH  /api/admin/streams/{id}     # Actualizar transmisión
DELETE /api/admin/streams/{id}     # Eliminar transmisión
```

## Aislamiento de Datos

### Conexión por Tenant

```python
class TenantMiddleware:
    async def __call__(self, request, call_next):
        # 1. Extraer tenant del host/header
        tenant_slug = extract_tenant(request)
        
        # 2. Buscar tenant en master DB
        tenant = await get_tenant(tenant_slug)
        
        # 3. Crear conexión a DB del tenant
        request.state.db_url = f"postgresql://.../{tenant.db_name}"
        request.state.tenant = tenant
        
        return await call_next(request)
```

### Creación de Nuevo Tenant

```python
async def create_tenant(name: str, slug: str):
    # 1. Crear registro en master
    tenant = await master_db.create_tenant(name, slug)
    
    # 2. Crear base de datos
    await create_database(f"ekk_{slug}")
    
    # 3. Aplicar schema
    await apply_tenant_schema(f"ekk_{slug}")
    
    # 4. Crear admin inicial
    await create_initial_admin(tenant)
    
    return tenant
```

## Seguridad

1. **Aislamiento Total**: Cada iglesia tiene su propia DB
2. **Sin Cruce de Datos**: Imposible acceder a datos de otro tenant
3. **Tokens Separados**: JWT incluye tenant_id
4. **Validación en Cada Request**: Middleware verifica tenant


# Arquitectura

## Visión General

Sistema de gestión eclesiástica con arquitectura de microservicios separada:

- **Frontend**: Aplicación SPA en HTML/CSS/JS puro servida por Nginx
- **Backend**: API REST con FastAPI estructurada en capas
- **Base de datos**: PostgreSQL 15 con esquema normalizado
- **Almacenamiento**: Sistema de archivos local con opción S3

## Diagrama de Arquitectura

```
                                    ┌──────────────────────────────────────────┐
                                    │              DOCKER COMPOSE              │
                                    └──────────────────────────────────────────┘
                                                         │
        ┌────────────────────────────────────────────────┼────────────────────────────────────────────────┐
        │                                                │                                                │
        ▼                                                ▼                                                ▼
┌───────────────┐                               ┌───────────────┐                               ┌───────────────┐
│   FRONTEND    │                               │    BACKEND    │                               │   DATABASE    │
│   (Nginx)     │──────── HTTP/REST ──────────▶│   (FastAPI)   │──────── async/await ─────────▶│  (PostgreSQL) │
│   Port 3000   │                               │   Port 6076   │                               │   Port 5432   │
└───────────────┘                               └───────────────┘                               └───────────────┘
        │                                                │
        │                                                │
        ▼                                                ▼
  ┌───────────┐                                  ┌───────────────┐
  │  Browser  │◀──── WebSocket ─────────────────│ WS /api/ws/   │
  │   Client  │      notifications              │ notifications │
  └───────────┘                                  └───────────────┘
```

## Capas del Backend

```
┌─────────────────────────────────────────────────────────────────────┐
│                           ROUTERS                                    │
│   (app/api/routes/)                                                 │
│   • Definición de endpoints HTTP                                    │
│   • Validación de entrada con Pydantic                              │
│   • Inyección de dependencias (auth, session)                       │
└─────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────┐
│                           SERVICES                                   │
│   (app/api/services/)                                               │
│   • Lógica de negocio                                               │
│   • Orquestación de operaciones                                     │
│   • Validaciones de reglas de negocio                               │
└─────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────┐
│                         REPOSITORIES                                 │
│   (app/api/repositories/)                                           │
│   • Acceso a datos (CRUD)                                           │
│   • Queries SQLAlchemy                                              │
│   • Abstracción del ORM                                             │
└─────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────┐
│                           MODELS                                     │
│   (app/models/)                                                     │
│   • Entidades SQLAlchemy                                            │
│   • Relaciones entre tablas                                         │
│   • Constraints y defaults                                          │
└─────────────────────────────────────────────────────────────────────┘
```

## Decisiones Arquitectónicas

### 1. Separación Frontend/Backend

**Decisión**: Frontend y backend en contenedores separados con puertos distintos.

**Razones**:
- Mayor seguridad (aislamiento de servicios)
- Escalabilidad independiente
- Desarrollo paralelo de equipos
- Cacheo optimizado de assets estáticos

### 2. Sin Framework Frontend

**Decisión**: HTML/CSS/JavaScript vanilla en lugar de React/Vue/Angular.

**Razones**:
- Simplicidad y menor curva de aprendizaje
- Sin dependencias de build
- Rendimiento óptimo
- Mantenimiento a largo plazo

### 3. FastAPI + SQLAlchemy Async

**Decisión**: Backend asíncrono con FastAPI y SQLAlchemy 2.0.

**Razones**:
- Alto rendimiento con I/O asíncrono
- Documentación automática (OpenAPI)
- Validación robusta con Pydantic
- Type hints nativos

### 4. Sin Alembic

**Decisión**: Migraciones manuales con scripts SQL.

**Razones**:
- Control total sobre el DDL
- Simplicidad en entorno de desarrollo
- Evitar incompatibilidades con versiones

### 5. JWT con Access + Refresh Tokens

**Decisión**: Autenticación stateless con doble token.

**Razones**:
- Escalabilidad horizontal
- Tokens de corta duración (seguridad)
- Refresh automático sin re-login

## Módulos del Sistema

| Módulo | Ruta | Responsabilidad |
|--------|------|-----------------|
| Routes | `app/api/routes/` | Endpoints HTTP |
| Schemas | `app/api/schemas/` | DTOs Pydantic |
| Services | `app/api/services/` | Lógica de negocio |
| Repositories | `app/api/repositories/` | Acceso a datos |
| Models | `app/models/` | Entidades ORM |
| Core | `app/core/` | Config, security, deps |
| DB | `app/db/` | Sesión y SQL |

## Flujo de Datos

### Ejemplo: Crear Donación

```
1. Browser (localhost:3000)
   └─▶ POST /api/donations (JSON)
       
2. Backend (localhost:6076)
   ├─▶ Router: valida token JWT
   ├─▶ Schema: valida payload
   ├─▶ Service: aplica reglas de negocio
   ├─▶ Repository: inserta en DB
   ├─▶ WebSocket: broadcast a conectados
   └─▶ Response: 201 Created
       
3. Browser
   └─▶ Actualiza UI + toast notification
```

## Comunicación en Tiempo Real

```
┌──────────────┐                    ┌──────────────┐
│   Browser    │                    │   Backend    │
└──────────────┘                    └──────────────┘
       │                                   │
       │──── WS Connect ──────────────────▶│
       │     ?token=<jwt>                  │
       │                                   │
       │◀─── Connection OK ────────────────│
       │                                   │
       │                   [Nueva donación]│
       │◀─── {type: "donation.created"}───│
       │                                   │
       │                   [Nuevo evento]  │
       │◀─── {type: "event.created"} ─────│
       │                                   │
```

## Almacenamiento de Archivos

```
./storage/
├── 2024/
│   ├── 01/
│   │   ├── abc123_recibo.pdf
│   │   └── def456_comprobante.jpg
│   └── 02/
│       └── ...
```

- Organización por año/mes
- Nombre único con checksum
- Metadatos en tabla `documents`
- Validación MIME y tamaño

## Consideraciones de Seguridad

1. **CORS** configurado para origenes específicos
2. **JWT** con expiración corta (30 min access, 30 días refresh)
3. **Bcrypt** para hash de contraseñas
4. **Validación** de tipos MIME en uploads
5. **Headers de seguridad** en Nginx

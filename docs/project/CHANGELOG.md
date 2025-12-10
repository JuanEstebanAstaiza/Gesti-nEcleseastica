# Changelog

Todos los cambios notables del proyecto están documentados en este archivo.

El formato está basado en [Keep a Changelog](https://keepachangelog.com/es-ES/1.0.0/).

## [1.0.0] - 2024-12-10

### Añadido

#### Arquitectura
- Separación completa de frontend y backend en contenedores independientes
- Frontend servido por Nginx en puerto 3000
- Backend FastAPI en puerto 6076
- Configuración CORS para comunicación segura entre servicios
- WebSocket autenticado para notificaciones en tiempo real

#### Frontend
- Diseño moderno inspirado en Stripe/Instagram
- Sistema de autenticación con login/registro
- Dashboard con métricas en tiempo real
- Gestión de donaciones (crear, listar, exportar)
- Gestión de documentos (subir, descargar)
- Gestión de eventos y inscripciones
- Reportes con filtros y exportación CSV
- Notificaciones toast
- Responsive design completo
- Tema oscuro elegante

#### Backend
- Autenticación JWT completa (access + refresh tokens)
- CRUD de usuarios con roles (member, admin)
- CRUD de donaciones con tipos (diezmo, ofrenda, misiones, especial)
- Sistema de documentos con validación MIME y checksum
- Gestión de eventos con capacidad
- Inscripciones con validación de duplicados y cupo
- Reportes (summary, dashboard, export CSV)
- WebSocket para notificaciones broadcast
- Middleware CORS configurado

#### Base de Datos
- Esquema PostgreSQL normalizado
- Tipos ENUM para roles, tipos de donación y métodos de pago
- Índices optimizados
- Script de inicialización automática

#### DevOps
- Docker Compose con 3 servicios (db, backend, frontend)
- Health checks configurados
- Volúmenes persistentes
- Archivo .env para configuración

#### Testing
- Tests unitarios de seguridad (hashing, JWT)
- Tests de integración de API
- Tests end-to-end
- Tests de integración frontend-backend
- Configuración pytest con asyncio

#### Documentación
- README completo con instrucciones
- ARCHITECTURE.md con diagramas
- API_SPEC.md con todos los endpoints
- DATABASE_SCHEMA.md con ERD
- SECURITY.md con políticas
- TESTING.md con estrategia de tests
- DEPLOYMENT.md con guía de despliegue

### Cambiado
- Puerto del backend de 8000 a 6076
- Frontend separado del backend (antes compartían puerto)
- Estructura de docker-compose simplificada

### Eliminado
- Alembic (migraciones manuales con SQL)
- Servicio de frontend integrado en backend

## [0.2.0] - 2024-12-09

### Añadido
- Endpoints de reportes (summary, dashboard, export)
- WebSocket básico para notificaciones
- Inscripciones a eventos con validaciones
- Tests de reports y events

### Cambiado
- Migración a Pydantic V2 (ConfigDict, model_dump)
- Fixture de tests a scope function

## [0.1.0] - 2024-12-08

### Añadido
- Estructura inicial del proyecto
- Modelos base (User, Donation, Document, Event)
- Autenticación JWT básica
- Endpoints CRUD iniciales
- Docker Compose inicial
- Documentación base

---

## Convenciones

### Tipos de cambios
- **Añadido**: nuevas funcionalidades
- **Cambiado**: cambios en funcionalidades existentes
- **Obsoleto**: funcionalidades que serán eliminadas
- **Eliminado**: funcionalidades eliminadas
- **Corregido**: corrección de bugs
- **Seguridad**: vulnerabilidades corregidas

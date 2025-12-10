# Changelog

Todos los cambios notables del proyecto están documentados en este archivo.

El formato está basado en [Keep a Changelog](https://keepachangelog.com/es-ES/1.0.0/).

## [2.0.0] - 2024-12-10

### Añadido

#### Formato de Donaciones Actualizado
- **Montos separados**: Diezmo, Ofrenda, Misiones, Especial
- **Datos completos del donante**: Nombre, Cédula, Dirección, Teléfono, Email
- **Métodos de pago duales**: Efectivo y/o Transferencia con referencia
- **Metadatos**: Número de sobre, número de semana, número de recibo único
- **Soporte para donaciones anónimas (OSI)**

#### Reportes para Contaduría
- **Reporte mensual detallado** en formato CSV
  - Columnas: FECHA | NOMBRE | EFECTIVO | TRANSFERENCIA | DOCUMENTO | DIEZMO | OFRENDA | MISIONES | TOTAL
  - Subtotales por semana
  - Gran total del mes
- **Reporte semanal para contadora**
  - Tabla: CONCEPTO | EFECTIVO | TRANSFERENCIA | TOTAL
  - Cálculo automático de "Diezmo de diezmos" (10%)
  - Campos para testigos
  - Exportación a CSV
- **Cierre semanal** con auditoría completa

#### Módulo de Gastos Completo
- **Categorías personalizables**
  - Predeterminadas: Servicios, Arriendo, Salarios, Mantenimiento, etc.
  - Colores e iconos para UI
  - Presupuesto mensual por categoría
- **Subcategorías** para detalle fino
  - Ej: Servicios → Agua, Luz, Gas, Internet
- **Etiquetas libres** para clasificación
  - Urgente, Recurrente, Deducible, etc.
- **Gestión de gastos**
  - CRUD completo con validaciones
  - Estados: Pendiente → Aprobado → Pagado / Cancelado
  - Proveedor con NIT/Cédula
  - Múltiples métodos de pago
  - Número de factura y recibo
  - Gastos recurrentes (mensual, semanal, anual)
- **Documentos de soporte**
  - Facturas, recibos, cotizaciones, contratos
  - Checksum SHA-256 para integridad
- **Carpetas organizativas**
  - Por período (mes, año)
  - Jerárquicas (subcarpetas)
- **Reportes de gastos**
  - Mensual con totales por categoría
  - Seguimiento de presupuesto
  - Exportación CSV

#### Nuevas Tablas de Base de Datos
- `donation_summaries`: Resúmenes semanales
- `expense_categories`: Categorías de gastos
- `expense_subcategories`: Subcategorías
- `expense_tags`: Etiquetas
- `expenses`: Gastos
- `expense_documents`: Documentos de gastos
- `expense_folders`: Carpetas organizativas

#### Nuevos Endpoints
- `GET/POST /reports/donations/monthly` - Reporte mensual
- `GET /reports/donations/monthly/csv` - Exportar CSV mensual
- `GET /reports/donations/weekly/{week}` - Reporte semanal
- `GET /reports/donations/weekly/{week}/csv` - Exportar CSV semanal
- `POST /reports/donations/weekly/close` - Cerrar semana
- `GET/POST /expenses/categories` - Categorías
- `GET/POST /expenses/subcategories` - Subcategorías
- `GET/POST/DELETE /expenses/tags` - Etiquetas
- `GET/POST/PATCH/DELETE /expenses` - Gastos
- `POST /expenses/{id}/approve` - Aprobar gasto
- `POST /expenses/{id}/pay` - Marcar pagado
- `GET/POST /expenses/{id}/documents` - Documentos
- `GET/POST /expenses/folders` - Carpetas
- `GET /expenses/reports/monthly` - Reporte mensual gastos
- `GET /expenses/reports/summary` - Resumen dashboard

### Cambiado
- Modelo de `Donation` actualizado con campos separados por tipo
- Esquema de base de datos ampliado significativamente
- API_SPEC.md con documentación completa de nuevos endpoints
- DATABASE_SCHEMA.md con diagramas actualizados

---

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

---

## [0.2.0] - 2024-12-09

### Añadido
- Endpoints de reportes (summary, dashboard, export)
- WebSocket básico para notificaciones
- Inscripciones a eventos con validaciones
- Tests de reports y events

### Cambiado
- Migración a Pydantic V2 (ConfigDict, model_dump)
- Fixture de tests a scope function

---

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

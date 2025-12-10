# 🙏 Ekklesia - Sistema de Gestión Eclesiástica

<div align="center">

![Version](https://img.shields.io/badge/version-2.0.0-blue.svg)
![Python](https://img.shields.io/badge/python-3.11+-green.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688.svg)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15-336791.svg)
![Docker](https://img.shields.io/badge/Docker-ready-2496ED.svg)

*Plataforma SaaS Multi-Tenant para gestión administrativa de iglesias*

</div>

---

## ✨ Características Principales

### 💰 Gestión de Donaciones
- **Montos separados**: Diezmo, Ofrenda, Misiones, Especial
- **Datos completos del donante**: Nombre, Cédula, Dirección, Teléfono
- **Métodos de pago**: Efectivo y/o Transferencia
- **Donaciones anónimas (OSI)**
- **Número de sobre y recibo único**

### 📊 Reportes para Contaduría
- **Reporte mensual** con formato Excel/CSV
  - Columnas: FECHA | NOMBRE | EFECTIVO | TRANSFERENCIA | DOCUMENTO | DIEZMO | OFRENDA | MISIONES | TOTAL
  - Subtotales por semana y totales generales
- **Reporte semanal** para contadora
  - Tabla de totales por concepto y método de pago
  - Cálculo automático de "Diezmo de diezmos" (10%)
  - Campos para testigos

### 💸 Módulo de Gastos
- **Categorías personalizables**: Servicios, Arriendo, Salarios, Mantenimiento
- **Subcategorías** para detalle: Agua, Luz, Gas, Internet
- **Etiquetas**: Urgente, Recurrente, Deducible
- **Flujo de aprobación**: Pendiente → Aprobado → Pagado
- **Documentos de soporte**: Facturas, recibos, cotizaciones
- **Presupuesto mensual** por categoría

### Más Funcionalidades
- 🔐 **Autenticación JWT** - Access y refresh tokens
- 📄 **Documentos** - Subida con validación y trazabilidad SHA-256
- 📅 **Eventos** - Creación e inscripciones con cupo
- 🔔 **Notificaciones** - WebSocket en tiempo real
- 🎨 **UI Moderna** - Diseño elegante estilo Stripe/Instagram
- 🏢 **Multi-Tenant** - Base de datos independiente por iglesia

---

## 🚀 Inicio Rápido

### Requisitos

- Docker y Docker Compose

### Instalación

```bash
# 1. Clonar el repositorio
git clone <repository-url>
cd GestionEcleseastica

# 2. Levantar los servicios
docker-compose up -d --build

# 3. ¡Listo! Accede a:
#    Frontend: http://localhost:3000
#    API Docs: http://localhost:6076/docs
```

---

## 🌐 URLs de Acceso

| Servicio | URL | Descripción |
|----------|-----|-------------|
| 🖥️ Frontend | http://localhost:3000 | Interfaz de usuario |
| ⚡ Backend API | http://localhost:6076/api | API REST |
| 📚 Swagger | http://localhost:6076/docs | Documentación interactiva |
| 🗃️ PostgreSQL | localhost:55432 | Base de datos |

---

## 📁 Estructura del Proyecto

```
├── app/                    # 🐍 Backend FastAPI
│   ├── api/               
│   │   ├── routes/        # Endpoints (donations, expenses, reports...)
│   │   ├── schemas/       # DTOs Pydantic
│   │   ├── services/      # Lógica de negocio
│   │   └── repositories/  # Acceso a datos
│   ├── core/              # Config, security, storage
│   ├── db/                
│   │   └── sql/           # Scripts de esquema
│   └── models/            # ORM SQLAlchemy
├── frontend/              # 🎨 Frontend
│   ├── css/              
│   ├── js/               
│   └── index.html        
├── tests/                 # 🧪 Pruebas
├── docs/                  # 📚 Documentación
└── docker-compose.yml     # 🐳 Orquestación
```

---

## 💰 Formato de Donación

Basado en el comprobante oficial de la iglesia:

```
"Honra al Señor con tus riquezas y con los
primeros frutos de tus cosechas."          Diezmos    $_________
                                            Ofrendas   $_________
Proverbios 3:9-10                           Misiones   $_________
                                            TOTAL      $_________

Nombre: _________________________    [X] Efectivo
Dirección: ______________________    [ ] Transferencia
Cédula: _________________________    Fecha: DD/MM/AAAA

            IGLESIA COMUNIDAD CRISTIANA DE FE
```

---

## 📊 Formato de Reporte Semanal

Para la contadora:

```
                    RELACIÓN DE DIEZMOS Y OFRENDAS

FECHA: ____________    SEMANA: ____
NÚMERO DE SOBRES: ____

┌────────────┬────────────┬───────────────┬──────────┐
│ CONCEPTO   │  EFECTIVO  │ TRANSFERENCIA │  TOTAL   │
├────────────┼────────────┼───────────────┼──────────┤
│ DIEZMOS    │            │               │          │
│ OFRENDAS   │            │               │          │
│ MISIONES   │            │               │          │
├────────────┼────────────┼───────────────┼──────────┤
│ VALOR TOTAL│            │               │          │
└────────────┴────────────┴───────────────┴──────────┘

DIEZMOS DE DIEZMOS: ____________

TESTIGO 1: _____________    TESTIGO 2: _____________
```

---

## 🔑 Roles de Usuario

| Rol | Permisos |
|-----|----------|
| **Public** | Ver eventos públicos, inscribirse, ver información de la iglesia |
| **Member** | + Registrar donaciones propias, subir documentos, ver historial |
| **Admin** | + Gestión completa, reportes, gastos, exportar, cerrar semanas |
| **SuperAdmin** | + Gestión de iglesias (multi-tenant), crear administradores |

---

## 🧪 Ejecutar Pruebas

```bash
# Todas las pruebas
docker exec -it ekklesia_backend pytest -v

# Pruebas de integración
pytest tests/test_integration_endpoints.py -v

# Solo tests de donaciones
pytest app/tests/test_donations.py -v
```

---

## 📖 Documentación

| Documento | Contenido |
|-----------|-----------|
| [📐 Arquitectura](docs/architecture/ARCHITECTURE.md) | Diseño del sistema |
| [🏢 Multi-Tenant](docs/architecture/MULTI_TENANT.md) | Arquitectura multi-inquilino |
| [🔌 API Spec](docs/api/API_SPEC.md) | Endpoints y respuestas |
| [🗃️ Base de Datos](docs/db/DATABASE_SCHEMA.md) | Esquema y tablas |
| [🔒 Seguridad](docs/security/SECURITY.md) | Políticas JWT y CORS |
| [🚀 Despliegue](docs/deployment/DEPLOYMENT.md) | Guía de producción |
| [🧪 Testing](docs/testing/TESTING.md) | Estrategia de pruebas |

---

## 🛠️ Comandos Útiles

```bash
# Ver logs en tiempo real
docker-compose logs -f backend

# Reiniciar servicios
docker-compose restart

# Backup de base de datos
docker exec ekklesia_db pg_dump -U ekklesia ekklesia > backup.sql

# Aplicar esquema actualizado
docker exec ekklesia_db psql -U ekklesia -d ekklesia -f /code/app/db/sql/tenant_schema.sql

# Detener todo
docker-compose down

# Reconstruir completamente
docker-compose down -v && docker-compose up -d --build
```

---

## 📝 Changelog

Ver [CHANGELOG.md](docs/project/CHANGELOG.md) para el historial completo de cambios.

### Último release: v2.0.0
- ✅ Formato de donación con montos separados
- ✅ Reportes para contaduría (mensual y semanal)
- ✅ Módulo completo de gastos con categorías
- ✅ Documentos de soporte para gastos
- ✅ Cierre semanal con testigos

---

<div align="center">

**Desarrollado con ❤️ para la comunidad eclesiástica**

*"Honra al Señor con tus riquezas" - Proverbios 3:9*

</div>

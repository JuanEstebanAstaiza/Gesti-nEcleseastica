# 🙏 Ekklesia - Sistema de Gestión Eclesiástica

<div align="center">

![Version](https://img.shields.io/badge/version-1.0.0-blue.svg)
![Python](https://img.shields.io/badge/python-3.11+-green.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688.svg)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15-336791.svg)
![Docker](https://img.shields.io/badge/Docker-ready-2496ED.svg)

*Plataforma web moderna para gestión de donaciones, eventos e inscripciones*

</div>

---

## ✨ Características

- 🔐 **Autenticación JWT** - Access y refresh tokens
- 💰 **Gestión de Donaciones** - Diezmos, ofrendas, misiones
- 📄 **Documentos** - Subida con validación y trazabilidad
- 📅 **Eventos** - Creación e inscripciones con cupo
- 📊 **Reportes** - Dashboard y exportación CSV
- 🔔 **Notificaciones** - WebSocket en tiempo real
- 🎨 **UI Moderna** - Diseño elegante estilo Stripe/Instagram

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
│   │   ├── routes/        # Endpoints
│   │   ├── schemas/       # DTOs Pydantic
│   │   ├── services/      # Lógica de negocio
│   │   └── repositories/  # Acceso a datos
│   ├── core/              # Config, security
│   ├── db/                # Sesión y SQL
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

## 🔑 Roles de Usuario

| Rol | Permisos |
|-----|----------|
| **Public** | Ver eventos, inscribirse |
| **Member** | + Crear donaciones, subir documentos |
| **Admin** | + Gestión de usuarios, reportes, exportar |

---

## 🧪 Ejecutar Pruebas

```bash
# Todas las pruebas
docker exec -it ekklesia_backend pytest -v

# Pruebas de integración
pytest tests/test_integration_endpoints.py -v
```

---

## 📖 Documentación

| Documento | Contenido |
|-----------|-----------|
| [📐 Arquitectura](docs/architecture/ARCHITECTURE.md) | Diseño del sistema |
| [🔌 API Spec](docs/api/API_SPEC.md) | Endpoints y respuestas |
| [🗃️ Base de Datos](docs/db/DATABASE_SCHEMA.md) | Esquema y tablas |
| [🔒 Seguridad](docs/security/SECURITY.md) | Políticas JWT y CORS |
| [🚀 Despliegue](docs/deployment/DEPLOYMENT.md) | Guía de producción |
| [🧪 Testing](docs/testing/TESTING.md) | Estrategia de pruebas |

---

## 🛠️ Comandos Útiles

```bash
# Ver logs
docker-compose logs -f backend

# Reiniciar servicios
docker-compose restart

# Backup de base de datos
docker exec ekklesia_db pg_dump -U ekklesia ekklesia > backup.sql

# Detener todo
docker-compose down
```

---

## 📝 Changelog

Ver [CHANGELOG.md](docs/project/CHANGELOG.md) para el historial de cambios.

---

<div align="center">

**Desarrollado con ❤️ para la comunidad eclesiástica**

</div>

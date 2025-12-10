# Ekklesia Admin

Plataforma web moderna para gestión administrativa eclesiástica: donaciones, eventos, inscripciones y trazabilidad documental, con arquitectura separada de frontend (Nginx) y backend (FastAPI) sobre PostgreSQL.

## 🚀 Características

- **Autenticación JWT** completa (access + refresh tokens)
- **Gestión de donaciones** con tipos (diezmo, ofrenda, misiones, especial)
- **Subida de documentos** con validación de tipo/tamaño y trazabilidad
- **Eventos e inscripciones** con control de capacidad
- **Reportes y exportación CSV**
- **Notificaciones en tiempo real** vía WebSocket
- **Frontend moderno** estilo Stripe/Instagram
- **API RESTful** documentada automáticamente

## 📋 Requisitos

- Docker y Docker Compose
- Git

## ⚡ Inicio Rápido

### 1. Clonar y configurar

```bash
git clone <repository-url>
cd GestionEcleseastica
```

### 2. Crear archivo `.env`

```bash
# El archivo .env ya está configurado con valores por defecto
# Ajusta SECRET_KEY y las credenciales de PostgreSQL para producción
```

### 3. Levantar los contenedores

```bash
docker-compose up -d --build
```

### 4. Acceder a la aplicación

| Servicio | URL | Descripción |
|----------|-----|-------------|
| **Frontend** | http://localhost:3000 | Interfaz de usuario |
| **Backend API** | http://localhost:6076/api | API REST |
| **API Docs** | http://localhost:6076/docs | Documentación Swagger |
| **PostgreSQL** | localhost:55432 | Base de datos |

## 🏗️ Arquitectura

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│    Frontend     │     │     Backend     │     │   PostgreSQL    │
│   (Nginx:3000)  │────▶│ (FastAPI:6076)  │────▶│    (DB:5432)    │
└─────────────────┘     └─────────────────┘     └─────────────────┘
     HTML/CSS/JS              Python              Datos + SQL
```

### Contenedores Docker

| Contenedor | Imagen | Puerto | Descripción |
|------------|--------|--------|-------------|
| `ekklesia_frontend` | nginx:alpine | 3000:80 | Servidor web frontend |
| `ekklesia_backend` | python:3.11-slim | 6076:6076 | API FastAPI |
| `ekklesia_db` | postgres:15-alpine | 55432:5432 | Base de datos |

## 📁 Estructura del Proyecto

```
├── app/                    # Backend FastAPI
│   ├── api/
│   │   ├── routes/        # Endpoints HTTP
│   │   ├── schemas/       # Esquemas Pydantic
│   │   ├── services/      # Lógica de negocio
│   │   └── repositories/  # Acceso a datos
│   ├── core/              # Configuración, seguridad, deps
│   ├── db/                # Sesión y scripts SQL
│   └── models/            # Modelos SQLAlchemy
├── frontend/              # Frontend HTML/CSS/JS
│   ├── css/
│   ├── js/
│   └── index.html
├── tests/                 # Pruebas pytest
├── docs/                  # Documentación
├── docker-compose.yml     # Orquestación
└── requirements.txt       # Dependencias Python
```

## 🔐 Roles de Usuario

| Rol | Descripción | Permisos |
|-----|-------------|----------|
| `public` | Sin autenticación | Ver eventos, inscribirse |
| `member` | Usuario registrado | Todo lo público + crear donaciones, subir documentos |
| `admin` | Administrador | Todo + gestión de usuarios, reportes, exportaciones |

## 🧪 Ejecutar Pruebas

```bash
# Pruebas unitarias y de integración
docker exec -it ekklesia_backend pytest -v

# Pruebas de integración frontend-backend (con contenedores corriendo)
pytest tests/test_integration_endpoints.py -v
```

## 📚 Documentación Relacionada

| Documento | Descripción |
|-----------|-------------|
| [ARCHITECTURE.md](../architecture/ARCHITECTURE.md) | Arquitectura del sistema |
| [API_SPEC.md](../api/API_SPEC.md) | Especificación de la API |
| [DATABASE_SCHEMA.md](../db/DATABASE_SCHEMA.md) | Esquema de base de datos |
| [SECURITY.md](../security/SECURITY.md) | Políticas de seguridad |
| [TESTING.md](../testing/TESTING.md) | Estrategia de testing |
| [DEPLOYMENT.md](../deployment/DEPLOYMENT.md) | Guía de despliegue |
| [CHANGELOG.md](../project/CHANGELOG.md) | Historial de cambios |

## 🛠️ Desarrollo Local

```bash
# Levantar solo la base de datos
docker-compose up -d db

# Instalar dependencias localmente
pip install -r requirements.txt

# Ejecutar backend en modo desarrollo
uvicorn app.main:app --reload --port 6076

# Servir frontend localmente
cd frontend && python -m http.server 3000
```

## 📝 Licencia

Este proyecto es para uso interno de la iglesia. Ver [LICENSE_INFO.md](../project/LICENSE_INFO.md).

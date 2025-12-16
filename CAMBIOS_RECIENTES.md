# Ekklesia - Sistema de Gestión Eclesiástica

## 🎉 Estado: FUNCIONAL | 100% Pruebas Pasando

**Última actualización:** 15 de Diciembre 2025

---

## 📋 Índice

1. [Acceso al Sistema](#-acceso-al-sistema)
2. [Datos de Prueba](#-datos-de-prueba)
3. [Flujos de Prueba](#-flujos-de-prueba)
4. [Arquitectura](#-arquitectura)
5. [Funcionalidades](#-funcionalidades)
6. [Historial de Cambios](#-historial-de-cambios)

---

## 🔐 Acceso al Sistema

### URLs

| Recurso | URL |
|---------|-----|
| **Landing Page** | http://localhost:3000 |
| **Super Admin** | http://localhost:3000/superadmin.html |
| **API Docs** | http://localhost:6076/docs |
| **API ReDoc** | http://localhost:6076/redoc |

### Credenciales

| Rol | Email | Contraseña | Acceso |
|-----|-------|------------|--------|
| **Super Admin** | `super@ekklesia.com` | `superadmin123` | Panel de gestión de iglesias |
| **Admin Iglesia** | `admin@comunidadfe.org` | `admin123` | Panel completo de iglesia |
| **Tesorero** | `tesorero@comunidadfe.org` | `admin123` | Panel de administración |
| **Secretaria** | `secretaria@comunidadfe.org` | `admin123` | Panel de administración |
| **Miembro 1** | `juan.perez@email.com` | `member123` | Panel de feligrés |
| **Miembro 2** | `maria.rodriguez@email.com` | `member123` | Panel de feligrés |
| **Miembro 3** | `pedro.sanchez@email.com` | `member123` | Panel de feligrés |

---

## 📊 Datos de Prueba

### Iglesia Configurada

| Campo | Valor |
|-------|-------|
| **Nombre** | Iglesia Comunidad de Fe |
| **Slogan** | Transformando vidas con el amor de Cristo |
| **Ciudad** | Medellín, Colombia |
| **Teléfono** | +57 4 123 4567 |
| **Email** | contacto@comunidadfe.org |
| **Website** | www.comunidadfe.org |

### Horarios de Servicio

| Día | Evento | Hora |
|-----|--------|------|
| Domingo | Escuela Dominical | 09:00 |
| Domingo | Culto Principal | 10:30 |
| Miércoles | Estudio Bíblico | 19:00 |
| Viernes | Reunión de Jóvenes | 19:30 |

### Eventos Disponibles (41 eventos)

| Evento | Tipo |
|--------|------|
| Conferencia de Jóvenes 2024 | Público |
| Culto de Navidad 2024 | Público |
| Retiro de Jóvenes "Renuévate" | Público |
| Conferencia de Mujeres | Público |
| Estudio Bíblico: Libro de Romanos | Público |
| Campaña de Alimentación | Público |
| Culto de Año Nuevo | Público |
| Escuela para Padres | Público |
| Concierto de Alabanza | Público |
| Bautismo en Agua | Público |
| Reunión de Líderes | Privado |

### Anuncios Activos (25 anuncios)

| Anuncio | Visibilidad |
|---------|-------------|
| Inscripciones Retiro de Jóvenes | Público |
| Horario Especial Navidad | Público |
| Campaña de Alimentos | Público |
| Nuevas Células de Estudio | Público |
| Actualización de Datos | Privado |

### Planes de Suscripción

| Plan | Usuarios | Almacenamiento | Precio/Mes |
|------|----------|----------------|------------|
| Básico | 50 | 1 GB | $29,900 COP |
| Profesional | 200 | 5 GB | $79,900 COP |
| Empresarial | Ilimitado | 20 GB | $149,900 COP |

---

## 🧪 Flujos de Prueba

### 1. Landing Page Pública (Sin Login)

1. Ir a **http://localhost:3000**
2. **Verificar elementos visibles:**
   - ✅ Header con nombre de iglesia y navegación
   - ✅ Hero section con slogan
   - ✅ Horarios de servicio (Domingo, Miércoles, Viernes)
   - ✅ Próximos eventos
   - ✅ Anuncios públicos
   - ✅ Botón "Ingresar"
3. **Probar navegación:**
   - Click "Nosotros" → Info de la iglesia
   - Click "Eventos" → Lista de eventos públicos con botón "Inscribirse"
   - Click "Donar" → Tarjetas de tipos de donación y métodos de pago
   - Click "En Vivo" → Sección de transmisiones

### 2. Inscripción a Eventos (Nuevo flujo)

1. Ir a **http://localhost:3000** → Click "Eventos"
2. **Sin estar logueado:**
   - Click "Inscribirse" en cualquier evento
   - ✅ Debe mostrar modal de login con mensaje informativo
3. **Registrarse como nuevo usuario:**
   - En el modal, click "Registrarse"
   - Llenar datos y enviar
   - ✅ Debe auto-loguear e inscribir al evento automáticamente
4. **Ya logueado:**
   - Click "Inscribirse"
   - ✅ Debe inscribir directamente y cambiar botón a "Inscrito"

### 3. Login y Registro

1. Click en **"Ingresar"**
2. **Probar login admin:**
   - Email: `admin@comunidadfe.org`
   - Contraseña: `admin123`
   - ✅ Debe mostrar Dashboard con secciones admin
3. **Probar login miembro:**
   - Email: `juan.perez@email.com`
   - Contraseña: `member123`
   - ✅ Debe mostrar Dashboard sin secciones admin
4. **Probar logout:**
   - Click en el botón de salir
   - ✅ Debe volver a la landing page

### 3. Panel Admin de Iglesia

**Login:** `admin@comunidadfe.org` / `admin123`

| Sección | Acciones a Probar |
|---------|-------------------|
| **Dashboard** | Ver métricas de donaciones, eventos próximos |
| **Donaciones** | Registrar nueva donación, ver historial |
| **Eventos** | Crear evento, editar ✏️, eliminar, ver registrados/capacidad |
| **Gastos** | Crear gasto, aprobar, marcar como pagado |
| **Anuncios** | Publicar anuncio público/privado |
| **Configuración** | Editar nombre, misión, visión, redes sociales, **transmisiones en vivo** |
| **Reportes** | Ver balance, filtrar por período, exportar Excel/PDF |

### 5. Gestión de Transmisiones en Vivo (Admin)

**Login:** `admin@comunidadfe.org` / `admin123`

1. Ir a **Configuración** → Scroll hasta "Transmisión en Vivo"
2. **Agregar transmisión:**
   - Título: "Servicio Dominical"
   - Plataforma: YouTube
   - URL: https://youtube.com/watch?v=xxxxx
   - Click "Agregar Transmisión"
3. **Activar transmisión:**
   - Click botón "Iniciar" en la transmisión
   - ✅ Badge cambia a "En Vivo"
4. **Detener transmisión:**
   - Click botón "Detener"
   - ✅ Badge cambia a "Inactivo"
5. **Eliminar transmisión:**
   - Click botón de eliminar (icono 🗑️)

### 4. Panel de Miembro/Feligrés

**Login:** `juan.perez@email.com` / `member123`

| Sección | Acciones a Probar |
|---------|-------------------|
| **Inicio** | Ver eventos próximos, anuncios |
| **Mis Eventos** | Ver eventos inscritos |
| **Comunidad** | Ver anuncios de la iglesia |
| **En Vivo** | Ver transmisiones |
| **Mi Perfil** | Ver/editar datos personales |

### 5. Panel Super Administrador

**URL:** http://localhost:3000/superadmin.html  
**Login:** `super@ekklesia.com` / `superadmin123`

| Sección | Acciones a Probar |
|---------|-------------------|
| **Dashboard** | Ver estadísticas globales |
| **Iglesias** | Ver lista de tenants, crear nuevo |
| **Planes** | Crear plan, editar precios, eliminar |
| **Backups** | Crear backup, descargar, subir |
| **Ingresos** | Ver MRR, ARR, desglose por plan |

---

## 🏗️ Arquitectura

### Contenedores Docker

| Contenedor | Puerto | Descripción |
|------------|--------|-------------|
| `ekklesia_frontend` | 3000 | Nginx + Frontend estático |
| `ekklesia_backend` | 6076 | FastAPI + Python |
| `ekklesia_db` | 55432 | PostgreSQL (datos de iglesia) |
| `ekklesia_db_master` | 55433 | PostgreSQL (tenants y planes) |

### Bases de Datos

| Base de Datos | Host | Contenido |
|---------------|------|-----------|
| `ekklesia` | db:5432 | Usuarios, eventos, donaciones, gastos |
| `ekklesia_master` | db_master:5432 | Super admins, tenants, planes |

### Estructura de Carpetas

```
├── app/                    # Backend FastAPI
│   ├── api/routes/         # Endpoints
│   ├── api/schemas/        # Modelos Pydantic
│   ├── api/services/       # Lógica de negocio
│   ├── core/               # Configuración, seguridad
│   └── db/                 # Sesiones y SQL
├── frontend/               # Frontend estático
│   ├── css/styles.css      # Estilos
│   ├── js/app.js           # JavaScript principal
│   ├── index.html          # Landing + Panel usuario
│   └── superadmin.html     # Panel super admin
└── docker-compose.yml      # Orquestación
```

---

## ✨ Funcionalidades

### Endpoints Públicos (Sin Auth)

```
GET  /api/public/config         - Info de la iglesia
GET  /api/public/events         - Eventos públicos
GET  /api/public/announcements  - Anuncios públicos
GET  /api/public/streams        - Transmisiones
GET  /api/public/donation-info  - Info de donaciones
```

### Endpoints de Autenticación

```
POST /api/auth/register         - Registrar usuario
POST /api/auth/login            - Iniciar sesión
POST /api/auth/refresh          - Renovar token
GET  /api/auth/me               - Perfil actual
```

### Endpoints Admin de Iglesia

```
GET/POST   /api/donations       - Donaciones
GET/POST   /api/events          - Eventos
GET/POST   /api/expenses        - Gastos
GET/POST   /api/admin/announcements - Anuncios
GET/PATCH  /api/admin/config    - Configuración
```

### Endpoints Super Admin

```
POST /api/superadmin/auth/login     - Login super admin
GET  /api/superadmin/tenants        - Lista iglesias
GET  /api/superadmin/plans          - Lista planes
GET  /api/superadmin/stats          - Estadísticas
GET  /api/superadmin/revenue        - Métricas de ingresos
GET  /api/superadmin/backups        - Lista backups
POST /api/superadmin/backups/{id}   - Crear backup
```

---

## 📜 Historial de Cambios

### Sesión Actual (15 Dic 2025)

| Cambio | Descripción |
|--------|-------------|
| ✅ **Panel Admin Clicks** | Corregido selector CSS `#user-app` para navegación de secciones |
| ✅ **Página Donar** | Diseño mejorado con tarjetas de tipos de donación y métodos de pago |
| ✅ **Eventos Públicos** | Nuevo diseño con botón "Inscribirse" para cada evento |
| ✅ **Registro a Eventos** | Flujo completo: si usuario no logueado → modal login → auto-inscripción |
| ✅ **Auto-login Registro** | Después de registrarse, auto-login e inscripción al evento pendiente |
| ✅ **Transmisiones en Vivo** | Nueva sección en Configuración para gestionar streams |
| ✅ **CRUD Streams** | Agregar, activar/desactivar, eliminar transmisiones de YouTube/Facebook/Twitch |

### Sesión Anterior (15 Dic 2025 - mañana)

| Cambio | Descripción |
|--------|-------------|
| ✅ **editEvent()** | Función agregada para editar eventos existentes |
| ✅ **Registrados** | Contador de inscritos/capacidad en tabla de eventos admin |
| ✅ **Reportes** | Filtros de período funcionales (mes, trimestre, año, personalizado) |
| ✅ **Resumen de Gastos** | Nuevo panel con desglose por estado (pendientes, aprobados, pagados) |
| ✅ **Configuración** | Serialización JSON corregida para `service_schedule` y `bank_info` |
| ✅ **Formulario Eventos** | Soporte para crear y editar eventos desde el mismo formulario |

### Sesión Anterior (12 Dic 2025)

| Cambio | Descripción |
|--------|-------------|
| ✅ Contraseñas | Hashes bcrypt regenerados con `fix_passwords.py` |
| ✅ `/auth/me` | Endpoint agregado para perfil de usuario |
| ✅ Schema | `service_schedule` cambiado a `list \| dict \| None` |
| ✅ DB Master | URL corregida a `db_master:5432` |
| ✅ Pruebas | 18/18 endpoints verificados (100%) |

### Cambios Anteriores

| Cambio | Descripción |
|--------|-------------|
| 🔧 Multi-tenant | Eliminado, sistema simplificado a una iglesia |
| 🔧 CORS | Configurado `allow_origins=["*"]` |
| 🔧 JavaScript | Event listeners seguros con `addEvent()` |
| ➕ Estilos | +400 líneas CSS para landing page |
| ➕ Gastos | Módulo completo con flujo de aprobación |
| ➕ Super Admin | Panel restaurado con backups y métricas |

---

## ⚠️ Notas Importantes

1. **Después de reconstruir contenedores**, ejecutar:
   ```bash
   docker cp fix_passwords.py ekklesia_backend:/code/fix_passwords.py
   docker exec ekklesia_backend python /code/fix_passwords.py
   ```

2. **Backups** se almacenan en `./backups/` dentro del contenedor backend.

3. **Flujo de gastos:**
   - `pending` → `approved` → `paid`
   - `pending` → `rejected`

4. **Roles:**
   - `superadmin` - Gestiona toda la plataforma
   - `admin` - Gestiona una iglesia
   - `member` - Usuario regular (feligrés)

---

*Documentación generada para Ekklesia Platform v1.0*

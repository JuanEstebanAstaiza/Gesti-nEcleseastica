# Glosario

## Términos de Negocio

| Término | Definición |
|---------|------------|
| **Diezmo** | Donación correspondiente al 10% de los ingresos del fiel |
| **Ofrenda** | Donación voluntaria sin monto específico |
| **Misiones** | Donación destinada a proyectos misioneros |
| **Ofrenda Especial** | Donación para propósitos específicos (construcción, eventos) |
| **Inscripción** | Registro de asistencia a un evento |
| **Comprobante** | Documento que respalda una donación |

## Términos Técnicos

| Término | Definición |
|---------|------------|
| **JWT** | JSON Web Token - Estándar de tokens para autenticación |
| **Access Token** | Token de corta duración para autenticar requests |
| **Refresh Token** | Token de larga duración para obtener nuevos access tokens |
| **CORS** | Cross-Origin Resource Sharing - Política de seguridad de navegadores |
| **ORM** | Object-Relational Mapping - Mapeo objeto-relacional |
| **API REST** | Interfaz de programación de aplicaciones con arquitectura REST |
| **WebSocket** | Protocolo de comunicación bidireccional en tiempo real |

## Roles de Usuario

| Rol | Descripción |
|-----|-------------|
| **public** | Usuario no autenticado, acceso solo a endpoints públicos |
| **member** | Usuario registrado, puede crear donaciones y documentos |
| **admin** | Administrador, acceso total incluyendo gestión de usuarios |

## Tipos de Donación

| Tipo | Código | Descripción |
|------|--------|-------------|
| Diezmo | `diezmo` | Porcentaje de ingresos |
| Ofrenda | `ofrenda` | Donación libre |
| Misiones | `misiones` | Para proyectos misioneros |
| Especial | `especial` | Propósito específico |

## Métodos de Pago

| Método | Código | Descripción |
|--------|--------|-------------|
| Efectivo | `efectivo` | Pago en billetes/monedas |
| Transferencia | `transferencia` | Transferencia bancaria |
| Tarjeta | `tarjeta` | Débito o crédito |
| Otro | `otro` | Cualquier otro método |

## Componentes del Sistema

| Componente | Descripción |
|------------|-------------|
| **Frontend** | Interfaz de usuario en HTML/CSS/JS |
| **Backend** | API REST en FastAPI |
| **Database** | PostgreSQL para persistencia |
| **Storage** | Sistema de archivos para documentos |

## Endpoints Principales

| Endpoint | Descripción |
|----------|-------------|
| `/api/auth/*` | Autenticación (login, registro, refresh) |
| `/api/users/*` | Gestión de usuarios |
| `/api/donations/*` | Gestión de donaciones |
| `/api/documents/*` | Gestión de documentos |
| `/api/events/*` | Gestión de eventos |
| `/api/reports/*` | Reportes y exportaciones |
| `/api/ws/*` | WebSocket para notificaciones |

# Políticas de Seguridad

## Autenticación

### JWT (JSON Web Tokens)

El sistema utiliza autenticación basada en tokens JWT con dos tipos:

| Token | Expiración | Propósito |
|-------|------------|-----------|
| Access Token | 30 minutos | Autenticación de requests |
| Refresh Token | 30 días | Renovación de access tokens |

### Flujo de Autenticación

```
┌─────────┐      ┌─────────┐      ┌─────────┐
│ Cliente │      │ Backend │      │   DB    │
└────┬────┘      └────┬────┘      └────┬────┘
     │                │                │
     │ POST /login    │                │
     │───────────────▶│                │
     │                │ Verify password│
     │                │───────────────▶│
     │                │◀───────────────│
     │                │                │
     │ {access, refresh}               │
     │◀───────────────│                │
     │                │                │
     │ GET /resource  │                │
     │ Authorization: │                │
     │ Bearer <access>│                │
     │───────────────▶│                │
     │                │ Validate JWT   │
     │◀───────────────│                │
     │                │                │
     │ POST /refresh  │                │
     │ {refresh_token}│                │
     │───────────────▶│                │
     │ {new_access}   │                │
     │◀───────────────│                │
```

### Estructura del Token

```json
{
  "sub": "user_id",
  "scope": "access",  // o "refresh"
  "exp": 1704067200,
  "iat": 1704063600
}
```

## Hashing de Contraseñas

### Algoritmo

- **Bcrypt** con factor de costo 12
- Sal única por contraseña (generada automáticamente)

### Implementación

```python
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)
```

## Control de Acceso (RBAC)

### Roles

| Rol | Nivel | Descripción |
|-----|-------|-------------|
| `public` | 0 | Sin autenticación |
| `member` | 1 | Usuario registrado |
| `admin` | 2 | Administrador |

### Matriz de Permisos

| Endpoint | Public | Member | Admin |
|----------|--------|--------|-------|
| GET /events | ✅ | ✅ | ✅ |
| POST /events/{id}/registrations | ✅ | ✅ | ✅ |
| GET /users/me | ❌ | ✅ | ✅ |
| POST /donations | ❌ | ✅ | ✅ |
| POST /documents | ❌ | ✅ | ✅ |
| POST /events | ❌ | ❌ | ✅ |
| GET /donations | ❌ | ❌ | ✅ |
| GET /documents | ❌ | ❌ | ✅ |
| GET /reports/* | ❌ | ❌ | ✅ |
| */users/{id} | ❌ | ❌ | ✅ |

## CORS (Cross-Origin Resource Sharing)

### Configuración

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### Headers de Seguridad (Nginx)

```nginx
add_header X-Frame-Options "SAMEORIGIN" always;
add_header X-Content-Type-Options "nosniff" always;
add_header X-XSS-Protection "1; mode=block" always;
add_header Referrer-Policy "strict-origin-when-cross-origin" always;
```

## Validación de Archivos

### Tipos MIME Permitidos

```python
ALLOWED_MIMES = {
    "application/pdf",
    "image/png",
    "image/jpeg",
    "image/jpg",
}
```

### Límites

| Parámetro | Valor |
|-----------|-------|
| Tamaño máximo | 10 MB |
| Extensiones | .pdf, .png, .jpg, .jpeg |

### Proceso de Validación

1. Verificar Content-Type del header
2. Verificar extensión del nombre de archivo
3. Verificar tamaño
4. Generar checksum SHA-256
5. Almacenar con nombre único

```python
def validate_file(file: UploadFile) -> bool:
    # 1. MIME type
    if file.content_type not in ALLOWED_MIMES:
        raise HTTPException(400, "Tipo de archivo no permitido")
    
    # 2. Extensión
    ext = Path(file.filename).suffix.lower()
    if ext not in [".pdf", ".png", ".jpg", ".jpeg"]:
        raise HTTPException(400, "Extensión no permitida")
    
    # 3. Tamaño
    if file.size > MAX_UPLOAD_MB * 1024 * 1024:
        raise HTTPException(400, "Archivo muy grande")
    
    return True
```

## Almacenamiento Seguro

### Estructura de Directorios

```
storage/
├── 2024/
│   ├── 01/
│   │   ├── a1b2c3d4_documento.pdf
│   │   └── e5f6g7h8_imagen.jpg
│   └── 02/
```

### Nombres de Archivo

- Prefijo único generado con checksum parcial
- Nombre original sanitizado
- Evita path traversal

```python
def safe_filename(filename: str) -> str:
    # Remover caracteres peligrosos
    safe = re.sub(r'[^\w\-.]', '', filename)
    # Agregar prefijo único
    prefix = hashlib.sha256(os.urandom(16)).hexdigest()[:8]
    return f"{prefix}_{safe}"
```

## Variables de Entorno Sensibles

### Nunca commitear

```gitignore
.env
.env.local
.env.production
```

### Variables requeridas

| Variable | Descripción | Ejemplo |
|----------|-------------|---------|
| SECRET_KEY | Clave para JWT | `openssl rand -hex 32` |
| POSTGRES_PASSWORD | Contraseña DB | Generada |
| DATABASE_URL | Connection string | Con password |

### Generación de SECRET_KEY

```bash
# Python
python -c "import secrets; print(secrets.token_urlsafe(32))"

# OpenSSL
openssl rand -hex 32
```

## WebSocket Security

### Autenticación

```javascript
const ws = new WebSocket(`ws://host/api/ws/notifications?token=${jwt}`);
```

### Validación en Backend

```python
@router.websocket("/notifications")
async def websocket_endpoint(websocket: WebSocket, token: str = Query(...)):
    try:
        payload = decode_token(token)
        if payload.get("scope") != "access":
            await websocket.close(code=4001)
            return
        # ... continuar
    except:
        await websocket.close(code=4001)
```

## Recomendaciones de Producción

### 1. HTTPS Obligatorio

```nginx
server {
    listen 80;
    return 301 https://$host$request_uri;
}
```

### 2. Rate Limiting

```nginx
limit_req_zone $binary_remote_addr zone=api:10m rate=10r/s;

location /api {
    limit_req zone=api burst=20 nodelay;
}
```

### 3. Logs de Auditoría

```python
@app.middleware("http")
async def audit_log(request: Request, call_next):
    response = await call_next(request)
    logger.info(f"{request.method} {request.url} - {response.status_code}")
    return response
```

### 4. Rotación de Tokens

- Access tokens: 30 minutos
- Refresh tokens: 30 días
- Invalidar refresh token al hacer logout

### 5. Prevención de Inyección SQL

- Usar siempre ORM (SQLAlchemy)
- Evitar queries raw
- Parameterizar cuando sea necesario

```python
# ✅ Correcto
session.execute(select(User).where(User.email == email))

# ❌ Incorrecto
session.execute(f"SELECT * FROM users WHERE email = '{email}'")
```

## Checklist de Seguridad

### Desarrollo

- [ ] SECRET_KEY única y segura
- [ ] Contraseñas hasheadas con bcrypt
- [ ] Validación de entrada en todos los endpoints
- [ ] CORS configurado correctamente
- [ ] Tests de autenticación pasan

### Producción

- [ ] HTTPS habilitado
- [ ] Headers de seguridad configurados
- [ ] Rate limiting activo
- [ ] Logs de auditoría habilitados
- [ ] Backups encriptados
- [ ] Secrets en variables de entorno (no en código)

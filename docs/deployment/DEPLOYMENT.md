# Guía de Despliegue

## Arquitectura de Contenedores

```
┌─────────────────────────────────────────────────────────────────┐
│                      docker-compose.yml                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐         │
│  │  frontend   │    │   backend   │    │     db      │         │
│  │   :3000     │───▶│    :6076    │───▶│    :5432    │         │
│  │   (nginx)   │    │  (uvicorn)  │    │ (postgres)  │         │
│  └─────────────┘    └─────────────┘    └─────────────┘         │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

## Requisitos

- Docker 20.10+
- Docker Compose 2.0+
- 2GB RAM mínimo
- 10GB espacio en disco

## Configuración Rápida

### 1. Configurar Variables de Entorno

Crear archivo `.env` en la raíz del proyecto:

```bash
# Base de datos
POSTGRES_USER=ekklesia
POSTGRES_PASSWORD=tu_password_seguro
POSTGRES_DB=ekklesia
DATABASE_URL=postgresql+asyncpg://ekklesia:tu_password_seguro@db:5432/ekklesia

# JWT (CAMBIAR EN PRODUCCIÓN)
SECRET_KEY=genera-una-clave-segura-de-256-bits
ACCESS_TOKEN_EXP_MINUTES=30
REFRESH_TOKEN_EXP_MINUTES=43200
JWT_ALGORITHM=HS256

# Aplicación
APP_NAME=Ekklesia Admin
ENVIRONMENT=production

# Almacenamiento
STORAGE_PATH=./storage
MAX_UPLOAD_MB=10
```

### 2. Levantar Servicios

```bash
# Construir y levantar en segundo plano
docker-compose up -d --build

# Verificar estado
docker-compose ps

# Ver logs
docker-compose logs -f
```

### 3. Verificar Despliegue

```bash
# Test frontend
curl http://localhost:3000

# Test backend health
curl http://localhost:6076/api/health

# Test base de datos
docker exec ekklesia_db pg_isready -U ekklesia
```

## Puertos y URLs

| Servicio | Puerto Host | Puerto Contenedor | URL |
|----------|-------------|-------------------|-----|
| Frontend | 3000 | 80 | http://localhost:3000 |
| Backend | 6076 | 6076 | http://localhost:6076/api |
| API Docs | 6076 | 6076 | http://localhost:6076/docs |
| PostgreSQL | 55432 | 5432 | postgresql://localhost:55432 |

## Volúmenes y Persistencia

```yaml
volumes:
  pgdata:     # Datos de PostgreSQL
    driver: local
  
# Montajes bind
- ./storage:/code/storage   # Documentos subidos
- ./app:/code/app           # Código backend (solo dev)
```

## Comandos Útiles

### Gestión de Contenedores

```bash
# Detener todo
docker-compose down

# Detener y eliminar volúmenes (¡CUIDADO! Borra datos)
docker-compose down -v

# Reiniciar un servicio
docker-compose restart backend

# Ver logs de un servicio
docker-compose logs -f backend

# Ejecutar comando en contenedor
docker exec -it ekklesia_backend bash
```

### Base de Datos

```bash
# Conectar a PostgreSQL
docker exec -it ekklesia_db psql -U ekklesia -d ekklesia

# Backup de base de datos
docker exec ekklesia_db pg_dump -U ekklesia ekklesia > backup_$(date +%Y%m%d).sql

# Restaurar backup
cat backup.sql | docker exec -i ekklesia_db psql -U ekklesia -d ekklesia

# Aplicar schema inicial
docker exec ekklesia_db psql -U ekklesia -d ekklesia -f /docker-entrypoint-initdb.d/initial_schema.sql
```

### Pruebas

```bash
# Ejecutar pruebas en contenedor
docker exec -it ekklesia_backend pytest -v

# Ejecutar pruebas de integración
pytest tests/test_integration_endpoints.py -v
```

## Despliegue en Producción

### 1. Reverse Proxy (Nginx)

Configuración recomendada para producción con HTTPS:

```nginx
# /etc/nginx/sites-available/ekklesia
server {
    listen 80;
    server_name tu-dominio.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name tu-dominio.com;
    
    ssl_certificate /etc/letsencrypt/live/tu-dominio.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/tu-dominio.com/privkey.pem;
    
    # Frontend
    location / {
        proxy_pass http://localhost:3000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
    
    # Backend API
    location /api {
        proxy_pass http://localhost:6076;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
    
    # WebSocket
    location /api/ws {
        proxy_pass http://localhost:6076;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
```

### 2. Variables de Producción

```bash
# Generar SECRET_KEY seguro
python -c "import secrets; print(secrets.token_urlsafe(32))"

# Actualizar .env
SECRET_KEY=tu-clave-generada-super-segura
ENVIRONMENT=production
```

### 3. Deshabilitar Debug

En `docker-compose.yml` para producción:

```yaml
backend:
  command: uvicorn app.main:app --host 0.0.0.0 --port 6076 --workers 4
  # Quitar --reload
```

## Backups

### Script de Backup Automático

```bash
#!/bin/bash
# backup.sh
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR=/backups/ekklesia

# Backup PostgreSQL
docker exec ekklesia_db pg_dump -U ekklesia ekklesia | gzip > $BACKUP_DIR/db_$DATE.sql.gz

# Backup storage
tar -czf $BACKUP_DIR/storage_$DATE.tar.gz ./storage

# Mantener últimos 30 días
find $BACKUP_DIR -mtime +30 -delete
```

### Cron Job

```bash
# Backup diario a las 2 AM
0 2 * * * /path/to/backup.sh >> /var/log/ekklesia_backup.log 2>&1
```

## Monitoreo

### Health Checks

```bash
# Script de monitoreo
#!/bin/bash
curl -sf http://localhost:6076/api/health > /dev/null || \
    echo "Backend DOWN" | mail -s "Alerta Ekklesia" admin@iglesia.com

curl -sf http://localhost:3000 > /dev/null || \
    echo "Frontend DOWN" | mail -s "Alerta Ekklesia" admin@iglesia.com
```

### Docker Health Status

```bash
docker inspect --format='{{.State.Health.Status}}' ekklesia_backend
docker inspect --format='{{.State.Health.Status}}' ekklesia_db
```

## Troubleshooting

### El backend no inicia

```bash
# Ver logs detallados
docker-compose logs backend

# Verificar conexión a DB
docker exec ekklesia_backend python -c "from app.db.session import engine; print('OK')"
```

### Error de conexión a base de datos

```bash
# Verificar que DB está sana
docker exec ekklesia_db pg_isready

# Verificar credenciales en .env
grep DATABASE_URL .env
```

### Frontend no carga

```bash
# Verificar nginx
docker exec ekklesia_frontend nginx -t

# Ver logs nginx
docker-compose logs frontend
```

## CI/CD

Ver `.github/workflows/ci.yml` para configuración de:
- Tests automatizados
- Build de imágenes Docker
- Deploy automático (opcional)

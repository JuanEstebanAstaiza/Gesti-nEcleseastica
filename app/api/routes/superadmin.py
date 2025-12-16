"""
Rutas del Super Administrador - Gestión de la plataforma
"""
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from fastapi.responses import FileResponse
from sqlalchemy import select, text, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.schemas.tenant import (
    TenantCreate, TenantRead, TenantUpdate,
    TenantAdminCreate, TenantAdminRead,
    SuperAdminLogin, SuperAdminRead,
    SubscriptionPlanRead, PlatformStats
)
from app.api.schemas.auth import TokenPair
from app.core.security import verify_password, get_password_hash, create_access_token, create_refresh_token
from app.core.tenant import get_tenant_engine, get_tenant_db_url

router = APIRouter(prefix="/superadmin", tags=["superadmin"])


# ============== Dependencias ==============

async def get_master_session():
    """Obtiene sesión de la base de datos master"""
    from sqlalchemy.ext.asyncio import async_sessionmaker
    engine = await get_tenant_engine("ekklesia_master")
    session_factory = async_sessionmaker(engine, expire_on_commit=False)
    session = session_factory()
    try:
        yield session
    finally:
        await session.close()


async def get_current_superadmin(
    # Aquí iría la validación del token de super admin
    # Por ahora simplificado
):
    """Valida el token de super admin"""
    # TODO: Implementar validación real con JWT
    return {"id": 1, "email": "super@ekklesia.com"}


# ============== Autenticación ==============

@router.post("/auth/login", response_model=TokenPair)
async def superadmin_login(
    data: SuperAdminLogin,
    session: AsyncSession = Depends(get_master_session)
):
    """Login de super administrador"""
    result = await session.execute(
        text("SELECT id, email, hashed_password, full_name, is_active FROM super_admins WHERE email = :email"),
        {"email": data.email}
    )
    admin = result.fetchone()
    
    if not admin or not verify_password(data.password, admin.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales inválidas"
        )
    
    if not admin.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cuenta desactivada"
        )
    
    access_token = create_access_token(subject=str(admin.id), extra={"type": "superadmin"})
    refresh_token = create_refresh_token(subject=str(admin.id), extra={"type": "superadmin"})
    
    return TokenPair(access_token=access_token, refresh_token=refresh_token)


@router.get("/me", response_model=SuperAdminRead)
async def get_superadmin_profile(
    session: AsyncSession = Depends(get_master_session),
    current_admin = Depends(get_current_superadmin)
):
    """Obtiene perfil del super admin actual"""
    result = await session.execute(
        text("SELECT id, email, full_name, is_active, created_at FROM super_admins WHERE id = :id"),
        {"id": current_admin["id"]}
    )
    admin = result.fetchone()
    if not admin:
        raise HTTPException(status_code=404, detail="Admin no encontrado")
    
    return SuperAdminRead(
        id=admin.id,
        email=admin.email,
        full_name=admin.full_name,
        is_active=admin.is_active,
        created_at=admin.created_at
    )


# ============== Gestión de Tenants ==============

@router.get("/tenants", response_model=list[TenantRead])
async def list_tenants(
    session: AsyncSession = Depends(get_master_session),
    current_admin = Depends(get_current_superadmin)
):
    """Lista todos los tenants/iglesias"""
    result = await session.execute(
        text("""
            SELECT id, slug, name, subdomain, custom_domain, db_name, 
                   is_active, plan_id, created_at, expires_at 
            FROM tenants ORDER BY created_at DESC
        """)
    )
    tenants = result.fetchall()
    return [TenantRead(
        id=t.id,
        slug=t.slug,
        name=t.name,
        subdomain=t.subdomain,
        custom_domain=t.custom_domain,
        db_name=t.db_name,
        is_active=t.is_active,
        plan_id=t.plan_id,
        created_at=t.created_at,
        expires_at=t.expires_at
    ) for t in tenants]


@router.post("/tenants", response_model=TenantRead, status_code=status.HTTP_201_CREATED)
async def create_tenant(
    data: TenantCreate,
    session: AsyncSession = Depends(get_master_session),
    current_admin = Depends(get_current_superadmin)
):
    """
    Crea un nuevo tenant (iglesia).
    - Registra en la base master
    - Crea la base de datos del tenant
    - Aplica el esquema inicial
    """
    import re
    from sqlalchemy import text as sql_text
    
    # Validar slug
    if not re.match(r'^[a-z0-9-]+$', data.slug):
        raise HTTPException(
            status_code=400,
            detail="El slug solo puede contener letras minúsculas, números y guiones"
        )
    
    # Verificar que no exista
    existing = await session.execute(
        text("SELECT id FROM tenants WHERE slug = :slug"),
        {"slug": data.slug}
    )
    if existing.fetchone():
        raise HTTPException(status_code=409, detail="Ya existe un tenant con ese slug")
    
    db_name = f"ekk_{data.slug.replace('-', '_')}"
    
    # Crear registro del tenant
    result = await session.execute(
        text("""
            INSERT INTO tenants (slug, name, subdomain, custom_domain, db_name, plan_id)
            VALUES (:slug, :name, :subdomain, :custom_domain, :db_name, :plan_id)
            RETURNING id, slug, name, subdomain, custom_domain, db_name, is_active, plan_id, created_at, expires_at
        """),
        {
            "slug": data.slug,
            "name": data.name,
            "subdomain": data.subdomain or data.slug,
            "custom_domain": data.custom_domain,
            "db_name": db_name,
            "plan_id": data.plan_id
        }
    )
    tenant = result.fetchone()
    await session.commit()
    
    # Crear la base de datos para el tenant
    try:
        # Conexión al servidor PostgreSQL (no a una DB específica)
        from sqlalchemy import create_engine
        from app.core.config import settings
        
        # Usar conexión síncrona para crear DB
        base_url = str(settings.database_url).replace("+asyncpg", "").replace("ekklesia", "postgres")
        sync_engine = create_engine(base_url, isolation_level="AUTOCOMMIT")
        
        with sync_engine.connect() as conn:
            conn.execute(sql_text(f"CREATE DATABASE {db_name}"))
        
        sync_engine.dispose()
        
        # Aplicar schema al nuevo tenant
        tenant_url = get_tenant_db_url(db_name).replace("+asyncpg", "")
        tenant_engine = create_engine(tenant_url)
        
        # Leer y ejecutar el schema SQL
        import os
        schema_path = os.path.join(os.path.dirname(__file__), "../../db/sql/tenant_schema.sql")
        with open(schema_path) as f:
            schema_sql = f.read()
        
        with tenant_engine.connect() as conn:
            # Ejecutar cada statement por separado
            for statement in schema_sql.split(";"):
                statement = statement.strip()
                if statement:
                    try:
                        conn.execute(sql_text(statement))
                    except Exception:
                        pass  # Ignorar errores de objetos existentes
            conn.commit()
        
        tenant_engine.dispose()
        
    except Exception as e:
        # Si falla la creación de DB, eliminar el registro
        await session.execute(
            text("DELETE FROM tenants WHERE id = :id"),
            {"id": tenant.id}
        )
        await session.commit()
        raise HTTPException(
            status_code=500,
            detail=f"Error al crear la base de datos: {str(e)}"
        )
    
    return TenantRead(
        id=tenant.id,
        slug=tenant.slug,
        name=tenant.name,
        subdomain=tenant.subdomain,
        custom_domain=tenant.custom_domain,
        db_name=tenant.db_name,
        is_active=tenant.is_active,
        plan_id=tenant.plan_id,
        created_at=tenant.created_at,
        expires_at=tenant.expires_at
    )


@router.get("/tenants/{tenant_id}", response_model=TenantRead)
async def get_tenant(
    tenant_id: str,
    session: AsyncSession = Depends(get_master_session),
    current_admin = Depends(get_current_superadmin)
):
    """Obtiene un tenant por ID"""
    result = await session.execute(
        text("""
            SELECT id, slug, name, subdomain, custom_domain, db_name, 
                   is_active, plan_id, created_at, expires_at 
            FROM tenants WHERE id = :id
        """),
        {"id": tenant_id}
    )
    tenant = result.fetchone()
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant no encontrado")
    
    return TenantRead(
        id=tenant.id,
        slug=tenant.slug,
        name=tenant.name,
        subdomain=tenant.subdomain,
        custom_domain=tenant.custom_domain,
        db_name=tenant.db_name,
        is_active=tenant.is_active,
        plan_id=tenant.plan_id,
        created_at=tenant.created_at,
        expires_at=tenant.expires_at
    )


@router.patch("/tenants/{tenant_id}", response_model=TenantRead)
async def update_tenant(
    tenant_id: str,
    data: TenantUpdate,
    session: AsyncSession = Depends(get_master_session),
    current_admin = Depends(get_current_superadmin)
):
    """Actualiza un tenant"""
    # Construir query dinámico
    updates = []
    params = {"id": tenant_id}
    
    if data.name is not None:
        updates.append("name = :name")
        params["name"] = data.name
    if data.subdomain is not None:
        updates.append("subdomain = :subdomain")
        params["subdomain"] = data.subdomain
    if data.custom_domain is not None:
        updates.append("custom_domain = :custom_domain")
        params["custom_domain"] = data.custom_domain
    if data.is_active is not None:
        updates.append("is_active = :is_active")
        params["is_active"] = data.is_active
    if data.plan_id is not None:
        updates.append("plan_id = :plan_id")
        params["plan_id"] = data.plan_id
    
    if not updates:
        raise HTTPException(status_code=400, detail="No hay campos para actualizar")
    
    result = await session.execute(
        text(f"""
            UPDATE tenants SET {', '.join(updates)}
            WHERE id = :id
            RETURNING id, slug, name, subdomain, custom_domain, db_name, 
                      is_active, plan_id, created_at, expires_at
        """),
        params
    )
    tenant = result.fetchone()
    await session.commit()
    
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant no encontrado")
    
    return TenantRead(
        id=tenant.id,
        slug=tenant.slug,
        name=tenant.name,
        subdomain=tenant.subdomain,
        custom_domain=tenant.custom_domain,
        db_name=tenant.db_name,
        is_active=tenant.is_active,
        plan_id=tenant.plan_id,
        created_at=tenant.created_at,
        expires_at=tenant.expires_at
    )


@router.post("/tenants/{tenant_id}/admins", response_model=TenantAdminRead, status_code=status.HTTP_201_CREATED)
async def create_tenant_admin(
    tenant_id: str,
    data: TenantAdminCreate,
    session: AsyncSession = Depends(get_master_session),
    current_admin = Depends(get_current_superadmin)
):
    """Crea un administrador para un tenant específico"""
    # Verificar que el tenant existe
    result = await session.execute(
        text("SELECT db_name FROM tenants WHERE id = :id"),
        {"id": tenant_id}
    )
    tenant = result.fetchone()
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant no encontrado")
    
    # Crear usuario admin en la base del tenant
    from sqlalchemy import create_engine
    from sqlalchemy import text as sql_text
    
    tenant_url = get_tenant_db_url(tenant.db_name).replace("+asyncpg", "")
    tenant_engine = create_engine(tenant_url)
    
    hashed_password = get_password_hash(data.password)
    
    with tenant_engine.connect() as conn:
        conn.execute(
            sql_text("""
                INSERT INTO users (email, hashed_password, full_name, role)
                VALUES (:email, :password, :name, 'admin')
            """),
            {"email": data.email, "password": hashed_password, "name": data.full_name}
        )
        conn.commit()
    
    tenant_engine.dispose()
    
    # Registrar referencia en master
    result = await session.execute(
        text("""
            INSERT INTO tenant_admins (tenant_id, email)
            VALUES (:tenant_id, :email)
            RETURNING id, tenant_id, email, created_at
        """),
        {"tenant_id": tenant_id, "email": data.email}
    )
    admin = result.fetchone()
    await session.commit()
    
    return TenantAdminRead(
        id=admin.id,
        tenant_id=admin.tenant_id,
        email=admin.email,
        created_at=admin.created_at
    )


# ============== Planes de Suscripción ==============

@router.get("/plans", response_model=list[SubscriptionPlanRead])
async def list_plans(
    session: AsyncSession = Depends(get_master_session),
    current_admin = Depends(get_current_superadmin)
):
    """Lista todos los planes de suscripción"""
    result = await session.execute(
        text("""
            SELECT id, name, description, max_users, max_storage_mb, 
                   features, price_monthly, is_active 
            FROM subscription_plans ORDER BY price_monthly
        """)
    )
    plans = result.fetchall()
    return [SubscriptionPlanRead(
        id=p.id,
        name=p.name,
        description=p.description,
        max_users=p.max_users,
        max_storage_mb=p.max_storage_mb,
        features=p.features,
        price_monthly=float(p.price_monthly) if p.price_monthly else None,
        is_active=p.is_active
    ) for p in plans]


# ============== Estadísticas ==============

@router.get("/stats", response_model=PlatformStats)
async def get_platform_stats(
    session: AsyncSession = Depends(get_master_session),
    current_admin = Depends(get_current_superadmin)
):
    """Obtiene estadísticas generales de la plataforma"""
    # Total de tenants
    result = await session.execute(text("SELECT COUNT(*) FROM tenants"))
    total_tenants = result.scalar()
    
    # Tenants activos
    result = await session.execute(text("SELECT COUNT(*) FROM tenants WHERE is_active = TRUE"))
    active_tenants = result.scalar()
    
    # TODO: Agregar queries agregadas a cada tenant para usuarios y donaciones
    
    return PlatformStats(
        total_tenants=total_tenants,
        active_tenants=active_tenants,
        total_users=0,  # Calcular sumando de todos los tenants
        total_donations_amount=0.0
    )


# ============== Gestión de Backups ==============

@router.get("/backups")
async def list_backups(
    session: AsyncSession = Depends(get_master_session),
    current_admin = Depends(get_current_superadmin)
):
    """Lista los backups disponibles"""
    import os
    from pathlib import Path
    
    backup_dir = Path("./backups")
    backup_dir.mkdir(exist_ok=True)
    
    backups = []
    if backup_dir.exists():
        for f in backup_dir.glob("*.sql*"):
            stat = f.stat()
            backups.append({
                "filename": f.name,
                "size_mb": round(stat.st_size / (1024**2), 2),
                "created_at": stat.st_mtime,
                "path": str(f)
            })
    
    return {
        "backups": sorted(backups, key=lambda x: x["created_at"], reverse=True),
        "backup_directory": str(backup_dir.absolute())
    }


@router.post("/backups/{tenant_id}")
async def create_backup(
    tenant_id: str,
    session: AsyncSession = Depends(get_master_session),
    current_admin = Depends(get_current_superadmin)
):
    """Crea un backup de la base de datos de un tenant"""
    import subprocess
    from datetime import datetime
    from pathlib import Path
    from app.core.config import settings
    
    # Obtener info del tenant
    result = await session.execute(
        text("SELECT db_name, slug FROM tenants WHERE id = :id"),
        {"id": tenant_id}
    )
    tenant = result.fetchone()
    
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant no encontrado")
    
    backup_dir = Path("./backups")
    backup_dir.mkdir(exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_file = backup_dir / f"{tenant.slug}_{timestamp}.sql"
    
    try:
        # Comando pg_dump - Host "db" es el nombre del servicio en docker-compose
        cmd = [
            "pg_dump",
            "-h", "db",
            "-p", "5432",
            "-U", "ekklesia",
            "-d", tenant.db_name,
            "-f", str(backup_file),
        ]
        
        env = {"PGPASSWORD": "ekklesia"}
        
        result = subprocess.run(cmd, capture_output=True, text=True, env={**subprocess.os.environ, **env})
        
        if result.returncode != 0:
            raise HTTPException(
                status_code=500,
                detail=f"Error al crear backup: {result.stderr}"
            )
        
        stat = backup_file.stat()
        return {
            "message": "Backup creado exitosamente",
            "filename": backup_file.name,
            "size_mb": round(stat.st_size / (1024**2), 2),
            "path": str(backup_file)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al crear backup: {str(e)}")


@router.delete("/backups/{filename}")
async def delete_backup(
    filename: str,
    current_admin = Depends(get_current_superadmin)
):
    """Elimina un archivo de backup"""
    from pathlib import Path
    import re
    
    # Validar nombre de archivo (prevenir path traversal)
    if not re.match(r'^[\w\-\.]+\.sql(\.gz)?$', filename):
        raise HTTPException(status_code=400, detail="Nombre de archivo inválido")
    
    backup_path = Path("./backups") / filename
    
    if not backup_path.exists():
        raise HTTPException(status_code=404, detail="Backup no encontrado")
    
    backup_path.unlink()
    return {"message": f"Backup {filename} eliminado"}


@router.get("/backups/{filename}/download")
async def download_backup(
    filename: str,
    current_admin = Depends(get_current_superadmin)
):
    """Descarga un archivo de backup"""
    import re
    from pathlib import Path
    
    if not re.match(r'^[\w\-\.]+\.sql(\.gz)?$', filename):
        raise HTTPException(status_code=400, detail="Nombre de archivo inválido")
    
    backup_path = Path("./backups") / filename
    if not backup_path.exists():
        raise HTTPException(status_code=404, detail="Backup no encontrado")
    
    return FileResponse(backup_path, media_type="application/octet-stream", filename=filename)


@router.post("/backups/upload-file")
async def upload_backup(
    file: UploadFile = File(...),
    current_admin = Depends(get_current_superadmin)
):
    """Sube un archivo de backup a la carpeta local (no restaura)"""
    import re
    from pathlib import Path
    
    if not file.filename or not re.match(r'^[\w\-\.]+\.sql(\.gz)?$', file.filename):
        raise HTTPException(status_code=400, detail="Nombre de archivo inválido")
    
    backup_dir = Path("./backups")
    backup_dir.mkdir(exist_ok=True)
    dest = backup_dir / file.filename
    
    content = await file.read()
    dest.write_bytes(content)
    
    stat = dest.stat()
    return {
        "message": "Backup subido",
        "filename": dest.name,
        "size_mb": round(stat.st_size / (1024**2), 2)
    }


# ============== Métricas de Ingresos ==============

@router.get("/revenue")
async def get_revenue_metrics(
    session: AsyncSession = Depends(get_master_session),
    current_admin = Depends(get_current_superadmin)
):
    """Obtiene métricas de ingresos de la plataforma"""
    from decimal import Decimal
    
    # Obtener todos los tenants con sus planes
    result = await session.execute(
        text("""
            SELECT t.id, t.name, t.slug, t.plan_id, t.created_at,
                   p.name as plan_name, p.price_monthly
            FROM tenants t
            LEFT JOIN subscription_plans p ON t.plan_id = p.id
            WHERE t.is_active = TRUE
        """)
    )
    tenants = result.fetchall()
    
    total_mrr = Decimal("0")
    by_plan = {}
    
    for t in tenants:
        if t.price_monthly:
            total_mrr += t.price_monthly
            plan_name = t.plan_name or "Sin plan"
            if plan_name not in by_plan:
                by_plan[plan_name] = {"count": 0, "revenue": Decimal("0")}
            by_plan[plan_name]["count"] += 1
            by_plan[plan_name]["revenue"] += t.price_monthly
    
    return {
        "mrr": float(total_mrr),  # Monthly Recurring Revenue
        "arr": float(total_mrr * 12),  # Annual Recurring Revenue
        "active_subscriptions": len(tenants),
        "by_plan": {k: {"count": v["count"], "revenue": float(v["revenue"])} for k, v in by_plan.items()},
        "currency": "COP"
    }


# ============== Gestión de Planes ==============

@router.post("/plans", status_code=status.HTTP_201_CREATED)
async def create_plan(
    data: dict,
    session: AsyncSession = Depends(get_master_session),
    current_admin = Depends(get_current_superadmin)
):
    """Crea un nuevo plan de suscripción"""
    result = await session.execute(
        text("""
            INSERT INTO subscription_plans (name, description, max_users, max_storage_mb, features, price_monthly)
            VALUES (:name, :description, :max_users, :max_storage_mb, :features, :price_monthly)
            RETURNING id, name, description, max_users, max_storage_mb, features, price_monthly, is_active
        """),
        {
            "name": data.get("name"),
            "description": data.get("description"),
            "max_users": data.get("max_users", 10),
            "max_storage_mb": data.get("max_storage_mb", 1024),
            "features": data.get("features", "{}"),
            "price_monthly": data.get("price_monthly", 0)
        }
    )
    plan = result.fetchone()
    await session.commit()
    
    return {
        "id": plan.id,
        "name": plan.name,
        "description": plan.description,
        "max_users": plan.max_users,
        "max_storage_mb": plan.max_storage_mb,
        "features": plan.features,
        "price_monthly": float(plan.price_monthly) if plan.price_monthly else 0,
        "is_active": plan.is_active
    }


@router.patch("/plans/{plan_id}")
async def update_plan(
    plan_id: int,
    data: dict,
    session: AsyncSession = Depends(get_master_session),
    current_admin = Depends(get_current_superadmin)
):
    """Actualiza un plan de suscripción"""
    updates = []
    params = {"id": plan_id}
    
    for key in ["name", "description", "max_users", "max_storage_mb", "features", "price_monthly", "is_active"]:
        if key in data:
            updates.append(f"{key} = :{key}")
            params[key] = data[key]
    
    if not updates:
        raise HTTPException(status_code=400, detail="No hay campos para actualizar")
    
    result = await session.execute(
        text(f"""
            UPDATE subscription_plans SET {', '.join(updates)}
            WHERE id = :id
            RETURNING id, name, description, max_users, max_storage_mb, features, price_monthly, is_active
        """),
        params
    )
    plan = result.fetchone()
    await session.commit()
    
    if not plan:
        raise HTTPException(status_code=404, detail="Plan no encontrado")
    
    return {
        "id": plan.id,
        "name": plan.name,
        "description": plan.description,
        "max_users": plan.max_users,
        "max_storage_mb": plan.max_storage_mb,
        "features": plan.features,
        "price_monthly": float(plan.price_monthly) if plan.price_monthly else 0,
        "is_active": plan.is_active
    }


@router.delete("/plans/{plan_id}")
async def delete_plan(
    plan_id: int,
    session: AsyncSession = Depends(get_master_session),
    current_admin = Depends(get_current_superadmin)
):
    """Elimina un plan permanentemente"""
    # Verificar que no hay tenants usando este plan
    result = await session.execute(
        text("SELECT COUNT(*) FROM tenants WHERE plan_id = :id"),
        {"id": plan_id}
    )
    count = result.scalar()
    
    if count > 0:
        raise HTTPException(
            status_code=400, 
            detail=f"No se puede eliminar: {count} iglesia(s) están usando este plan"
        )
    
    result = await session.execute(
        text("DELETE FROM subscription_plans WHERE id = :id RETURNING id"),
        {"id": plan_id}
    )
    row = result.fetchone()
    await session.commit()
    
    if not row:
        raise HTTPException(status_code=404, detail="Plan no encontrado")
    
    return {"message": "Plan eliminado permanentemente", "id": plan_id}


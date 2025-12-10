"""
Middleware y utilidades para gestión de multi-tenancy
"""
from contextvars import ContextVar
from typing import Optional
from fastapi import Request, HTTPException
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

from app.core.config import settings

# Context variable para el tenant actual
current_tenant: ContextVar[Optional[dict]] = ContextVar("current_tenant", default=None)
current_db_session: ContextVar[Optional[AsyncSession]] = ContextVar("current_db_session", default=None)

# Cache de engines por tenant
_tenant_engines: dict[str, any] = {}


def get_tenant_db_url(db_name: str) -> str:
    """Construye la URL de conexión para un tenant específico"""
    base_url = str(settings.database_url)
    # Reemplazar el nombre de la base de datos
    parts = base_url.rsplit("/", 1)
    return f"{parts[0]}/{db_name}"


def get_master_db_url() -> str:
    """URL de la base de datos master"""
    return str(settings.master_database_url)


async def get_tenant_engine(db_name: str):
    """Obtiene o crea un engine para un tenant específico"""
    if db_name not in _tenant_engines:
        db_url = get_tenant_db_url(db_name)
        engine = create_async_engine(db_url, future=True, echo=False, pool_pre_ping=True)
        _tenant_engines[db_name] = engine
    return _tenant_engines[db_name]


async def get_tenant_session(db_name: str) -> AsyncSession:
    """Crea una sesión para un tenant específico"""
    engine = await get_tenant_engine(db_name)
    session_factory = async_sessionmaker(engine, expire_on_commit=False)
    return session_factory()


def extract_tenant_from_request(request: Request) -> Optional[str]:
    """
    Extrae el identificador del tenant de la request.
    Busca en:
    1. Header X-Tenant-ID
    2. Subdominio del host
    3. Query parameter ?tenant=
    """
    # 1. Header personalizado
    tenant_header = request.headers.get("X-Tenant-ID")
    if tenant_header:
        return tenant_header
    
    # 2. Subdominio
    host = request.headers.get("host", "")
    if host:
        parts = host.split(".")
        # Si tiene subdominio (ej: iglesia-ejemplo.ekklesia.app)
        if len(parts) >= 3 and parts[0] not in ["www", "api", "admin"]:
            return parts[0]
    
    # 3. Query parameter (útil para desarrollo)
    tenant_param = request.query_params.get("tenant")
    if tenant_param:
        return tenant_param
    
    return None


class TenantMiddleware:
    """
    Middleware que resuelve el tenant y establece la conexión a su BD.
    """
    
    # Rutas que no requieren tenant (super admin, health, etc.)
    EXCLUDED_PATHS = [
        "/api/health",
        "/api/superadmin",
        "/docs",
        "/redoc",
        "/openapi.json",
    ]
    
    def __init__(self, app):
        self.app = app
    
    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
        
        request = Request(scope, receive)
        path = request.url.path
        
        # Verificar si la ruta está excluida
        for excluded in self.EXCLUDED_PATHS:
            if path.startswith(excluded):
                await self.app(scope, receive, send)
                return
        
        # Extraer tenant
        tenant_slug = extract_tenant_from_request(request)
        
        if tenant_slug:
            # Buscar tenant en master DB y establecer contexto
            try:
                tenant_info = await self._resolve_tenant(tenant_slug)
                if tenant_info:
                    current_tenant.set(tenant_info)
                    scope["state"]["tenant"] = tenant_info
            except Exception as e:
                # Log error pero continuar (puede ser ruta pública)
                pass
        
        await self.app(scope, receive, send)
    
    async def _resolve_tenant(self, slug: str) -> Optional[dict]:
        """Busca el tenant en la base de datos master"""
        from sqlalchemy import select, text
        
        try:
            engine = await get_tenant_engine("ekklesia_master")
            async with engine.connect() as conn:
                result = await conn.execute(
                    text("SELECT id, slug, name, db_name, is_active FROM tenants WHERE slug = :slug"),
                    {"slug": slug}
                )
                row = result.fetchone()
                if row and row.is_active:
                    return {
                        "id": str(row.id),
                        "slug": row.slug,
                        "name": row.name,
                        "db_name": row.db_name,
                    }
        except Exception:
            pass
        return None


def get_current_tenant() -> Optional[dict]:
    """Obtiene el tenant actual del contexto"""
    return current_tenant.get()


def require_tenant():
    """Dependencia que requiere un tenant válido"""
    tenant = get_current_tenant()
    if not tenant:
        raise HTTPException(
            status_code=400,
            detail="Tenant no especificado. Use el header X-Tenant-ID o acceda via subdominio."
        )
    return tenant


async def get_tenant_db():
    """
    Dependencia de FastAPI para obtener sesión de BD del tenant actual.
    """
    tenant = get_current_tenant()
    if not tenant:
        raise HTTPException(
            status_code=400,
            detail="Tenant no especificado"
        )
    
    session = await get_tenant_session(tenant["db_name"])
    try:
        yield session
    finally:
        await session.close()


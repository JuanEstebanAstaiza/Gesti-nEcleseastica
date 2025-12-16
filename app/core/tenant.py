"""
Utilidades de base de datos - Sistema de una sola iglesia
"""
from typing import Optional
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

from app.core.config import settings

# Cache de engines
_engines: dict[str, any] = {}

# Base de datos principal de la iglesia
CHURCH_DB = "ekklesia"
MASTER_DB = "ekklesia_master"


def get_db_url(db_name: str) -> str:
    """Construye la URL de conexión para una base de datos"""
    # Para la base de datos master usamos el host db_master
    if db_name == MASTER_DB:
        return f"postgresql+asyncpg://ekklesia:ekklesia@db_master:5432/{db_name}"
    
    # Para las demás, usamos el host db
    base_url = str(settings.database_url)
    parts = base_url.rsplit("/", 1)
    return f"{parts[0]}/{db_name}"


async def get_engine(db_name: str):
    """Obtiene o crea un engine para una base de datos"""
    if db_name not in _engines:
        db_url = get_db_url(db_name)
        engine = create_async_engine(db_url, future=True, echo=False, pool_pre_ping=True)
        _engines[db_name] = engine
    return _engines[db_name]


async def get_session(db_name: str) -> AsyncSession:
    """Crea una sesión para una base de datos"""
    engine = await get_engine(db_name)
    session_factory = async_sessionmaker(engine, expire_on_commit=False)
    return session_factory()


# Aliases para compatibilidad
get_tenant_db_url = get_db_url
get_tenant_engine = get_engine
get_tenant_session = get_session


async def get_tenant_db():
    """
    Dependencia de FastAPI para obtener sesión de BD de la iglesia.
    Siempre usa la base de datos principal 'ekklesia'.
    """
    session = await get_session(CHURCH_DB)
    try:
        yield session
    finally:
        await session.close()


def require_tenant():
    """Dependencia dummy para compatibilidad - siempre retorna la iglesia principal"""
    return {
        "id": "1",
        "slug": "mi-iglesia",
        "name": "Mi Iglesia",
        "db_name": CHURCH_DB,
    }


def get_current_tenant() -> Optional[dict]:
    """Retorna info de la iglesia principal"""
    return require_tenant()


from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.core.config import settings


engine = create_async_engine(str(settings.database_url), future=True, echo=False)
AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False)


async def get_session():
    """Dependencia de FastAPI para obtener una sesión async."""
    async with AsyncSessionLocal() as session:
        yield session


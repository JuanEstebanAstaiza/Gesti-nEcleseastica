from fastapi import FastAPI

from app.api.routes import router as api_router
from app.core.config import settings


def create_application() -> FastAPI:
    app = FastAPI(
        title=settings.app_name,
        version="0.1.0",
        description="Gestión administrativa eclesiástica - backend FastAPI",
    )
    app.include_router(api_router, prefix="/api")
    return app


app = create_application()


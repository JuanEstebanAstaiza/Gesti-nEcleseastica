from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import router as api_router
from app.core.config import settings
from app.core.tenant import TenantMiddleware


def create_application() -> FastAPI:
    app = FastAPI(
        title=settings.app_name,
        version="1.0.0",
        description="Ekklesia - Plataforma SaaS Multi-tenant para Gestión Eclesiástica",
        docs_url="/docs",
        redoc_url="/redoc",
    )

    # CORS configuration - permite cualquier subdominio de ekklesia
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[
            "http://localhost:3000",
            "http://127.0.0.1:3000",
            "http://localhost",
            "http://127.0.0.1",
        ],
        allow_origin_regex=r"https?://.*\.ekklesia\.app",  # Subdominios en producción
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
        expose_headers=["X-Tenant-ID"],
    )

    # Tenant middleware para multi-tenancy
    app.add_middleware(TenantMiddleware)

    app.include_router(api_router, prefix="/api")
    return app


app = create_application()


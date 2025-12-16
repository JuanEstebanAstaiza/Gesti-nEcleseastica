from fastapi import APIRouter

from app.api.routes import (
    health,
    auth,
    users,
    donations,
    documents,
    events,
    expenses,
    reports,
    registrations,
    ws,
    superadmin,
    public,
    church_admin,
)

router = APIRouter()

# Health check (sin tenant)
router.include_router(health.router, prefix="/health", tags=["health"])

# Super Admin routes (sin tenant)
router.include_router(superadmin.router)

# Public routes (requiere tenant)
router.include_router(public.router)

# Church admin routes (requiere tenant + admin)
router.include_router(church_admin.router)

# Tenant routes (requiere tenant)
router.include_router(auth.router)
router.include_router(users.router)
router.include_router(donations.router)
router.include_router(documents.router)
router.include_router(events.router)
router.include_router(expenses.router)
router.include_router(reports.router)
router.include_router(registrations.router)
router.include_router(ws.router)


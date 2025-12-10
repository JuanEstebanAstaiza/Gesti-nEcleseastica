from fastapi import APIRouter

from app.api.routes import (
    health,
    auth,
    users,
    donations,
    documents,
    events,
    reports,
    registrations,
    ws,
)

router = APIRouter()
router.include_router(health.router, prefix="/health", tags=["health"])
router.include_router(auth.router)
router.include_router(users.router)
router.include_router(donations.router)
router.include_router(documents.router)
router.include_router(events.router)
router.include_router(reports.router)
router.include_router(registrations.router)
router.include_router(ws.router)


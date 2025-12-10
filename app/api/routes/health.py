from fastapi import APIRouter

router = APIRouter()


@router.get("", summary="Healthcheck del servicio")
async def healthcheck():
    return {"status": "ok"}


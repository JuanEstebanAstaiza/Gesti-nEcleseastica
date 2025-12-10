from fastapi import APIRouter, Depends, Query

from app.api.schemas import RegistrationCreate, RegistrationRead
from app.api.services.registration import RegistrationService
from app.core.deps import require_admin
from app.db.session import get_session

router = APIRouter(prefix="/events/{event_id}/registrations", tags=["registrations"])


@router.post("", response_model=RegistrationRead, status_code=201)
async def create_registration(event_id: int, payload: RegistrationCreate, session=Depends(get_session)):
    service = RegistrationService(session)
    reg = await service.register(
        event_id=event_id,
        attendee_name=payload.attendee_name,
        attendee_email=payload.attendee_email,
        notes=payload.notes,
    )
    return reg


@router.get("", response_model=list[RegistrationRead], dependencies=[Depends(require_admin)])
async def list_registrations(
    event_id: int,
    session=Depends(get_session),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
):
    service = RegistrationService(session)
    return await service.repo.list_by_event(event_id, limit=limit, offset=offset)


@router.delete("/{registration_id}", status_code=204, dependencies=[Depends(require_admin)])
async def cancel_registration(event_id: int, registration_id: int, session=Depends(get_session)):
    service = RegistrationService(session)
    await service.cancel(event_id, registration_id)
    return None


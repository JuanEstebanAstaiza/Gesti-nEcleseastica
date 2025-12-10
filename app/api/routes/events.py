from fastapi import APIRouter, Depends, status

from app.api.schemas import EventCreate, EventRead
from app.api.services.event import EventService
from app.core.deps import get_current_user, require_admin
from app.db.session import get_session
from app.models.user import User
from app.api.routes.ws import manager

router = APIRouter(prefix="/events", tags=["events"])


@router.post("", response_model=EventRead, status_code=status.HTTP_201_CREATED, dependencies=[Depends(require_admin)])
async def create_event(payload: EventCreate, session=Depends(get_session), current_user: User = Depends(get_current_user)):
    service = EventService(session)
    event = await service.create_event(
        name=payload.name,
        description=payload.description,
        start_date=payload.start_date,
        end_date=payload.end_date,
        capacity=payload.capacity,
        created_by_id=current_user.id,
    )
    await manager.broadcast(
        {
            "type": "event.created",
            "event_id": event.id,
            "name": event.name,
            "capacity": event.capacity,
        }
    )
    return event


@router.get("", response_model=list[EventRead])
async def list_events(session=Depends(get_session)):
    service = EventService(session)
    return await service.list_events()


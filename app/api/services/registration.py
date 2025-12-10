from app.api.repositories.registration import RegistrationRepository
from app.api.repositories.event import EventRepository
from fastapi import HTTPException, status


class RegistrationService:
    def __init__(self, session):
        self.repo = RegistrationRepository(session)
        self.event_repo = EventRepository(session)

    async def register(self, **data):
        event_id = data["event_id"]
        event = await self.event_repo.get_by_id(event_id)
        if not event:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Evento no encontrado")

        if await self.repo.exists_by_email(event_id, data["attendee_email"]):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El asistente ya está registrado en este evento",
            )

        # Capacity check
        current_count = await self.repo.count_by_event(event_id)
        if event.capacity is not None and current_count >= event.capacity:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Capacidad del evento alcanzada",
            )

        return await self.repo.create(**data)

    async def list_by_event(self, event_id: int):
        return await self.repo.list_by_event(event_id)

    async def cancel(self, event_id: int, registration_id: int):
        success = await self.repo.cancel(registration_id, event_id)
        if not success:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Registro no encontrado")
        return True


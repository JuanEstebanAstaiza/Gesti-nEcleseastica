from sqlalchemy.ext.asyncio import AsyncSession

from app.api.repositories.event import EventRepository


class EventService:
    def __init__(self, session: AsyncSession):
        self.repo = EventRepository(session)

    async def create_event(self, **data):
        return await self.repo.create(**data)

    async def list_events(self):
        return await self.repo.list_all()


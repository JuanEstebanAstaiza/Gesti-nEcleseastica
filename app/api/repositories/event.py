from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.event import Event


class EventRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, **data) -> Event:
        event = Event(**data)
        self.session.add(event)
        await self.session.commit()
        await self.session.refresh(event)
        return event

    async def list_all(self) -> list[Event]:
        result = await self.session.execute(select(Event))
        return list(result.scalars().all())

    async def get_by_id(self, event_id: int) -> Event | None:
        result = await self.session.execute(select(Event).where(Event.id == event_id))
        return result.scalar_one_or_none()


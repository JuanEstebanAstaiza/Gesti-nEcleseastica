from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.registration import Registration


class RegistrationRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, **data) -> Registration:
        reg = Registration(**data)
        self.session.add(reg)
        await self.session.commit()
        await self.session.refresh(reg)
        return reg

    async def list_by_event(self, event_id: int, limit: int = 50, offset: int = 0) -> list[Registration]:
        stmt = (
            select(Registration)
            .where(Registration.event_id == event_id)
            .order_by(Registration.registered_at.desc())
            .limit(limit)
            .offset(offset)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def exists_by_email(self, event_id: int, attendee_email: str) -> bool:
        result = await self.session.execute(
            select(Registration.id).where(
                Registration.event_id == event_id,
                Registration.attendee_email == attendee_email,
            )
        )
        return result.scalar_one_or_none() is not None

    async def count_by_event(self, event_id: int) -> int:
        from sqlalchemy import func

        result = await self.session.execute(
            select(func.count()).where(Registration.event_id == event_id, Registration.is_cancelled.is_(False))
        )
        return result.scalar_one()

    async def cancel(self, registration_id: int, event_id: int) -> bool:
        reg = await self.session.get(Registration, registration_id)
        if not reg or reg.event_id != event_id:
            return False
        reg.is_cancelled = True
        await self.session.commit()
        return True


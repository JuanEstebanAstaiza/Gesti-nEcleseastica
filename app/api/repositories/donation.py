from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.donation import Donation


class DonationRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, *, user_id: int | None, **data) -> Donation:
        donation = Donation(user_id=user_id, **data)
        self.session.add(donation)
        await self.session.commit()
        await self.session.refresh(donation)
        return donation

    async def list_all(self) -> list[Donation]:
        result = await self.session.execute(select(Donation))
        return list(result.scalars().all())

    async def list_by_user(self, user_id: int) -> list[Donation]:
        result = await self.session.execute(select(Donation).where(Donation.user_id == user_id))
        return list(result.scalars().all())


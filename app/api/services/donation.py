from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.repositories.donation import DonationRepository


class DonationService:
    def __init__(self, session: AsyncSession):
        self.repo = DonationRepository(session)

    async def create_donation(self, *, user_id: int | None, data: dict):
        return await self.repo.create(user_id=user_id, **data)

    async def list_for_admin(self):
        return await self.repo.list_all()

    async def list_for_user(self, user_id: int):
        return await self.repo.list_by_user(user_id)


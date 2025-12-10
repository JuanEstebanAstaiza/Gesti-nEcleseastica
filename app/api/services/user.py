from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.repositories.user import UserRepository


class UserService:
    def __init__(self, session: AsyncSession):
        self.repo = UserRepository(session)

    async def list_users(self):
        return await self.repo.list_all()

    async def get_user(self, user_id: int):
        user = await self.repo.get_by_id(user_id)
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuario no encontrado")
        return user

    async def update_user(self, user_id: int, **fields):
        if fields.get("role") and fields["role"] not in {"public", "member", "admin"}:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Rol inválido")

        user = await self.repo.update_user(user_id, **fields)
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuario no encontrado")
        return user

    async def delete_user(self, user_id: int):
        deleted = await self.repo.delete_user(user_id)
        if not deleted:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuario no encontrado")
        return True


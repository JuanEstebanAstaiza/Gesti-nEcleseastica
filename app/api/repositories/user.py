from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import get_password_hash
from app.models.user import User


class UserRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_email(self, email: str) -> User | None:
        result = await self.session.execute(select(User).where(User.email == email))
        return result.scalar_one_or_none()

    async def get_by_id(self, user_id: int) -> User | None:
        result = await self.session.execute(select(User).where(User.id == user_id))
        return result.scalar_one_or_none()

    async def list_all(self) -> list[User]:
        result = await self.session.execute(select(User))
        return list(result.scalars().all())

    async def create_user(self, email: str, password: str, full_name: str | None, role: str = "member") -> User:
        hashed = get_password_hash(password)
        user = User(email=email, hashed_password=hashed, full_name=full_name, role=role)
        self.session.add(user)
        await self.session.commit()
        await self.session.refresh(user)
        return user

    async def update_user(
        self,
        user_id: int,
        *,
        full_name: str | None = None,
        role: str | None = None,
        password: str | None = None,
        is_active: bool | None = None,
    ) -> User | None:
        user = await self.get_by_id(user_id)
        if not user:
            return None
        if full_name is not None:
            user.full_name = full_name
        if role is not None:
            user.role = role
        if password is not None:
            user.hashed_password = get_password_hash(password)
        if is_active is not None:
            user.is_active = is_active

        await self.session.commit()
        await self.session.refresh(user)
        return user

    async def delete_user(self, user_id: int) -> bool:
        result = await self.session.execute(delete(User).where(User.id == user_id))
        await self.session.commit()
        return result.rowcount > 0


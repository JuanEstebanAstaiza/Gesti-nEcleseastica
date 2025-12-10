from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.repositories.user import UserRepository
from app.api.schemas import LoginRequest, UserCreate
from app.core.security import (
    create_access_token,
    create_refresh_token,
    verify_password,
)


class AuthService:
    def __init__(self, session: AsyncSession):
        self.repo = UserRepository(session)
        self.session = session

    async def register(self, data: UserCreate):
        if data.role not in {"public", "member", "admin"}:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Rol inválido",
            )
        existing = await self.repo.get_by_email(data.email)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El correo ya está registrado",
            )
        user = await self.repo.create_user(
            email=data.email, password=data.password, full_name=data.full_name, role=data.role
        )
        return user

    async def login(self, data: LoginRequest):
        user = await self.repo.get_by_email(data.email)
        if not user or not verify_password(data.password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Credenciales inválidas",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return self._issue_tokens(str(user.id))

    def refresh(self, refresh_token: str):
        return self._issue_tokens_from_refresh(refresh_token)

    def _issue_tokens(self, subject: str):
        access = create_access_token(subject)
        refresh = create_refresh_token(subject)
        return {"access_token": access, "refresh_token": refresh, "token_type": "bearer"}

    def _issue_tokens_from_refresh(self, token: str):
        from app.core.security import decode_token

        payload = decode_token(token)
        if payload.get("scope") != "refresh_token":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Refresh token inválido",
                headers={"WWW-Authenticate": "Bearer"},
            )
        subject = payload.get("sub")
        return self._issue_tokens(subject=subject)


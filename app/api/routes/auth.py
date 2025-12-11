from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.schemas import LoginRequest, TokenPair, RefreshRequest, UserCreate, UserRead
from app.api.services.auth import AuthService
from app.db.session import get_session
from app.core.deps import get_current_user
from app.models.user import User

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=UserRead, status_code=status.HTTP_201_CREATED)
async def register_user(data: UserCreate, session: AsyncSession = Depends(get_session)):
    service = AuthService(session)
    user = await service.register(data)
    return user


@router.post("/login", response_model=TokenPair)
async def login(data: LoginRequest, session: AsyncSession = Depends(get_session)):
    service = AuthService(session)
    tokens = await service.login(data)
    return tokens


@router.post("/refresh", response_model=TokenPair)
async def refresh_token(data: RefreshRequest, session: AsyncSession = Depends(get_session)):
    service = AuthService(session)
    tokens = service.refresh(data.refresh_token)
    return tokens


@router.get("/me", response_model=UserRead)
async def me(current_user: User = Depends(get_current_user)):
    return current_user


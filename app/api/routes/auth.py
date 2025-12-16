from fastapi import APIRouter, Depends, status, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

from app.api.schemas import LoginRequest, TokenPair, RefreshRequest, UserCreate, UserRead
from app.api.services.auth import AuthService
from app.core.security import decode_token
from app.db.session import get_session

router = APIRouter(prefix="/auth", tags=["auth"])
security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    session: AsyncSession = Depends(get_session)
) -> dict:
    """Obtiene el usuario actual desde el token JWT"""
    try:
        payload = decode_token(credentials.credentials)
        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(status_code=401, detail="Token inválido")
        
        result = await session.execute(
            text("SELECT id, email, full_name, role, phone, is_active, created_at FROM users WHERE id = :id"),
            {"id": int(user_id)}
        )
        user = result.fetchone()
        
        if not user:
            raise HTTPException(status_code=401, detail="Usuario no encontrado")
        
        if not user.is_active:
            raise HTTPException(status_code=403, detail="Cuenta desactivada")
        
        return {
            "id": user.id,
            "email": user.email,
            "full_name": user.full_name,
            "role": user.role,
            "phone": user.phone,
            "is_active": user.is_active,
            "created_at": user.created_at
        }
    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e))


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
async def get_profile(current_user: dict = Depends(get_current_user)):
    """Obtiene el perfil del usuario autenticado"""
    return UserRead(
        id=current_user["id"],
        email=current_user["email"],
        full_name=current_user["full_name"],
        role=current_user["role"],
        phone=current_user["phone"],
        is_active=current_user["is_active"],
        created_at=current_user["created_at"]
    )


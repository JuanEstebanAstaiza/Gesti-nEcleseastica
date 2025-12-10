from fastapi import APIRouter, Depends, status

from app.api.schemas import UserRead, UserUpdate
from app.api.services.user import UserService
from app.core.deps import get_current_user, require_admin
from app.db.session import get_session
from app.models.user import User

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me", response_model=UserRead)
async def read_me(current_user: User = Depends(get_current_user)):
    return current_user


@router.get("", response_model=list[UserRead], dependencies=[Depends(require_admin)])
async def list_users(session=Depends(get_session)):
    service = UserService(session)
    return await service.list_users()


@router.get("/{user_id}", response_model=UserRead, dependencies=[Depends(require_admin)])
async def get_user(user_id: int, session=Depends(get_session)):
    service = UserService(session)
    return await service.get_user(user_id)


@router.patch(
    "/{user_id}",
    response_model=UserRead,
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(require_admin)],
)
async def update_user(user_id: int, payload: UserUpdate, session=Depends(get_session)):
    service = UserService(session)
    return await service.update_user(
        user_id,
        full_name=payload.full_name,
        role=payload.role,
        password=payload.password,
        is_active=payload.is_active,
    )


@router.delete(
    "/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(require_admin)],
)
async def delete_user(user_id: int, session=Depends(get_session)):
    service = UserService(session)
    await service.delete_user(user_id)
    return None


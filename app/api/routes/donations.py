from fastapi import APIRouter, Depends, status

from app.api.schemas import DonationCreate, DonationRead
from app.api.services.donation import DonationService
from app.core.deps import get_current_user, require_admin
from app.db.session import get_session
from app.models.user import User
from app.api.routes.ws import manager

router = APIRouter(prefix="/donations", tags=["donations"])


@router.post("", response_model=DonationRead, status_code=status.HTTP_201_CREATED)
async def create_donation(
    payload: DonationCreate,
    session=Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    service = DonationService(session)
    donation = await service.create_donation(user_id=current_user.id, data=payload.model_dump())
    await manager.broadcast(
        {
            "type": "donation.created",
            "donation_id": donation.id,
            "amount": float(donation.amount),
            "donation_type": donation.donation_type,
        }
    )
    return donation


@router.get("", response_model=list[DonationRead], dependencies=[Depends(require_admin)])
async def list_donations(session=Depends(get_session)):
    service = DonationService(session)
    return await service.list_for_admin()


@router.get("/me", response_model=list[DonationRead])
async def list_my_donations(session=Depends(get_session), current_user: User = Depends(get_current_user)):
    service = DonationService(session)
    return await service.list_for_user(current_user.id)


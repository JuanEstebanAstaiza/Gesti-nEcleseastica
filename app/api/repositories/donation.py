from datetime import date
from decimal import Decimal
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.donation import Donation


class DonationRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, *, user_id: int | None, **data) -> Donation:
        # Calcular total y flags de método de pago
        amount_tithe = Decimal(str(data.get("amount_tithe", 0)))
        amount_offering = Decimal(str(data.get("amount_offering", 0)))
        amount_missions = Decimal(str(data.get("amount_missions", 0)))
        amount_special = Decimal(str(data.get("amount_special", 0)))
        amount_total = amount_tithe + amount_offering + amount_missions + amount_special
        
        cash_amount = Decimal(str(data.get("cash_amount", 0)))
        transfer_amount = Decimal(str(data.get("transfer_amount", 0)))
        
        is_cash = cash_amount > 0
        is_transfer = transfer_amount > 0
        
        # Calcular semana del año
        donation_date = data.get("donation_date")
        if isinstance(donation_date, str):
            donation_date = date.fromisoformat(donation_date)
        week_number = donation_date.isocalendar()[1] if donation_date else None
        
        donation = Donation(
            user_id=user_id,
            donor_name=data.get("donor_name"),
            donor_document=data.get("donor_document"),
            donor_address=data.get("donor_address"),
            donor_phone=data.get("donor_phone"),
            donor_email=data.get("donor_email"),
            amount_tithe=amount_tithe,
            amount_offering=amount_offering,
            amount_missions=amount_missions,
            amount_special=amount_special,
            amount_total=amount_total,
            is_cash=is_cash,
            is_transfer=is_transfer,
            payment_reference=data.get("payment_reference"),
            donation_date=donation_date,
            week_number=week_number,
            envelope_number=data.get("envelope_number"),
            note=data.get("note"),
            is_anonymous=data.get("is_anonymous", False),
            event_id=data.get("event_id"),
            created_by_id=user_id,
        )
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


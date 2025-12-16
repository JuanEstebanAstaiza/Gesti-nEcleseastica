from datetime import date
from decimal import Decimal
from pydantic import BaseModel, Field, ConfigDict


class DonationBase(BaseModel):
    donor_name: str
    donor_document: str | None = None
    donation_type: str = Field(pattern="^(diezmo|ofrenda|misiones|especial)$")
    amount: Decimal
    payment_method: str = Field(pattern="^(efectivo|transferencia|tarjeta|otro)$")
    note: str | None = None
    donation_date: date
    event_id: int | None = None


class DonationCreate(DonationBase):
    pass


class DonationRead(DonationBase):
    id: int
    user_id: int | None = None

    model_config = ConfigDict(from_attributes=True)


from datetime import datetime
from decimal import Decimal

from sqlalchemy import (
    Date,
    DateTime,
    ForeignKey,
    Numeric,
    String,
    Text,
    func,
    Enum,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


DONATION_TYPES = ("diezmo", "ofrenda", "misiones", "especial")
PAYMENT_METHODS = ("efectivo", "transferencia", "tarjeta", "otro")


class Donation(Base):
    __tablename__ = "donations"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), index=True)
    event_id: Mapped[int | None] = mapped_column(ForeignKey("events.id"), index=True)

    donor_name: Mapped[str] = mapped_column(String(255))
    donor_document: Mapped[str | None] = mapped_column(String(50))
    donation_type: Mapped[str] = mapped_column(
        Enum(*DONATION_TYPES, name="donation_type_enum"), index=True
    )
    amount: Mapped[Decimal] = mapped_column(Numeric(12, 2))
    payment_method: Mapped[str] = mapped_column(
        Enum(*PAYMENT_METHODS, name="payment_method_enum"), index=True
    )
    note: Mapped[str | None] = mapped_column(Text)
    donation_date: Mapped[datetime | None] = mapped_column(Date, index=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    user: Mapped["User"] = relationship("User", back_populates="donations")
    event: Mapped["Event"] = relationship("Event", back_populates="donations")
    documents: Mapped[list["Document"]] = relationship(
        "Document", back_populates="donation"
    )

    def __repr__(self) -> str:
        return f"Donation(id={self.id}, type={self.donation_type}, amount={self.amount})"


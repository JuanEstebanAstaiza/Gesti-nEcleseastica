"""
Modelo de Donación actualizado con montos separados por tipo
Formato basado en el comprobante oficial de la iglesia
"""
from datetime import datetime
from decimal import Decimal

from sqlalchemy import (
    Boolean,
    Date,
    DateTime,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Text,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Donation(Base):
    """
    Donación con montos separados por tipo (diezmo, ofrenda, misiones).
    Cada registro representa un sobre/comprobante de donación.
    """
    __tablename__ = "donations"

    id: Mapped[int] = mapped_column(primary_key=True)
    
    # Relaciones
    user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), index=True)
    event_id: Mapped[int | None] = mapped_column(ForeignKey("events.id"), index=True)
    
    # Datos del donante
    donor_name: Mapped[str] = mapped_column(String(255))
    donor_document: Mapped[str | None] = mapped_column(String(50))  # Cédula/NIT
    donor_address: Mapped[str | None] = mapped_column(String(500))
    donor_phone: Mapped[str | None] = mapped_column(String(50))
    donor_email: Mapped[str | None] = mapped_column(String(255))
    
    # Montos separados por tipo
    amount_tithe: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=0)  # Diezmo
    amount_offering: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=0)  # Ofrenda
    amount_missions: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=0)  # Misiones
    amount_special: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=0)  # Especial/Otros
    amount_total: Mapped[Decimal] = mapped_column(Numeric(12, 2))  # Total
    
    # Método de pago
    is_cash: Mapped[bool] = mapped_column(Boolean, default=True)  # Efectivo
    is_transfer: Mapped[bool] = mapped_column(Boolean, default=False)  # Transferencia
    payment_reference: Mapped[str | None] = mapped_column(String(100))  # Ref. de transferencia
    
    # Metadatos
    donation_date: Mapped[datetime | None] = mapped_column(Date, index=True)
    week_number: Mapped[int | None] = mapped_column(Integer)  # Número de semana
    envelope_number: Mapped[str | None] = mapped_column(String(50))  # Número de sobre
    note: Mapped[str | None] = mapped_column(Text)
    receipt_number: Mapped[str | None] = mapped_column(String(50), unique=True)  # Número de recibo
    
    # Auditoría
    is_anonymous: Mapped[bool] = mapped_column(Boolean, default=False)
    created_by_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    
    # Relationships
    user: Mapped["User"] = relationship("User", foreign_keys=[user_id], back_populates="donations")
    created_by: Mapped["User"] = relationship("User", foreign_keys=[created_by_id])
    event: Mapped["Event"] = relationship("Event", back_populates="donations")
    documents: Mapped[list["Document"]] = relationship("Document", back_populates="donation")

    def __repr__(self) -> str:
        return f"Donation(id={self.id}, total={self.amount_total}, date={self.donation_date})"


class DonationSummary(Base):
    """
    Resumen semanal de donaciones para reportes a contaduría.
    Se genera automáticamente al cerrar una semana.
    """
    __tablename__ = "donation_summaries"

    id: Mapped[int] = mapped_column(primary_key=True)
    
    # Período
    summary_date: Mapped[datetime] = mapped_column(Date, index=True)
    week_number: Mapped[int] = mapped_column(Integer)
    year: Mapped[int] = mapped_column(Integer)
    
    # Número de sobres/donaciones procesadas
    envelope_count: Mapped[int] = mapped_column(Integer, default=0)
    
    # Totales por tipo y método de pago
    tithe_cash: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=0)
    tithe_transfer: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=0)
    offering_cash: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=0)
    offering_transfer: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=0)
    missions_cash: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=0)
    missions_transfer: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=0)
    special_cash: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=0)
    special_transfer: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=0)
    
    # Totales generales
    total_cash: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=0)
    total_transfer: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=0)
    grand_total: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=0)
    
    # Diezmo de diezmos (10% para la denominación)
    tithe_of_tithes: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=0)
    
    # Testigos
    witness_1_name: Mapped[str | None] = mapped_column(String(255))
    witness_1_document: Mapped[str | None] = mapped_column(String(50))
    witness_2_name: Mapped[str | None] = mapped_column(String(255))
    witness_2_document: Mapped[str | None] = mapped_column(String(50))
    
    # Auditoría
    created_by_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    is_closed: Mapped[bool] = mapped_column(Boolean, default=False)
    closed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    
    notes: Mapped[str | None] = mapped_column(Text)

    created_by: Mapped["User"] = relationship("User")


# Import para evitar circular imports
from app.models.user import User
from app.models.event import Event
from app.models.document import Document

"""
Modelo de Gastos para la iglesia
Incluye categorías, etiquetas y documentos de soporte
"""
from datetime import datetime
from decimal import Decimal

from sqlalchemy import (
    Boolean,
    Date,
    DateTime,
    ForeignKey,
    Integer,
    JSON,
    Numeric,
    String,
    Text,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class ExpenseCategory(Base):
    """
    Categorías de gastos (personalizables por iglesia).
    Ej: Servicios públicos, Arriendo, Salarios, Mantenimiento, etc.
    """
    __tablename__ = "expense_categories"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    color: Mapped[str] = mapped_column(String(7), default="#6b7280")  # Color hex para UI
    icon: Mapped[str | None] = mapped_column(String(50))  # Nombre del icono
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    sort_order: Mapped[int] = mapped_column(Integer, default=0)
    
    # Presupuesto mensual opcional
    monthly_budget: Mapped[Decimal | None] = mapped_column(Numeric(12, 2))
    
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    expenses: Mapped[list["Expense"]] = relationship("Expense", back_populates="category")
    subcategories: Mapped[list["ExpenseSubcategory"]] = relationship("ExpenseSubcategory", back_populates="category")

    def __repr__(self) -> str:
        return f"ExpenseCategory(id={self.id}, name={self.name})"


class ExpenseSubcategory(Base):
    """
    Subcategorías de gastos (etiquetas más específicas).
    Ej: Dentro de "Servicios públicos": Agua, Luz, Gas, Internet
    """
    __tablename__ = "expense_subcategories"

    id: Mapped[int] = mapped_column(primary_key=True)
    category_id: Mapped[int] = mapped_column(ForeignKey("expense_categories.id", ondelete="CASCADE"), index=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    
    category: Mapped["ExpenseCategory"] = relationship("ExpenseCategory", back_populates="subcategories")
    expenses: Mapped[list["Expense"]] = relationship("Expense", back_populates="subcategory")


class ExpenseTag(Base):
    """
    Etiquetas libres para gastos (para filtrado y organización).
    Ej: Urgente, Recurrente, Deducible, etc.
    """
    __tablename__ = "expense_tags"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    color: Mapped[str] = mapped_column(String(7), default="#3b82f6")
    
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class Expense(Base):
    """
    Registro de un gasto de la iglesia.
    """
    __tablename__ = "expenses"

    id: Mapped[int] = mapped_column(primary_key=True)
    
    # Clasificación
    category_id: Mapped[int] = mapped_column(ForeignKey("expense_categories.id"), index=True)
    subcategory_id: Mapped[int | None] = mapped_column(ForeignKey("expense_subcategories.id"))
    
    # Información del gasto
    description: Mapped[str] = mapped_column(String(500), nullable=False)
    amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    expense_date: Mapped[datetime] = mapped_column(Date, index=True, nullable=False)
    
    # Proveedor/Beneficiario
    vendor_name: Mapped[str | None] = mapped_column(String(255))
    vendor_document: Mapped[str | None] = mapped_column(String(50))  # NIT/Cédula
    vendor_phone: Mapped[str | None] = mapped_column(String(50))
    
    # Método de pago
    payment_method: Mapped[str] = mapped_column(String(50), default="efectivo")  # efectivo, transferencia, cheque, tarjeta
    payment_reference: Mapped[str | None] = mapped_column(String(100))  # Número de cheque, referencia
    bank_account: Mapped[str | None] = mapped_column(String(100))  # Cuenta bancaria usada
    
    # Documento de soporte
    invoice_number: Mapped[str | None] = mapped_column(String(50))  # Número de factura
    receipt_number: Mapped[str | None] = mapped_column(String(50))  # Número de recibo
    
    # Estado
    status: Mapped[str] = mapped_column(String(20), default="pending")  # pending, approved, paid, cancelled
    is_recurring: Mapped[bool] = mapped_column(Boolean, default=False)
    recurrence_period: Mapped[str | None] = mapped_column(String(20))  # monthly, weekly, yearly
    
    # Etiquetas (almacenadas como JSON array de IDs)
    tags: Mapped[list | None] = mapped_column(JSON)
    
    # Notas adicionales
    notes: Mapped[str | None] = mapped_column(Text)
    
    # Auditoría
    created_by_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    approved_by_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    approved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    
    # Relationships
    category: Mapped["ExpenseCategory"] = relationship("ExpenseCategory", back_populates="expenses")
    subcategory: Mapped["ExpenseSubcategory"] = relationship("ExpenseSubcategory", back_populates="expenses")
    created_by: Mapped["User"] = relationship("User", foreign_keys=[created_by_id])
    approved_by: Mapped["User"] = relationship("User", foreign_keys=[approved_by_id])
    documents: Mapped[list["ExpenseDocument"]] = relationship("ExpenseDocument", back_populates="expense")

    def __repr__(self) -> str:
        return f"Expense(id={self.id}, amount={self.amount}, date={self.expense_date})"


class ExpenseDocument(Base):
    """
    Documentos de soporte para gastos (facturas, recibos, etc.)
    """
    __tablename__ = "expense_documents"

    id: Mapped[int] = mapped_column(primary_key=True)
    expense_id: Mapped[int] = mapped_column(ForeignKey("expenses.id", ondelete="CASCADE"), index=True)
    
    # Información del archivo
    file_name: Mapped[str] = mapped_column(String(255), nullable=False)
    stored_path: Mapped[str] = mapped_column(String(500), nullable=False)
    mime_type: Mapped[str] = mapped_column(String(100), nullable=False)
    size_bytes: Mapped[int] = mapped_column(Integer, nullable=False)
    checksum: Mapped[str | None] = mapped_column(String(64))
    
    # Tipo de documento
    document_type: Mapped[str] = mapped_column(String(50), default="invoice")  # invoice, receipt, quote, contract, other
    description: Mapped[str | None] = mapped_column(Text)
    
    # Auditoría
    uploaded_by_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    uploaded_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    
    expense: Mapped["Expense"] = relationship("Expense", back_populates="documents")
    uploaded_by: Mapped["User"] = relationship("User")


class ExpenseFolder(Base):
    """
    Carpetas para organizar documentos de gastos por período o categoría.
    """
    __tablename__ = "expense_folders"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    parent_id: Mapped[int | None] = mapped_column(ForeignKey("expense_folders.id"))
    
    # Tipo de carpeta
    folder_type: Mapped[str] = mapped_column(String(50), default="general")  # general, monthly, yearly, category
    
    # Para carpetas de período
    year: Mapped[int | None] = mapped_column(Integer)
    month: Mapped[int | None] = mapped_column(Integer)
    
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    
    # Self-referential relationship para subcarpetas
    parent: Mapped["ExpenseFolder"] = relationship("ExpenseFolder", remote_side=[id], backref="children")


# Import para evitar circular imports
from app.models.user import User


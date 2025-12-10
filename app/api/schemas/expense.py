"""
Schemas para módulo de gastos
"""
from datetime import date, datetime
from decimal import Decimal
from pydantic import BaseModel, Field, ConfigDict


# ============== Categorías ==============

class ExpenseCategoryCreate(BaseModel):
    """Crear categoría de gasto"""
    name: str = Field(..., min_length=1, max_length=100)
    description: str | None = None
    color: str = Field(default="#6b7280", pattern=r"^#[0-9a-fA-F]{6}$")
    icon: str | None = None
    monthly_budget: Decimal | None = Field(default=None, ge=0)


class ExpenseCategoryUpdate(BaseModel):
    """Actualizar categoría"""
    name: str | None = None
    description: str | None = None
    color: str | None = None
    icon: str | None = None
    monthly_budget: Decimal | None = None
    is_active: bool | None = None
    sort_order: int | None = None


class ExpenseCategoryRead(BaseModel):
    """Lectura de categoría"""
    id: int
    name: str
    description: str | None
    color: str
    icon: str | None
    is_active: bool
    sort_order: int
    monthly_budget: Decimal | None
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


# ============== Subcategorías ==============

class ExpenseSubcategoryCreate(BaseModel):
    """Crear subcategoría"""
    category_id: int
    name: str = Field(..., min_length=1, max_length=100)
    description: str | None = None


class ExpenseSubcategoryRead(BaseModel):
    """Lectura de subcategoría"""
    id: int
    category_id: int
    name: str
    description: str | None
    is_active: bool
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


# ============== Etiquetas ==============

class ExpenseTagCreate(BaseModel):
    """Crear etiqueta"""
    name: str = Field(..., min_length=1, max_length=50)
    color: str = Field(default="#3b82f6", pattern=r"^#[0-9a-fA-F]{6}$")


class ExpenseTagRead(BaseModel):
    """Lectura de etiqueta"""
    id: int
    name: str
    color: str
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


# ============== Gastos ==============

class ExpenseCreate(BaseModel):
    """Crear un gasto"""
    category_id: int
    subcategory_id: int | None = None
    
    description: str = Field(..., min_length=1, max_length=500)
    amount: Decimal = Field(..., gt=0)
    expense_date: date
    
    # Proveedor
    vendor_name: str | None = None
    vendor_document: str | None = None
    vendor_phone: str | None = None
    
    # Pago
    payment_method: str = Field(default="efectivo")  # efectivo, transferencia, cheque, tarjeta
    payment_reference: str | None = None
    bank_account: str | None = None
    
    # Documentos
    invoice_number: str | None = None
    receipt_number: str | None = None
    
    # Estado y recurrencia
    is_recurring: bool = False
    recurrence_period: str | None = None  # monthly, weekly, yearly
    
    tags: list[int] | None = None  # IDs de etiquetas
    notes: str | None = None


class ExpenseUpdate(BaseModel):
    """Actualizar gasto"""
    category_id: int | None = None
    subcategory_id: int | None = None
    description: str | None = None
    amount: Decimal | None = None
    expense_date: date | None = None
    vendor_name: str | None = None
    vendor_document: str | None = None
    vendor_phone: str | None = None
    payment_method: str | None = None
    payment_reference: str | None = None
    bank_account: str | None = None
    invoice_number: str | None = None
    receipt_number: str | None = None
    status: str | None = None  # pending, approved, paid, cancelled
    is_recurring: bool | None = None
    recurrence_period: str | None = None
    tags: list[int] | None = None
    notes: str | None = None


class ExpenseRead(BaseModel):
    """Lectura de gasto"""
    id: int
    category_id: int
    subcategory_id: int | None
    
    description: str
    amount: Decimal
    expense_date: date
    
    vendor_name: str | None
    vendor_document: str | None
    vendor_phone: str | None
    
    payment_method: str
    payment_reference: str | None
    bank_account: str | None
    
    invoice_number: str | None
    receipt_number: str | None
    
    status: str
    is_recurring: bool
    recurrence_period: str | None
    
    tags: list | None
    notes: str | None
    
    created_by_id: int
    approved_by_id: int | None
    created_at: datetime
    approved_at: datetime | None
    
    # Relaciones anidadas (opcional)
    category: ExpenseCategoryRead | None = None
    subcategory: ExpenseSubcategoryRead | None = None
    
    model_config = ConfigDict(from_attributes=True)


# ============== Documentos de Gastos ==============

class ExpenseDocumentRead(BaseModel):
    """Lectura de documento de gasto"""
    id: int
    expense_id: int
    file_name: str
    stored_path: str
    mime_type: str
    size_bytes: int
    checksum: str | None
    document_type: str
    description: str | None
    uploaded_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


# ============== Carpetas ==============

class ExpenseFolderCreate(BaseModel):
    """Crear carpeta"""
    name: str = Field(..., min_length=1, max_length=100)
    description: str | None = None
    parent_id: int | None = None
    folder_type: str = Field(default="general")
    year: int | None = None
    month: int | None = None


class ExpenseFolderRead(BaseModel):
    """Lectura de carpeta"""
    id: int
    name: str
    description: str | None
    parent_id: int | None
    folder_type: str
    year: int | None
    month: int | None
    is_active: bool
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


# ============== Reportes de Gastos ==============

class ExpenseReportRow(BaseModel):
    """Fila del reporte de gastos"""
    fecha: str
    categoria: str
    subcategoria: str | None
    descripcion: str
    proveedor: str | None
    metodo_pago: str
    monto: Decimal
    estado: str


class ExpenseReportSummary(BaseModel):
    """Resumen de gastos"""
    total_gastos: Decimal
    por_categoria: dict[str, Decimal]  # {"Servicios": 1000, "Arriendo": 5000}
    por_metodo_pago: dict[str, Decimal]  # {"efectivo": 3000, "transferencia": 3000}
    cantidad_gastos: int
    presupuesto_usado: dict[str, dict]  # {"Servicios": {"presupuesto": 2000, "gastado": 1000, "porcentaje": 50}}


class ExpenseMonthlyReport(BaseModel):
    """Reporte mensual de gastos"""
    church_name: str
    month: int
    year: int
    period_label: str
    expenses: list[ExpenseReportRow]
    summary: ExpenseReportSummary


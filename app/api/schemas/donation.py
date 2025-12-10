"""
Schemas para donaciones con formato actualizado
"""
from datetime import date, datetime
from decimal import Decimal
from pydantic import BaseModel, Field, ConfigDict, computed_field


class DonationCreate(BaseModel):
    """Crear una nueva donación con montos separados"""
    # Datos del donante
    donor_name: str = Field(..., min_length=1, max_length=255)
    donor_document: str | None = None  # Cédula/NIT
    donor_address: str | None = None
    donor_phone: str | None = None
    donor_email: str | None = None
    
    # Montos separados
    amount_tithe: Decimal = Field(default=0, ge=0)  # Diezmo
    amount_offering: Decimal = Field(default=0, ge=0)  # Ofrenda
    amount_missions: Decimal = Field(default=0, ge=0)  # Misiones
    amount_special: Decimal = Field(default=0, ge=0)  # Especial
    
    # Método de pago (puede ser ambos)
    cash_amount: Decimal = Field(default=0, ge=0)  # Monto en efectivo
    transfer_amount: Decimal = Field(default=0, ge=0)  # Monto por transferencia
    payment_reference: str | None = None
    
    # Metadatos
    donation_date: date
    envelope_number: str | None = None
    note: str | None = None
    is_anonymous: bool = False
    
    # Evento relacionado (opcional)
    event_id: int | None = None


class DonationRead(BaseModel):
    """Lectura de donación"""
    id: int
    
    # Donante
    donor_name: str
    donor_document: str | None
    donor_address: str | None
    donor_phone: str | None
    donor_email: str | None
    
    # Montos
    amount_tithe: Decimal
    amount_offering: Decimal
    amount_missions: Decimal
    amount_special: Decimal
    amount_total: Decimal
    
    # Método de pago
    is_cash: bool
    is_transfer: bool
    payment_reference: str | None
    
    # Metadatos
    donation_date: date
    week_number: int | None
    envelope_number: str | None
    receipt_number: str | None
    note: str | None
    is_anonymous: bool
    
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


class DonationReportRow(BaseModel):
    """Una fila del reporte mensual de donaciones"""
    fecha: str  # DD/MM/YYYY
    nombre: str
    efectivo: Decimal
    transferencia: Decimal
    documento: str
    diezmo: Decimal
    ofrenda: Decimal
    misiones: Decimal
    total: Decimal


class DonationReportSummary(BaseModel):
    """Resumen/totales del reporte"""
    total_efectivo: Decimal
    total_transferencia: Decimal
    total_diezmo: Decimal
    total_ofrenda: Decimal
    total_misiones: Decimal
    gran_total: Decimal
    cantidad_donaciones: int


class DonationMonthlyReport(BaseModel):
    """Reporte mensual completo"""
    church_name: str
    month: int
    year: int
    period_label: str  # "NOVIEMBRE 2025"
    donations: list[DonationReportRow]
    summary: DonationReportSummary


# ============== Resumen Semanal (Para Contadora) ==============

class WeeklySummaryCreate(BaseModel):
    """Crear resumen semanal"""
    summary_date: date
    week_number: int
    year: int
    
    # Testigos
    witness_1_name: str | None = None
    witness_1_document: str | None = None
    witness_2_name: str | None = None
    witness_2_document: str | None = None
    
    notes: str | None = None


class WeeklySummaryRead(BaseModel):
    """Lectura de resumen semanal"""
    id: int
    summary_date: date
    week_number: int
    year: int
    envelope_count: int
    
    # Por tipo y método
    tithe_cash: Decimal
    tithe_transfer: Decimal
    offering_cash: Decimal
    offering_transfer: Decimal
    missions_cash: Decimal
    missions_transfer: Decimal
    special_cash: Decimal
    special_transfer: Decimal
    
    # Totales
    total_cash: Decimal
    total_transfer: Decimal
    grand_total: Decimal
    tithe_of_tithes: Decimal
    
    # Testigos
    witness_1_name: str | None
    witness_1_document: str | None
    witness_2_name: str | None
    witness_2_document: str | None
    
    is_closed: bool
    closed_at: datetime | None
    notes: str | None
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


class AccountantReport(BaseModel):
    """Reporte para contadora (formato de la imagen)"""
    church_name: str
    logo_url: str | None
    
    # Encabezado
    fecha: str
    semana: int
    numero_sobres: int
    
    # Tabla principal
    # CONCEPTO | EFECTIVO | TRANSFERENCIA | TOTAL
    diezmos_efectivo: Decimal
    diezmos_transferencia: Decimal
    diezmos_total: Decimal
    
    ofrendas_efectivo: Decimal
    ofrendas_transferencia: Decimal
    ofrendas_total: Decimal
    
    misiones_efectivo: Decimal
    misiones_transferencia: Decimal
    misiones_total: Decimal
    
    total_efectivo: Decimal
    total_transferencia: Decimal
    valor_total: Decimal
    
    # Diezmo de diezmos
    diezmo_de_diezmos: Decimal
    
    # Testigos
    testigo_1: str | None
    testigo_2: str | None

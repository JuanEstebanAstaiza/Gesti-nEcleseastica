"""
Rutas para reportes de donaciones
Incluye:
- Reporte mensual detallado (Excel/CSV)
- Reporte semanal para contadora
- Exportación en diferentes formatos
"""
import csv
import io
from datetime import date, datetime
from decimal import Decimal
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Response
from fastapi.responses import StreamingResponse
from sqlalchemy import select, func, extract
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_current_user, require_admin
from app.db.session import get_session
from app.models.donation import Donation, DonationSummary
from app.api.schemas.donation import (
    DonationReportRow,
    DonationReportSummary,
    DonationMonthlyReport,
    AccountantReport,
    WeeklySummaryCreate,
    WeeklySummaryRead,
)

router = APIRouter(prefix="/reports/donations", tags=["donation-reports"])

MONTHS_ES = {
    1: "ENERO", 2: "FEBRERO", 3: "MARZO", 4: "ABRIL",
    5: "MAYO", 6: "JUNIO", 7: "JULIO", 8: "AGOSTO",
    9: "SEPTIEMBRE", 10: "OCTUBRE", 11: "NOVIEMBRE", 12: "DICIEMBRE"
}


@router.get("/monthly", response_model=DonationMonthlyReport)
async def get_monthly_report(
    month: int = Query(..., ge=1, le=12),
    year: int = Query(..., ge=2020, le=2100),
    session: AsyncSession = Depends(get_session),
    current_user=Depends(require_admin),
):
    """
    Obtiene el reporte mensual de donaciones en formato JSON.
    Columnas: FECHA | NOMBRE | EFECTIVO | TRANSFERENCIA | DOCUMENTO | DIEZMO | OFRENDA | MISIONES | TOTAL
    """
    # Consultar donaciones del mes
    query = (
        select(Donation)
        .where(
            extract("month", Donation.donation_date) == month,
            extract("year", Donation.donation_date) == year,
        )
        .order_by(Donation.donation_date, Donation.id)
    )
    
    result = await session.execute(query)
    donations = result.scalars().all()
    
    # Construir filas del reporte
    rows = []
    total_efectivo = Decimal("0")
    total_transferencia = Decimal("0")
    total_diezmo = Decimal("0")
    total_ofrenda = Decimal("0")
    total_misiones = Decimal("0")
    gran_total = Decimal("0")
    
    for d in donations:
        # Calcular efectivo y transferencia por donación
        # Si es_cash y es_transfer se determina por los flags
        efectivo = d.amount_total if d.is_cash and not d.is_transfer else Decimal("0")
        transferencia = d.amount_total if d.is_transfer and not d.is_cash else Decimal("0")
        
        # Si tiene ambos métodos, asumir que el total es la suma
        if d.is_cash and d.is_transfer:
            # En este caso, podríamos tener un campo específico, por ahora dividir
            efectivo = Decimal("0")  # Se requiere más info
            transferencia = d.amount_total
        
        # Nombre a mostrar (anónimo = OSI)
        nombre = "OSI" if d.is_anonymous else d.donor_name
        
        row = DonationReportRow(
            fecha=d.donation_date.strftime("%d/%m/%Y") if d.donation_date else "",
            nombre=nombre,
            efectivo=efectivo,
            transferencia=transferencia,
            documento=d.donor_document or "",
            diezmo=d.amount_tithe or Decimal("0"),
            ofrenda=d.amount_offering or Decimal("0"),
            misiones=d.amount_missions or Decimal("0"),
            total=d.amount_total,
        )
        rows.append(row)
        
        total_efectivo += efectivo
        total_transferencia += transferencia
        total_diezmo += d.amount_tithe or Decimal("0")
        total_ofrenda += d.amount_offering or Decimal("0")
        total_misiones += d.amount_missions or Decimal("0")
        gran_total += d.amount_total
    
    summary = DonationReportSummary(
        total_efectivo=total_efectivo,
        total_transferencia=total_transferencia,
        total_diezmo=total_diezmo,
        total_ofrenda=total_ofrenda,
        total_misiones=total_misiones,
        gran_total=gran_total,
        cantidad_donaciones=len(donations),
    )
    
    return DonationMonthlyReport(
        church_name="Iglesia Comunidad Cristiana de Fe",  # TODO: Obtener de config
        month=month,
        year=year,
        period_label=f"{MONTHS_ES[month]} {year}",
        donations=rows,
        summary=summary,
    )


@router.get("/monthly/csv")
async def export_monthly_csv(
    month: int = Query(..., ge=1, le=12),
    year: int = Query(..., ge=2020, le=2100),
    session: AsyncSession = Depends(get_session),
    current_user=Depends(require_admin),
):
    """
    Exporta el reporte mensual en formato CSV para Excel.
    Formato exacto como la imagen proporcionada.
    """
    # Obtener datos
    query = (
        select(Donation)
        .where(
            extract("month", Donation.donation_date) == month,
            extract("year", Donation.donation_date) == year,
        )
        .order_by(Donation.donation_date, Donation.id)
    )
    
    result = await session.execute(query)
    donations = result.scalars().all()
    
    # Crear CSV
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Encabezado con mes
    writer.writerow([MONTHS_ES[month], "NOMBRE", "EFECTIVO", "TRANSFERENCIA", "DOCUMENTO", "DIEZMO", "OFRENDA", "MISIONES", "TOTAL"])
    
    # Agrupar por semana para subtotales
    current_week = None
    week_totals = {
        "efectivo": Decimal("0"),
        "transferencia": Decimal("0"),
        "diezmo": Decimal("0"),
        "ofrenda": Decimal("0"),
        "misiones": Decimal("0"),
        "total": Decimal("0"),
    }
    
    grand_totals = {
        "efectivo": Decimal("0"),
        "transferencia": Decimal("0"),
        "diezmo": Decimal("0"),
        "ofrenda": Decimal("0"),
        "misiones": Decimal("0"),
        "total": Decimal("0"),
    }
    
    for d in donations:
        week = d.week_number or d.donation_date.isocalendar()[1] if d.donation_date else 0
        
        # Si cambiamos de semana, escribir subtotal
        if current_week is not None and week != current_week:
            writer.writerow([
                "TOTAL", "", 
                f"${week_totals['efectivo']:,.2f}",
                f"${week_totals['transferencia']:,.2f}",
                "",
                f"${week_totals['diezmo']:,.2f}",
                f"${week_totals['ofrenda']:,.2f}",
                f"${week_totals['misiones']:,.2f}",
                f"${week_totals['total']:,.2f}",
            ])
            # Separador
            writer.writerow(["NOMBRE", "EFECTIVO", "TRANSFERENCIA", "DOCUMENTO", "DIEZMO", "OFRENDA", "MISIONES", "TOTAL"])
            # Resetear totales de semana
            week_totals = {k: Decimal("0") for k in week_totals}
        
        current_week = week
        
        # Calcular valores
        efectivo = d.amount_total if d.is_cash and not d.is_transfer else Decimal("0")
        transferencia = d.amount_total if d.is_transfer else Decimal("0")
        nombre = "OSI" if d.is_anonymous else d.donor_name
        
        # Escribir fila
        writer.writerow([
            d.donation_date.strftime("%d/%m/%Y") if d.donation_date else "",
            nombre,
            f"${efectivo:,.2f}" if efectivo > 0 else "",
            f"${transferencia:,.2f}" if transferencia > 0 else "",
            d.donor_document or "",
            f"${d.amount_tithe:,.2f}" if d.amount_tithe else "",
            f"${d.amount_offering:,.2f}" if d.amount_offering else "",
            f"${d.amount_missions:,.2f}" if d.amount_missions else "",
            f"${d.amount_total:,.2f}",
        ])
        
        # Acumular totales
        week_totals["efectivo"] += efectivo
        week_totals["transferencia"] += transferencia
        week_totals["diezmo"] += d.amount_tithe or Decimal("0")
        week_totals["ofrenda"] += d.amount_offering or Decimal("0")
        week_totals["misiones"] += d.amount_missions or Decimal("0")
        week_totals["total"] += d.amount_total
        
        grand_totals["efectivo"] += efectivo
        grand_totals["transferencia"] += transferencia
        grand_totals["diezmo"] += d.amount_tithe or Decimal("0")
        grand_totals["ofrenda"] += d.amount_offering or Decimal("0")
        grand_totals["misiones"] += d.amount_missions or Decimal("0")
        grand_totals["total"] += d.amount_total
    
    # Último subtotal de semana
    if donations:
        writer.writerow([
            "TOTAL", "",
            f"${week_totals['efectivo']:,.2f}",
            f"${week_totals['transferencia']:,.2f}",
            "",
            f"${week_totals['diezmo']:,.2f}",
            f"${week_totals['ofrenda']:,.2f}",
            f"${week_totals['misiones']:,.2f}",
            f"${week_totals['total']:,.2f}",
        ])
    
    # Total general del mes
    writer.writerow([])  # Línea vacía
    writer.writerow([
        "GRAN TOTAL", "",
        f"${grand_totals['efectivo']:,.2f}",
        f"${grand_totals['transferencia']:,.2f}",
        "",
        f"${grand_totals['diezmo']:,.2f}",
        f"${grand_totals['ofrenda']:,.2f}",
        f"${grand_totals['misiones']:,.2f}",
        f"${grand_totals['total']:,.2f}",
    ])
    
    # Preparar respuesta
    output.seek(0)
    filename = f"donaciones_{MONTHS_ES[month].lower()}_{year}.csv"
    
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )


@router.get("/weekly/{week_number}", response_model=AccountantReport)
async def get_weekly_accountant_report(
    week_number: int,
    year: int = Query(..., ge=2020, le=2100),
    session: AsyncSession = Depends(get_session),
    current_user=Depends(require_admin),
):
    """
    Obtiene el reporte semanal para la contadora.
    Formato: CONCEPTO | EFECTIVO | TRANSFERENCIA | TOTAL
    """
    # Buscar resumen existente o calcular en vivo
    query = select(DonationSummary).where(
        DonationSummary.week_number == week_number,
        DonationSummary.year == year,
    )
    result = await session.execute(query)
    summary = result.scalar_one_or_none()
    
    if summary:
        return AccountantReport(
            church_name="Iglesia Comunidad Cristiana de Fe",
            logo_url=None,
            fecha=summary.summary_date.strftime("%d/%m/%Y"),
            semana=week_number,
            numero_sobres=summary.envelope_count,
            diezmos_efectivo=summary.tithe_cash,
            diezmos_transferencia=summary.tithe_transfer,
            diezmos_total=summary.tithe_cash + summary.tithe_transfer,
            ofrendas_efectivo=summary.offering_cash,
            ofrendas_transferencia=summary.offering_transfer,
            ofrendas_total=summary.offering_cash + summary.offering_transfer,
            misiones_efectivo=summary.missions_cash,
            misiones_transferencia=summary.missions_transfer,
            misiones_total=summary.missions_cash + summary.missions_transfer,
            total_efectivo=summary.total_cash,
            total_transferencia=summary.total_transfer,
            valor_total=summary.grand_total,
            diezmo_de_diezmos=summary.tithe_of_tithes,
            testigo_1=summary.witness_1_name,
            testigo_2=summary.witness_2_name,
        )
    
    # Calcular en vivo desde donaciones
    # Obtener donaciones de la semana
    query = (
        select(Donation)
        .where(
            Donation.week_number == week_number,
            extract("year", Donation.donation_date) == year,
        )
    )
    result = await session.execute(query)
    donations = result.scalars().all()
    
    # Calcular totales
    tithe_cash = Decimal("0")
    tithe_transfer = Decimal("0")
    offering_cash = Decimal("0")
    offering_transfer = Decimal("0")
    missions_cash = Decimal("0")
    missions_transfer = Decimal("0")
    
    for d in donations:
        if d.is_cash and not d.is_transfer:
            tithe_cash += d.amount_tithe or Decimal("0")
            offering_cash += d.amount_offering or Decimal("0")
            missions_cash += d.amount_missions or Decimal("0")
        elif d.is_transfer:
            tithe_transfer += d.amount_tithe or Decimal("0")
            offering_transfer += d.amount_offering or Decimal("0")
            missions_transfer += d.amount_missions or Decimal("0")
    
    total_cash = tithe_cash + offering_cash + missions_cash
    total_transfer = tithe_transfer + offering_transfer + missions_transfer
    grand_total = total_cash + total_transfer
    
    # Diezmo de diezmos = 10% del total de diezmos
    total_tithe = tithe_cash + tithe_transfer
    tithe_of_tithes = total_tithe * Decimal("0.10")
    
    return AccountantReport(
        church_name="Iglesia Comunidad Cristiana de Fe",
        logo_url=None,
        fecha=datetime.now().strftime("%d/%m/%Y"),
        semana=week_number,
        numero_sobres=len(donations),
        diezmos_efectivo=tithe_cash,
        diezmos_transferencia=tithe_transfer,
        diezmos_total=tithe_cash + tithe_transfer,
        ofrendas_efectivo=offering_cash,
        ofrendas_transferencia=offering_transfer,
        ofrendas_total=offering_cash + offering_transfer,
        misiones_efectivo=missions_cash,
        misiones_transferencia=missions_transfer,
        misiones_total=missions_cash + missions_transfer,
        total_efectivo=total_cash,
        total_transferencia=total_transfer,
        valor_total=grand_total,
        diezmo_de_diezmos=tithe_of_tithes,
        testigo_1=None,
        testigo_2=None,
    )


@router.get("/weekly/{week_number}/csv")
async def export_weekly_csv(
    week_number: int,
    year: int = Query(..., ge=2020, le=2100),
    session: AsyncSession = Depends(get_session),
    current_user=Depends(require_admin),
):
    """
    Exporta el reporte semanal para contadora en CSV.
    """
    report = await get_weekly_accountant_report(week_number, year, session, current_user)
    
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Encabezado del reporte
    writer.writerow([report.church_name])
    writer.writerow([])
    writer.writerow(["RELACIÓN DE DIEZMOS Y OFRENDAS"])
    writer.writerow([])
    writer.writerow(["FECHA:", report.fecha, "", "SEMANA:", report.semana])
    writer.writerow(["NÚMERO DE SOBRES:", report.numero_sobres])
    writer.writerow([])
    
    # Tabla principal
    writer.writerow(["CONCEPTO", "EFECTIVO", "TRANSFERENCIA", "TOTAL"])
    writer.writerow([
        "DIEZMOS",
        f"${report.diezmos_efectivo:,.2f}",
        f"${report.diezmos_transferencia:,.2f}",
        f"${report.diezmos_total:,.2f}",
    ])
    writer.writerow([
        "OFRENDAS",
        f"${report.ofrendas_efectivo:,.2f}",
        f"${report.ofrendas_transferencia:,.2f}",
        f"${report.ofrendas_total:,.2f}",
    ])
    writer.writerow([
        "MISIONES",
        f"${report.misiones_efectivo:,.2f}",
        f"${report.misiones_transferencia:,.2f}",
        f"${report.misiones_total:,.2f}",
    ])
    writer.writerow([
        "VALOR TOTAL",
        f"${report.total_efectivo:,.2f}",
        f"${report.total_transferencia:,.2f}",
        f"${report.valor_total:,.2f}",
    ])
    writer.writerow([])
    
    # Diezmo de diezmos
    writer.writerow(["DIEZMOS DE DIEZMOS", f"${report.diezmo_de_diezmos:,.2f}"])
    writer.writerow([])
    
    # Testigos
    writer.writerow(["TESTIGO 1", report.testigo_1 or "________________"])
    writer.writerow(["TESTIGO 2", report.testigo_2 or "________________"])
    
    output.seek(0)
    filename = f"reporte_contadora_semana_{week_number}_{year}.csv"
    
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )


@router.post("/weekly/close", response_model=WeeklySummaryRead)
async def close_weekly_summary(
    data: WeeklySummaryCreate,
    session: AsyncSession = Depends(get_session),
    current_user=Depends(require_admin),
):
    """
    Cierra el resumen semanal y lo guarda para auditoría.
    Una vez cerrado, no se pueden modificar las donaciones de esa semana.
    """
    # Verificar que no exista ya
    query = select(DonationSummary).where(
        DonationSummary.week_number == data.week_number,
        DonationSummary.year == data.year,
    )
    result = await session.execute(query)
    existing = result.scalar_one_or_none()
    
    if existing and existing.is_closed:
        raise HTTPException(400, "Esta semana ya está cerrada")
    
    # Calcular totales desde donaciones
    query = (
        select(Donation)
        .where(
            Donation.week_number == data.week_number,
            extract("year", Donation.donation_date) == data.year,
        )
    )
    result = await session.execute(query)
    donations = result.scalars().all()
    
    # Calcular totales
    tithe_cash = Decimal("0")
    tithe_transfer = Decimal("0")
    offering_cash = Decimal("0")
    offering_transfer = Decimal("0")
    missions_cash = Decimal("0")
    missions_transfer = Decimal("0")
    special_cash = Decimal("0")
    special_transfer = Decimal("0")
    
    for d in donations:
        if d.is_cash and not d.is_transfer:
            tithe_cash += d.amount_tithe or Decimal("0")
            offering_cash += d.amount_offering or Decimal("0")
            missions_cash += d.amount_missions or Decimal("0")
            special_cash += d.amount_special or Decimal("0")
        else:
            tithe_transfer += d.amount_tithe or Decimal("0")
            offering_transfer += d.amount_offering or Decimal("0")
            missions_transfer += d.amount_missions or Decimal("0")
            special_transfer += d.amount_special or Decimal("0")
    
    total_cash = tithe_cash + offering_cash + missions_cash + special_cash
    total_transfer = tithe_transfer + offering_transfer + missions_transfer + special_transfer
    grand_total = total_cash + total_transfer
    tithe_of_tithes = (tithe_cash + tithe_transfer) * Decimal("0.10")
    
    if existing:
        # Actualizar existente
        existing.tithe_cash = tithe_cash
        existing.tithe_transfer = tithe_transfer
        existing.offering_cash = offering_cash
        existing.offering_transfer = offering_transfer
        existing.missions_cash = missions_cash
        existing.missions_transfer = missions_transfer
        existing.special_cash = special_cash
        existing.special_transfer = special_transfer
        existing.total_cash = total_cash
        existing.total_transfer = total_transfer
        existing.grand_total = grand_total
        existing.tithe_of_tithes = tithe_of_tithes
        existing.envelope_count = len(donations)
        existing.witness_1_name = data.witness_1_name
        existing.witness_1_document = data.witness_1_document
        existing.witness_2_name = data.witness_2_name
        existing.witness_2_document = data.witness_2_document
        existing.is_closed = True
        existing.closed_at = datetime.utcnow()
        existing.notes = data.notes
        
        await session.commit()
        await session.refresh(existing)
        return existing
    
    # Crear nuevo
    summary = DonationSummary(
        summary_date=data.summary_date,
        week_number=data.week_number,
        year=data.year,
        envelope_count=len(donations),
        tithe_cash=tithe_cash,
        tithe_transfer=tithe_transfer,
        offering_cash=offering_cash,
        offering_transfer=offering_transfer,
        missions_cash=missions_cash,
        missions_transfer=missions_transfer,
        special_cash=special_cash,
        special_transfer=special_transfer,
        total_cash=total_cash,
        total_transfer=total_transfer,
        grand_total=grand_total,
        tithe_of_tithes=tithe_of_tithes,
        witness_1_name=data.witness_1_name,
        witness_1_document=data.witness_1_document,
        witness_2_name=data.witness_2_name,
        witness_2_document=data.witness_2_document,
        is_closed=True,
        closed_at=datetime.utcnow(),
        notes=data.notes,
        created_by_id=current_user.id,
    )
    
    session.add(summary)
    await session.commit()
    await session.refresh(summary)
    
    return summary


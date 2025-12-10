"""
Rutas para reportes legacy (actualizado para nuevo formato de donaciones)
"""
from datetime import date

from fastapi import APIRouter, Depends, Query
from sqlalchemy import and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.responses import StreamingResponse
import csv
import io

from app.core.deps import require_admin
from app.db.session import get_session
from app.models.donation import Donation

router = APIRouter(prefix="/reports", tags=["reports"], dependencies=[Depends(require_admin)])


def _apply_filters(query, start_date: date | None, end_date: date | None):
    conditions = []
    if start_date:
        conditions.append(Donation.donation_date >= start_date)
    if end_date:
        conditions.append(Donation.donation_date <= end_date)
    if conditions:
        query = query.where(and_(*conditions))
    return query


def _month_expr(session: AsyncSession):
    dialect = session.bind.dialect.name
    if dialect == "sqlite":
        return func.strftime("%Y-%m", Donation.donation_date)
    # postgres or others
    return func.to_char(Donation.donation_date, "YYYY-MM")


@router.get("/summary")
async def summary(
    session: AsyncSession = Depends(get_session),
    start_date: date | None = Query(None),
    end_date: date | None = Query(None),
):
    """Resumen de donaciones con totales"""
    total_amount_stmt = select(func.coalesce(func.sum(Donation.amount_total), 0))
    total_amount_stmt = _apply_filters(total_amount_stmt, start_date, end_date)

    count_stmt = select(func.count(Donation.id))
    count_stmt = _apply_filters(count_stmt, start_date, end_date)
    
    # Totales por tipo
    tithe_stmt = select(func.coalesce(func.sum(Donation.amount_tithe), 0))
    tithe_stmt = _apply_filters(tithe_stmt, start_date, end_date)
    
    offering_stmt = select(func.coalesce(func.sum(Donation.amount_offering), 0))
    offering_stmt = _apply_filters(offering_stmt, start_date, end_date)
    
    missions_stmt = select(func.coalesce(func.sum(Donation.amount_missions), 0))
    missions_stmt = _apply_filters(missions_stmt, start_date, end_date)

    total_amount = (await session.execute(total_amount_stmt)).scalar_one()
    total_count = (await session.execute(count_stmt)).scalar_one()
    total_tithe = (await session.execute(tithe_stmt)).scalar_one()
    total_offering = (await session.execute(offering_stmt)).scalar_one()
    total_missions = (await session.execute(missions_stmt)).scalar_one()

    return {
        "total_donations": total_count,
        "total_amount": float(total_amount),
        "by_type": {
            "diezmo": float(total_tithe),
            "ofrenda": float(total_offering),
            "misiones": float(total_missions),
        },
        "filters": {
            "start_date": start_date,
            "end_date": end_date,
        },
    }


@router.get("/dashboard")
async def dashboard(
    session: AsyncSession = Depends(get_session),
    start_date: date | None = Query(None),
    end_date: date | None = Query(None),
):
    """Dashboard con datos por mes"""
    month_col = _month_expr(session)

    base = select(
        month_col.label("month"), 
        func.count(Donation.id), 
        func.coalesce(func.sum(Donation.amount_total), 0.0)
    ).group_by(month_col)
    base = _apply_filters(base, start_date, end_date)

    by_month_rows = (await session.execute(base)).all()
    by_month = {
        row[0]: {"count": row[1], "amount": float(row[2])} for row in by_month_rows
    }

    # Por tipo de pago
    cash_stmt = select(func.coalesce(func.sum(Donation.amount_total), 0)).where(Donation.is_cash == True)
    cash_stmt = _apply_filters(cash_stmt, start_date, end_date)
    
    transfer_stmt = select(func.coalesce(func.sum(Donation.amount_total), 0)).where(Donation.is_transfer == True)
    transfer_stmt = _apply_filters(transfer_stmt, start_date, end_date)
    
    total_cash = (await session.execute(cash_stmt)).scalar_one()
    total_transfer = (await session.execute(transfer_stmt)).scalar_one()

    return {
        "by_month": by_month,
        "by_payment_method": {
            "efectivo": float(total_cash),
            "transferencia": float(total_transfer),
        },
        "filters": {
            "start_date": start_date,
            "end_date": end_date,
        },
    }


@router.get("/export")
async def export_report(
    session: AsyncSession = Depends(get_session),
    start_date: date | None = Query(None),
    end_date: date | None = Query(None),
):
    """Exportar donaciones a CSV"""
    stmt = select(
        Donation.id,
        Donation.donor_name,
        Donation.donor_document,
        Donation.amount_tithe,
        Donation.amount_offering,
        Donation.amount_missions,
        Donation.amount_special,
        Donation.amount_total,
        Donation.is_cash,
        Donation.is_transfer,
        Donation.donation_date,
    )
    stmt = _apply_filters(stmt, start_date, end_date)
    rows = (await session.execute(stmt)).all()

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow([
        "id", "donor_name", "donor_document", 
        "diezmo", "ofrenda", "misiones", "especial", "total",
        "efectivo", "transferencia", "fecha"
    ])
    for r in rows:
        writer.writerow([
            r[0], r[1], r[2],
            float(r[3] or 0), float(r[4] or 0), float(r[5] or 0), float(r[6] or 0), float(r[7] or 0),
            "Sí" if r[8] else "No", "Sí" if r[9] else "No",
            r[10].strftime("%Y-%m-%d") if r[10] else ""
        ])
    output.seek(0)

    filename = "donations_export.csv"
    return StreamingResponse(
        output,
        media_type="text/csv",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )

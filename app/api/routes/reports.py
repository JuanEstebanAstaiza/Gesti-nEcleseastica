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


def _apply_filters(query, start_date: date | None, end_date: date | None, donation_type: str | None):
    conditions = []
    if start_date:
        conditions.append(Donation.donation_date >= start_date)
    if end_date:
        conditions.append(Donation.donation_date <= end_date)
    if donation_type:
        conditions.append(Donation.donation_type == donation_type)
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
    donation_type: str | None = Query(None),
):
    base = select(Donation)
    base = _apply_filters(base, start_date, end_date, donation_type)

    total_amount_stmt = select(func.coalesce(func.sum(Donation.amount), 0))
    total_amount_stmt = _apply_filters(total_amount_stmt, start_date, end_date, donation_type)

    count_stmt = select(func.count(Donation.id))
    count_stmt = _apply_filters(count_stmt, start_date, end_date, donation_type)

    by_type_stmt = select(Donation.donation_type, func.count(Donation.id)).group_by(Donation.donation_type)
    by_type_stmt = _apply_filters(by_type_stmt, start_date, end_date, donation_type)

    total_amount = (await session.execute(total_amount_stmt)).scalar_one()
    total_count = (await session.execute(count_stmt)).scalar_one()
    by_type = (await session.execute(by_type_stmt)).all()

    return {
        "total_donations": total_count,
        "total_amount": float(total_amount),
        "by_type": {row[0]: row[1] for row in by_type},
        "filters": {
            "start_date": start_date,
            "end_date": end_date,
            "donation_type": donation_type,
        },
    }


@router.get("/dashboard")
async def dashboard(
    session: AsyncSession = Depends(get_session),
    start_date: date | None = Query(None),
    end_date: date | None = Query(None),
    donation_type: str | None = Query(None),
):
    month_col = _month_expr(session)

    base = select(month_col.label("month"), func.count(Donation.id), func.coalesce(func.sum(Donation.amount), 0.0)).group_by(
        month_col
    )
    base = _apply_filters(base, start_date, end_date, donation_type)

    by_month_rows = (await session.execute(base)).all()
    by_month = {
        row[0]: {"count": row[1], "amount": float(row[2])} for row in by_month_rows
    }

    by_type_stmt = select(Donation.donation_type, func.count(Donation.id), func.coalesce(func.sum(Donation.amount), 0.0)).group_by(
        Donation.donation_type
    )
    by_type_stmt = _apply_filters(by_type_stmt, start_date, end_date, donation_type)
    by_type_rows = (await session.execute(by_type_stmt)).all()
    by_type = {row[0]: {"count": row[1], "amount": float(row[2])} for row in by_type_rows}

    return {
        "by_month": by_month,
        "by_type": by_type,
        "filters": {
            "start_date": start_date,
            "end_date": end_date,
            "donation_type": donation_type,
        },
    }


@router.get("/export")
async def export_report(
    session: AsyncSession = Depends(get_session),
    start_date: date | None = Query(None),
    end_date: date | None = Query(None),
    donation_type: str | None = Query(None),
):
    stmt = select(
        Donation.id,
        Donation.donor_name,
        Donation.donation_type,
        Donation.amount,
        Donation.payment_method,
        Donation.donation_date,
    )
    stmt = _apply_filters(stmt, start_date, end_date, donation_type)
    rows = (await session.execute(stmt)).all()

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["id", "donor_name", "donation_type", "amount", "payment_method", "donation_date"])
    for r in rows:
        writer.writerow(r)
    output.seek(0)

    filename = "donations_export.csv"
    return StreamingResponse(
        output,
        media_type="text/csv",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


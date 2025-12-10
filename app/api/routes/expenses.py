"""
Rutas para el módulo de gastos
CRUD completo para categorías, subcategorías, etiquetas, gastos y documentos
"""
import csv
import io
from datetime import date, datetime
from decimal import Decimal
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File, Form
from fastapi.responses import StreamingResponse, FileResponse
from sqlalchemy import select, func, extract
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.deps import get_current_user, require_admin
from app.core.storage import save_file
from app.db.session import get_session
from app.models.expense import (
    Expense,
    ExpenseCategory,
    ExpenseSubcategory,
    ExpenseTag,
    ExpenseDocument,
    ExpenseFolder,
)
from app.api.schemas.expense import (
    ExpenseCategoryCreate,
    ExpenseCategoryUpdate,
    ExpenseCategoryRead,
    ExpenseSubcategoryCreate,
    ExpenseSubcategoryRead,
    ExpenseTagCreate,
    ExpenseTagRead,
    ExpenseCreate,
    ExpenseUpdate,
    ExpenseRead,
    ExpenseDocumentRead,
    ExpenseFolderCreate,
    ExpenseFolderRead,
    ExpenseReportRow,
    ExpenseReportSummary,
    ExpenseMonthlyReport,
)

router = APIRouter(prefix="/expenses", tags=["expenses"])

MONTHS_ES = {
    1: "ENERO", 2: "FEBRERO", 3: "MARZO", 4: "ABRIL",
    5: "MAYO", 6: "JUNIO", 7: "JULIO", 8: "AGOSTO",
    9: "SEPTIEMBRE", 10: "OCTUBRE", 11: "NOVIEMBRE", 12: "DICIEMBRE"
}


# ==================== CATEGORÍAS ====================

@router.get("/categories", response_model=list[ExpenseCategoryRead])
async def list_categories(
    include_inactive: bool = False,
    session: AsyncSession = Depends(get_session),
    current_user=Depends(get_current_user),
):
    """Lista todas las categorías de gastos"""
    query = select(ExpenseCategory).order_by(ExpenseCategory.sort_order)
    if not include_inactive:
        query = query.where(ExpenseCategory.is_active == True)
    
    result = await session.execute(query)
    return result.scalars().all()


@router.post("/categories", response_model=ExpenseCategoryRead, status_code=201)
async def create_category(
    data: ExpenseCategoryCreate,
    session: AsyncSession = Depends(get_session),
    current_user=Depends(require_admin),
):
    """Crea una nueva categoría de gasto"""
    category = ExpenseCategory(**data.model_dump())
    session.add(category)
    await session.commit()
    await session.refresh(category)
    return category


@router.patch("/categories/{category_id}", response_model=ExpenseCategoryRead)
async def update_category(
    category_id: int,
    data: ExpenseCategoryUpdate,
    session: AsyncSession = Depends(get_session),
    current_user=Depends(require_admin),
):
    """Actualiza una categoría"""
    query = select(ExpenseCategory).where(ExpenseCategory.id == category_id)
    result = await session.execute(query)
    category = result.scalar_one_or_none()
    
    if not category:
        raise HTTPException(404, "Categoría no encontrada")
    
    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(category, key, value)
    
    await session.commit()
    await session.refresh(category)
    return category


@router.delete("/categories/{category_id}", status_code=204)
async def delete_category(
    category_id: int,
    session: AsyncSession = Depends(get_session),
    current_user=Depends(require_admin),
):
    """Desactiva una categoría (soft delete)"""
    query = select(ExpenseCategory).where(ExpenseCategory.id == category_id)
    result = await session.execute(query)
    category = result.scalar_one_or_none()
    
    if not category:
        raise HTTPException(404, "Categoría no encontrada")
    
    category.is_active = False
    await session.commit()


# ==================== SUBCATEGORÍAS ====================

@router.get("/categories/{category_id}/subcategories", response_model=list[ExpenseSubcategoryRead])
async def list_subcategories(
    category_id: int,
    session: AsyncSession = Depends(get_session),
    current_user=Depends(get_current_user),
):
    """Lista subcategorías de una categoría"""
    query = (
        select(ExpenseSubcategory)
        .where(
            ExpenseSubcategory.category_id == category_id,
            ExpenseSubcategory.is_active == True,
        )
    )
    result = await session.execute(query)
    return result.scalars().all()


@router.post("/subcategories", response_model=ExpenseSubcategoryRead, status_code=201)
async def create_subcategory(
    data: ExpenseSubcategoryCreate,
    session: AsyncSession = Depends(get_session),
    current_user=Depends(require_admin),
):
    """Crea una subcategoría"""
    subcategory = ExpenseSubcategory(**data.model_dump())
    session.add(subcategory)
    await session.commit()
    await session.refresh(subcategory)
    return subcategory


# ==================== ETIQUETAS ====================

@router.get("/tags", response_model=list[ExpenseTagRead])
async def list_tags(
    session: AsyncSession = Depends(get_session),
    current_user=Depends(get_current_user),
):
    """Lista todas las etiquetas"""
    query = select(ExpenseTag).order_by(ExpenseTag.name)
    result = await session.execute(query)
    return result.scalars().all()


@router.post("/tags", response_model=ExpenseTagRead, status_code=201)
async def create_tag(
    data: ExpenseTagCreate,
    session: AsyncSession = Depends(get_session),
    current_user=Depends(require_admin),
):
    """Crea una nueva etiqueta"""
    # Verificar si ya existe
    query = select(ExpenseTag).where(ExpenseTag.name == data.name)
    result = await session.execute(query)
    if result.scalar_one_or_none():
        raise HTTPException(400, "Ya existe una etiqueta con ese nombre")
    
    tag = ExpenseTag(**data.model_dump())
    session.add(tag)
    await session.commit()
    await session.refresh(tag)
    return tag


@router.delete("/tags/{tag_id}", status_code=204)
async def delete_tag(
    tag_id: int,
    session: AsyncSession = Depends(get_session),
    current_user=Depends(require_admin),
):
    """Elimina una etiqueta"""
    query = select(ExpenseTag).where(ExpenseTag.id == tag_id)
    result = await session.execute(query)
    tag = result.scalar_one_or_none()
    
    if not tag:
        raise HTTPException(404, "Etiqueta no encontrada")
    
    await session.delete(tag)
    await session.commit()


# ==================== GASTOS ====================

@router.get("/", response_model=list[ExpenseRead])
async def list_expenses(
    category_id: Optional[int] = None,
    status: Optional[str] = None,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    limit: int = Query(default=50, le=200),
    offset: int = 0,
    session: AsyncSession = Depends(get_session),
    current_user=Depends(get_current_user),
):
    """Lista gastos con filtros opcionales"""
    query = (
        select(Expense)
        .options(
            selectinload(Expense.category),
            selectinload(Expense.subcategory),
        )
        .order_by(Expense.expense_date.desc(), Expense.id.desc())
    )
    
    if category_id:
        query = query.where(Expense.category_id == category_id)
    if status:
        query = query.where(Expense.status == status)
    if start_date:
        query = query.where(Expense.expense_date >= start_date)
    if end_date:
        query = query.where(Expense.expense_date <= end_date)
    
    query = query.limit(limit).offset(offset)
    
    result = await session.execute(query)
    return result.scalars().all()


@router.get("/{expense_id}", response_model=ExpenseRead)
async def get_expense(
    expense_id: int,
    session: AsyncSession = Depends(get_session),
    current_user=Depends(get_current_user),
):
    """Obtiene un gasto por ID"""
    query = (
        select(Expense)
        .options(
            selectinload(Expense.category),
            selectinload(Expense.subcategory),
        )
        .where(Expense.id == expense_id)
    )
    result = await session.execute(query)
    expense = result.scalar_one_or_none()
    
    if not expense:
        raise HTTPException(404, "Gasto no encontrado")
    
    return expense


@router.post("/", response_model=ExpenseRead, status_code=201)
async def create_expense(
    data: ExpenseCreate,
    session: AsyncSession = Depends(get_session),
    current_user=Depends(require_admin),
):
    """Crea un nuevo gasto"""
    # Verificar que la categoría existe
    query = select(ExpenseCategory).where(ExpenseCategory.id == data.category_id)
    result = await session.execute(query)
    if not result.scalar_one_or_none():
        raise HTTPException(400, "Categoría no encontrada")
    
    expense = Expense(
        **data.model_dump(),
        created_by_id=current_user.id,
    )
    session.add(expense)
    await session.commit()
    await session.refresh(expense)
    
    # Cargar relaciones
    query = (
        select(Expense)
        .options(
            selectinload(Expense.category),
            selectinload(Expense.subcategory),
        )
        .where(Expense.id == expense.id)
    )
    result = await session.execute(query)
    return result.scalar_one()


@router.patch("/{expense_id}", response_model=ExpenseRead)
async def update_expense(
    expense_id: int,
    data: ExpenseUpdate,
    session: AsyncSession = Depends(get_session),
    current_user=Depends(require_admin),
):
    """Actualiza un gasto"""
    query = select(Expense).where(Expense.id == expense_id)
    result = await session.execute(query)
    expense = result.scalar_one_or_none()
    
    if not expense:
        raise HTTPException(404, "Gasto no encontrado")
    
    if expense.status == "paid":
        raise HTTPException(400, "No se puede modificar un gasto ya pagado")
    
    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(expense, key, value)
    
    await session.commit()
    
    # Reload with relationships
    query = (
        select(Expense)
        .options(
            selectinload(Expense.category),
            selectinload(Expense.subcategory),
        )
        .where(Expense.id == expense_id)
    )
    result = await session.execute(query)
    return result.scalar_one()


@router.post("/{expense_id}/approve", response_model=ExpenseRead)
async def approve_expense(
    expense_id: int,
    session: AsyncSession = Depends(get_session),
    current_user=Depends(require_admin),
):
    """Aprueba un gasto pendiente"""
    query = select(Expense).where(Expense.id == expense_id)
    result = await session.execute(query)
    expense = result.scalar_one_or_none()
    
    if not expense:
        raise HTTPException(404, "Gasto no encontrado")
    
    if expense.status != "pending":
        raise HTTPException(400, f"El gasto está en estado '{expense.status}', no se puede aprobar")
    
    expense.status = "approved"
    expense.approved_by_id = current_user.id
    expense.approved_at = datetime.utcnow()
    
    await session.commit()
    
    # Reload with relationships
    query = (
        select(Expense)
        .options(
            selectinload(Expense.category),
            selectinload(Expense.subcategory),
        )
        .where(Expense.id == expense_id)
    )
    result = await session.execute(query)
    return result.scalar_one()


@router.post("/{expense_id}/pay", response_model=ExpenseRead)
async def mark_expense_paid(
    expense_id: int,
    payment_reference: Optional[str] = None,
    session: AsyncSession = Depends(get_session),
    current_user=Depends(require_admin),
):
    """Marca un gasto como pagado"""
    query = select(Expense).where(Expense.id == expense_id)
    result = await session.execute(query)
    expense = result.scalar_one_or_none()
    
    if not expense:
        raise HTTPException(404, "Gasto no encontrado")
    
    if expense.status not in ("pending", "approved"):
        raise HTTPException(400, f"El gasto está en estado '{expense.status}'")
    
    expense.status = "paid"
    if payment_reference:
        expense.payment_reference = payment_reference
    
    await session.commit()
    
    # Reload with relationships
    query = (
        select(Expense)
        .options(
            selectinload(Expense.category),
            selectinload(Expense.subcategory),
        )
        .where(Expense.id == expense_id)
    )
    result = await session.execute(query)
    return result.scalar_one()


@router.delete("/{expense_id}", status_code=204)
async def cancel_expense(
    expense_id: int,
    session: AsyncSession = Depends(get_session),
    current_user=Depends(require_admin),
):
    """Cancela un gasto (no lo elimina)"""
    query = select(Expense).where(Expense.id == expense_id)
    result = await session.execute(query)
    expense = result.scalar_one_or_none()
    
    if not expense:
        raise HTTPException(404, "Gasto no encontrado")
    
    if expense.status == "paid":
        raise HTTPException(400, "No se puede cancelar un gasto ya pagado")
    
    expense.status = "cancelled"
    await session.commit()


# ==================== DOCUMENTOS DE GASTOS ====================

@router.get("/{expense_id}/documents", response_model=list[ExpenseDocumentRead])
async def list_expense_documents(
    expense_id: int,
    session: AsyncSession = Depends(get_session),
    current_user=Depends(get_current_user),
):
    """Lista documentos de un gasto"""
    query = select(ExpenseDocument).where(ExpenseDocument.expense_id == expense_id)
    result = await session.execute(query)
    return result.scalars().all()


@router.post("/{expense_id}/documents", response_model=ExpenseDocumentRead, status_code=201)
async def upload_expense_document(
    expense_id: int,
    file: UploadFile = File(...),
    document_type: str = Form(default="invoice"),
    description: str = Form(default=None),
    session: AsyncSession = Depends(get_session),
    current_user=Depends(require_admin),
):
    """Sube un documento de soporte para un gasto"""
    # Verificar que el gasto existe
    query = select(Expense).where(Expense.id == expense_id)
    result = await session.execute(query)
    if not result.scalar_one_or_none():
        raise HTTPException(404, "Gasto no encontrado")
    
    # Guardar archivo
    content = await file.read()
    stored_path, checksum = save_file(
        content,
        file.filename,
        file.content_type,
        subfolder=f"expenses/{expense_id}",
    )
    
    doc = ExpenseDocument(
        expense_id=expense_id,
        file_name=file.filename,
        stored_path=stored_path,
        mime_type=file.content_type,
        size_bytes=len(content),
        checksum=checksum,
        document_type=document_type,
        description=description,
        uploaded_by_id=current_user.id,
    )
    
    session.add(doc)
    await session.commit()
    await session.refresh(doc)
    return doc


@router.get("/{expense_id}/documents/{doc_id}/download")
async def download_expense_document(
    expense_id: int,
    doc_id: int,
    session: AsyncSession = Depends(get_session),
    current_user=Depends(get_current_user),
):
    """Descarga un documento de gasto"""
    query = select(ExpenseDocument).where(
        ExpenseDocument.id == doc_id,
        ExpenseDocument.expense_id == expense_id,
    )
    result = await session.execute(query)
    doc = result.scalar_one_or_none()
    
    if not doc:
        raise HTTPException(404, "Documento no encontrado")
    
    return FileResponse(
        doc.stored_path,
        media_type=doc.mime_type,
        filename=doc.file_name,
    )


# ==================== CARPETAS ====================

@router.get("/folders", response_model=list[ExpenseFolderRead])
async def list_folders(
    parent_id: Optional[int] = None,
    session: AsyncSession = Depends(get_session),
    current_user=Depends(get_current_user),
):
    """Lista carpetas de gastos"""
    query = select(ExpenseFolder).where(ExpenseFolder.is_active == True)
    if parent_id:
        query = query.where(ExpenseFolder.parent_id == parent_id)
    else:
        query = query.where(ExpenseFolder.parent_id == None)
    
    result = await session.execute(query)
    return result.scalars().all()


@router.post("/folders", response_model=ExpenseFolderRead, status_code=201)
async def create_folder(
    data: ExpenseFolderCreate,
    session: AsyncSession = Depends(get_session),
    current_user=Depends(require_admin),
):
    """Crea una carpeta para organizar documentos"""
    folder = ExpenseFolder(**data.model_dump())
    session.add(folder)
    await session.commit()
    await session.refresh(folder)
    return folder


# ==================== REPORTES DE GASTOS ====================

@router.get("/reports/monthly", response_model=ExpenseMonthlyReport)
async def get_expense_monthly_report(
    month: int = Query(..., ge=1, le=12),
    year: int = Query(..., ge=2020, le=2100),
    session: AsyncSession = Depends(get_session),
    current_user=Depends(require_admin),
):
    """Reporte mensual de gastos"""
    query = (
        select(Expense)
        .options(
            selectinload(Expense.category),
            selectinload(Expense.subcategory),
        )
        .where(
            extract("month", Expense.expense_date) == month,
            extract("year", Expense.expense_date) == year,
            Expense.status != "cancelled",
        )
        .order_by(Expense.expense_date, Expense.id)
    )
    
    result = await session.execute(query)
    expenses = result.scalars().all()
    
    rows = []
    total_gastos = Decimal("0")
    por_categoria = {}
    por_metodo = {}
    presupuesto_usado = {}
    
    for e in expenses:
        cat_name = e.category.name if e.category else "Sin categoría"
        subcat_name = e.subcategory.name if e.subcategory else None
        
        rows.append(ExpenseReportRow(
            fecha=e.expense_date.strftime("%d/%m/%Y"),
            categoria=cat_name,
            subcategoria=subcat_name,
            descripcion=e.description,
            proveedor=e.vendor_name,
            metodo_pago=e.payment_method,
            monto=e.amount,
            estado=e.status,
        ))
        
        total_gastos += e.amount
        por_categoria[cat_name] = por_categoria.get(cat_name, Decimal("0")) + e.amount
        por_metodo[e.payment_method] = por_metodo.get(e.payment_method, Decimal("0")) + e.amount
        
        # Calcular uso de presupuesto
        if e.category and e.category.monthly_budget:
            if cat_name not in presupuesto_usado:
                presupuesto_usado[cat_name] = {
                    "presupuesto": float(e.category.monthly_budget),
                    "gastado": 0,
                    "porcentaje": 0,
                }
            presupuesto_usado[cat_name]["gastado"] += float(e.amount)
            presupuesto_usado[cat_name]["porcentaje"] = round(
                (presupuesto_usado[cat_name]["gastado"] / presupuesto_usado[cat_name]["presupuesto"]) * 100, 2
            )
    
    summary = ExpenseReportSummary(
        total_gastos=total_gastos,
        por_categoria=por_categoria,
        por_metodo_pago=por_metodo,
        cantidad_gastos=len(expenses),
        presupuesto_usado=presupuesto_usado,
    )
    
    return ExpenseMonthlyReport(
        church_name="Iglesia Comunidad Cristiana de Fe",
        month=month,
        year=year,
        period_label=f"{MONTHS_ES[month]} {year}",
        expenses=rows,
        summary=summary,
    )


@router.get("/reports/monthly/csv")
async def export_expenses_csv(
    month: int = Query(..., ge=1, le=12),
    year: int = Query(..., ge=2020, le=2100),
    session: AsyncSession = Depends(get_session),
    current_user=Depends(require_admin),
):
    """Exporta reporte de gastos en CSV"""
    report = await get_expense_monthly_report(month, year, session, current_user)
    
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Encabezado
    writer.writerow([f"REPORTE DE GASTOS - {report.period_label}"])
    writer.writerow([])
    writer.writerow(["FECHA", "CATEGORÍA", "SUBCATEGORÍA", "DESCRIPCIÓN", "PROVEEDOR", "MÉTODO PAGO", "MONTO", "ESTADO"])
    
    for row in report.expenses:
        writer.writerow([
            row.fecha,
            row.categoria,
            row.subcategoria or "",
            row.descripcion,
            row.proveedor or "",
            row.metodo_pago,
            f"${row.monto:,.2f}",
            row.estado,
        ])
    
    writer.writerow([])
    writer.writerow(["TOTAL GASTOS", "", "", "", "", "", f"${report.summary.total_gastos:,.2f}"])
    
    # Resumen por categoría
    writer.writerow([])
    writer.writerow(["RESUMEN POR CATEGORÍA"])
    for cat, amount in report.summary.por_categoria.items():
        writer.writerow([cat, f"${amount:,.2f}"])
    
    output.seek(0)
    filename = f"gastos_{MONTHS_ES[month].lower()}_{year}.csv"
    
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )


@router.get("/reports/summary")
async def get_expense_summary(
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    session: AsyncSession = Depends(get_session),
    current_user=Depends(require_admin),
):
    """Resumen de gastos para dashboard"""
    query = select(Expense).where(Expense.status != "cancelled")
    
    if start_date:
        query = query.where(Expense.expense_date >= start_date)
    if end_date:
        query = query.where(Expense.expense_date <= end_date)
    
    result = await session.execute(query)
    expenses = result.scalars().all()
    
    total = sum(e.amount for e in expenses)
    pending = sum(e.amount for e in expenses if e.status == "pending")
    approved = sum(e.amount for e in expenses if e.status == "approved")
    paid = sum(e.amount for e in expenses if e.status == "paid")
    
    return {
        "total": float(total),
        "pending": float(pending),
        "approved": float(approved),
        "paid": float(paid),
        "count": len(expenses),
    }


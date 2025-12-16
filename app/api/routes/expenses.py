"""
Rutas de gestión de gastos - Solo para admins del tenant
"""
from datetime import date
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.tenant import get_tenant_db
from app.core.deps import require_admin, get_current_user
from app.models.user import User

router = APIRouter(prefix="/expenses", tags=["expenses"])


# ============== Schemas ==============

class ExpenseCategoryCreate(BaseModel):
    name: str
    description: Optional[str] = None
    color: str = "#6b7280"


class ExpenseCategoryRead(BaseModel):
    id: int
    name: str
    description: Optional[str]
    color: str
    is_active: bool


class ExpenseCreate(BaseModel):
    description: str
    amount: float
    category_id: Optional[int] = None
    expense_date: date
    due_date: Optional[date] = None
    payment_method: Optional[str] = None
    receipt_number: Optional[str] = None
    vendor: Optional[str] = None
    notes: Optional[str] = None


class ExpenseRead(BaseModel):
    id: int
    description: str
    amount: float
    category_id: Optional[int]
    category_name: Optional[str] = None
    expense_date: date
    due_date: Optional[date]
    status: str
    payment_method: Optional[str]
    receipt_number: Optional[str]
    vendor: Optional[str]
    notes: Optional[str]
    created_by_id: Optional[int]
    approved_by_id: Optional[int]
    created_at: Optional[str]


# ============== Categorías de Gastos ==============

@router.get("/categories", response_model=list[ExpenseCategoryRead])
async def list_expense_categories(
    session: AsyncSession = Depends(get_tenant_db),
    current_user: User = Depends(require_admin)
):
    """Lista todas las categorías de gastos"""
    result = await session.execute(
        text("SELECT id, name, description, color, is_active FROM expense_categories WHERE is_active = TRUE ORDER BY name")
    )
    categories = result.fetchall()
    
    return [ExpenseCategoryRead(
        id=c.id,
        name=c.name,
        description=c.description,
        color=c.color,
        is_active=c.is_active
    ) for c in categories]


@router.post("/categories", response_model=ExpenseCategoryRead, status_code=status.HTTP_201_CREATED)
async def create_expense_category(
    data: ExpenseCategoryCreate,
    session: AsyncSession = Depends(get_tenant_db),
    current_user: User = Depends(require_admin)
):
    """Crea una nueva categoría de gastos"""
    result = await session.execute(
        text("""
            INSERT INTO expense_categories (name, description, color)
            VALUES (:name, :description, :color)
            RETURNING id, name, description, color, is_active
        """),
        {"name": data.name, "description": data.description, "color": data.color}
    )
    category = result.fetchone()
    await session.commit()
    
    return ExpenseCategoryRead(
        id=category.id,
        name=category.name,
        description=category.description,
        color=category.color,
        is_active=category.is_active
    )


@router.delete("/categories/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_expense_category(
    category_id: int,
    session: AsyncSession = Depends(get_tenant_db),
    current_user: User = Depends(require_admin)
):
    """Desactiva una categoría de gastos (soft delete)"""
    await session.execute(
        text("UPDATE expense_categories SET is_active = FALSE WHERE id = :id"),
        {"id": category_id}
    )
    await session.commit()
    return None


# ============== Gastos ==============

@router.get("", response_model=list[ExpenseRead])
async def list_expenses(
    status_filter: Optional[str] = None,
    category_id: Optional[int] = None,
    session: AsyncSession = Depends(get_tenant_db),
    current_user: User = Depends(require_admin)
):
    """Lista todos los gastos con filtros opcionales"""
    query = """
        SELECT e.id, e.description, e.amount, e.category_id, c.name as category_name,
               e.expense_date, e.due_date, e.status, e.payment_method, e.receipt_number,
               e.vendor, e.notes, e.created_by_id, e.approved_by_id, e.created_at
        FROM expenses e
        LEFT JOIN expense_categories c ON e.category_id = c.id
        WHERE 1=1
    """
    params = {}
    
    if status_filter:
        query += " AND e.status = :status"
        params["status"] = status_filter
    
    if category_id:
        query += " AND e.category_id = :category_id"
        params["category_id"] = category_id
    
    query += " ORDER BY e.expense_date DESC, e.created_at DESC"
    
    result = await session.execute(text(query), params)
    expenses = result.fetchall()
    
    return [ExpenseRead(
        id=e.id,
        description=e.description,
        amount=float(e.amount),
        category_id=e.category_id,
        category_name=e.category_name,
        expense_date=e.expense_date,
        due_date=e.due_date,
        status=e.status,
        payment_method=e.payment_method,
        receipt_number=e.receipt_number,
        vendor=e.vendor,
        notes=e.notes,
        created_by_id=e.created_by_id,
        approved_by_id=e.approved_by_id,
        created_at=e.created_at.isoformat() if e.created_at else None
    ) for e in expenses]


@router.post("", response_model=ExpenseRead, status_code=status.HTTP_201_CREATED)
async def create_expense(
    data: ExpenseCreate,
    session: AsyncSession = Depends(get_tenant_db),
    current_user: User = Depends(require_admin)
):
    """Crea un nuevo gasto"""
    result = await session.execute(
        text("""
            INSERT INTO expenses (description, amount, category_id, expense_date, due_date,
                payment_method, receipt_number, vendor, notes, created_by_id)
            VALUES (:description, :amount, :category_id, :expense_date, :due_date,
                :payment_method, :receipt_number, :vendor, :notes, :created_by_id)
            RETURNING id, description, amount, category_id, expense_date, due_date,
                status, payment_method, receipt_number, vendor, notes, created_by_id, 
                approved_by_id, created_at
        """),
        {
            "description": data.description,
            "amount": data.amount,
            "category_id": data.category_id,
            "expense_date": data.expense_date,
            "due_date": data.due_date,
            "payment_method": data.payment_method,
            "receipt_number": data.receipt_number,
            "vendor": data.vendor,
            "notes": data.notes,
            "created_by_id": current_user.id
        }
    )
    expense = result.fetchone()
    await session.commit()
    
    return ExpenseRead(
        id=expense.id,
        description=expense.description,
        amount=float(expense.amount),
        category_id=expense.category_id,
        category_name=None,
        expense_date=expense.expense_date,
        due_date=expense.due_date,
        status=expense.status,
        payment_method=expense.payment_method,
        receipt_number=expense.receipt_number,
        vendor=expense.vendor,
        notes=expense.notes,
        created_by_id=expense.created_by_id,
        approved_by_id=expense.approved_by_id,
        created_at=expense.created_at.isoformat() if expense.created_at else None
    )


@router.get("/{expense_id}", response_model=ExpenseRead)
async def get_expense(
    expense_id: int,
    session: AsyncSession = Depends(get_tenant_db),
    current_user: User = Depends(require_admin)
):
    """Obtiene un gasto por ID"""
    result = await session.execute(
        text("""
            SELECT e.id, e.description, e.amount, e.category_id, c.name as category_name,
                   e.expense_date, e.due_date, e.status, e.payment_method, e.receipt_number,
                   e.vendor, e.notes, e.created_by_id, e.approved_by_id, e.created_at
            FROM expenses e
            LEFT JOIN expense_categories c ON e.category_id = c.id
            WHERE e.id = :id
        """),
        {"id": expense_id}
    )
    expense = result.fetchone()
    
    if not expense:
        raise HTTPException(status_code=404, detail="Gasto no encontrado")
    
    return ExpenseRead(
        id=expense.id,
        description=expense.description,
        amount=float(expense.amount),
        category_id=expense.category_id,
        category_name=expense.category_name,
        expense_date=expense.expense_date,
        due_date=expense.due_date,
        status=expense.status,
        payment_method=expense.payment_method,
        receipt_number=expense.receipt_number,
        vendor=expense.vendor,
        notes=expense.notes,
        created_by_id=expense.created_by_id,
        approved_by_id=expense.approved_by_id,
        created_at=expense.created_at.isoformat() if expense.created_at else None
    )


@router.patch("/{expense_id}/approve")
async def approve_expense(
    expense_id: int,
    session: AsyncSession = Depends(get_tenant_db),
    current_user: User = Depends(require_admin)
):
    """Aprueba un gasto pendiente"""
    result = await session.execute(
        text("""
            UPDATE expenses 
            SET status = 'approved', approved_by_id = :approved_by, approved_at = NOW()
            WHERE id = :id AND status = 'pending'
            RETURNING id
        """),
        {"id": expense_id, "approved_by": current_user.id}
    )
    row = result.fetchone()
    await session.commit()
    
    if not row:
        raise HTTPException(status_code=404, detail="Gasto no encontrado o ya procesado")
    
    return {"message": "Gasto aprobado", "id": expense_id}


@router.patch("/{expense_id}/reject")
async def reject_expense(
    expense_id: int,
    session: AsyncSession = Depends(get_tenant_db),
    current_user: User = Depends(require_admin)
):
    """Rechaza un gasto pendiente"""
    result = await session.execute(
        text("""
            UPDATE expenses 
            SET status = 'rejected', approved_by_id = :approved_by, approved_at = NOW()
            WHERE id = :id AND status = 'pending'
            RETURNING id
        """),
        {"id": expense_id, "approved_by": current_user.id}
    )
    row = result.fetchone()
    await session.commit()
    
    if not row:
        raise HTTPException(status_code=404, detail="Gasto no encontrado o ya procesado")
    
    return {"message": "Gasto rechazado", "id": expense_id}


@router.patch("/{expense_id}/pay")
async def mark_expense_paid(
    expense_id: int,
    session: AsyncSession = Depends(get_tenant_db),
    current_user: User = Depends(require_admin)
):
    """Marca un gasto aprobado como pagado"""
    result = await session.execute(
        text("""
            UPDATE expenses 
            SET status = 'paid', paid_at = NOW()
            WHERE id = :id AND status = 'approved'
            RETURNING id
        """),
        {"id": expense_id}
    )
    row = result.fetchone()
    await session.commit()
    
    if not row:
        raise HTTPException(status_code=404, detail="Gasto no encontrado o no está aprobado")
    
    return {"message": "Gasto marcado como pagado", "id": expense_id}


@router.delete("/{expense_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_expense(
    expense_id: int,
    session: AsyncSession = Depends(get_tenant_db),
    current_user: User = Depends(require_admin)
):
    """Elimina un gasto (solo si está pendiente)"""
    result = await session.execute(
        text("DELETE FROM expenses WHERE id = :id AND status = 'pending' RETURNING id"),
        {"id": expense_id}
    )
    row = result.fetchone()
    await session.commit()
    
    if not row:
        raise HTTPException(status_code=400, detail="Solo se pueden eliminar gastos pendientes")
    
    return None


# ============== Resumen de Gastos ==============

@router.get("/summary/by-category")
async def get_expenses_by_category(
    year: Optional[int] = None,
    month: Optional[int] = None,
    session: AsyncSession = Depends(get_tenant_db),
    current_user: User = Depends(require_admin)
):
    """Obtiene resumen de gastos por categoría"""
    query = """
        SELECT c.name as category, c.color, SUM(e.amount) as total, COUNT(*) as count
        FROM expenses e
        LEFT JOIN expense_categories c ON e.category_id = c.id
        WHERE e.status IN ('approved', 'paid')
    """
    params = {}
    
    if year:
        query += " AND EXTRACT(YEAR FROM e.expense_date) = :year"
        params["year"] = year
    
    if month:
        query += " AND EXTRACT(MONTH FROM e.expense_date) = :month"
        params["month"] = month
    
    query += " GROUP BY c.id, c.name, c.color ORDER BY total DESC"
    
    result = await session.execute(text(query), params)
    rows = result.fetchall()
    
    return [
        {
            "category": r.category or "Sin categoría",
            "color": r.color or "#6b7280",
            "total": float(r.total) if r.total else 0,
            "count": r.count
        }
        for r in rows
    ]


@router.get("/summary/monthly")
async def get_monthly_expenses(
    year: Optional[int] = None,
    session: AsyncSession = Depends(get_tenant_db),
    current_user: User = Depends(require_admin)
):
    """Obtiene resumen mensual de gastos"""
    from datetime import datetime
    
    if not year:
        year = datetime.now().year
    
    result = await session.execute(
        text("""
            SELECT EXTRACT(MONTH FROM expense_date) as month, 
                   SUM(amount) as total, 
                   COUNT(*) as count
            FROM expenses
            WHERE EXTRACT(YEAR FROM expense_date) = :year
              AND status IN ('approved', 'paid')
            GROUP BY EXTRACT(MONTH FROM expense_date)
            ORDER BY month
        """),
        {"year": year}
    )
    rows = result.fetchall()
    
    months = {int(r.month): {"total": float(r.total), "count": r.count} for r in rows}
    
    return {
        "year": year,
        "months": [
            {
                "month": i,
                "total": months.get(i, {}).get("total", 0),
                "count": months.get(i, {}).get("count", 0)
            }
            for i in range(1, 13)
        ]
    }


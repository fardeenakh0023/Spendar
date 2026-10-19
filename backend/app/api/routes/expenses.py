from datetime import date

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.dependencies import get_csrf_protected_user, get_current_user
from app.core.database import get_db
from app.models import User
from app.schemas.expense import ExpenseCreate, ExpenseOut, ExpensePage, ExpenseUpdate
from app.services import expense_service

router = APIRouter(prefix="/expenses", tags=["expenses"])


@router.post("", response_model=ExpenseOut, status_code=201)
def create(data: ExpenseCreate, user: User = Depends(get_csrf_protected_user), db: Session = Depends(get_db)):
    return expense_service.create_expense(db, user.id, data)


@router.get("", response_model=ExpensePage)
def list_all(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    start_date: date | None = None,
    end_date: date | None = None,
    category_id: int | None = Query(None, gt=0),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    items, total = expense_service.list_expenses(db, user.id, page, page_size, start_date, end_date, category_id)
    return {"items": items, "total": total, "page": page, "page_size": page_size}


@router.get("/{expense_id}", response_model=ExpenseOut)
def get_one(expense_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return expense_service.get_expense(db, user.id, expense_id)


@router.patch("/{expense_id}", response_model=ExpenseOut)
def update(expense_id: int, data: ExpenseUpdate, user: User = Depends(get_csrf_protected_user),
           db: Session = Depends(get_db)):
    return expense_service.update_expense(db, user.id, expense_id, data)


@router.delete("/{expense_id}", status_code=204)
def delete(expense_id: int, user: User = Depends(get_csrf_protected_user), db: Session = Depends(get_db)):
    expense_service.delete_expense(db, user.id, expense_id)

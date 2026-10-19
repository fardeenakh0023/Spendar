from datetime import date

from sqlalchemy.orm import Session

from app.core.errors import AppError
from app.models import Expense
from app.repositories import category_repository, expense_repository
from app.schemas.expense import ExpenseCreate, ExpenseUpdate


def _require_own_category(db: Session, user_id: int, category_id: int) -> None:
    if category_repository.get_for_user(db, user_id, category_id) is None:
        raise AppError(422, "Selected category does not exist")


def _get_or_404(db: Session, user_id: int, expense_id: int) -> Expense:
    exp = expense_repository.get_for_user(db, user_id, expense_id)
    if exp is None:  # same answer for "missing" and "belongs to someone else"
        raise AppError(404, "Expense not found")
    return exp


def create_expense(db: Session, user_id: int, data: ExpenseCreate) -> Expense:
    _require_own_category(db, user_id, data.category_id)
    exp = expense_repository.create(db, user_id, **data.model_dump())
    db.commit()
    return exp


def get_expense(db: Session, user_id: int, expense_id: int) -> Expense:
    return _get_or_404(db, user_id, expense_id)


def list_expenses(
    db: Session, user_id: int, page: int, page_size: int,
    start: date | None, end: date | None, category_id: int | None,
):
    if start and end and start > end:
        raise AppError(422, "start_date must not be after end_date")
    return expense_repository.list_for_user(db, user_id, page, page_size, start, end, category_id)


def update_expense(db: Session, user_id: int, expense_id: int, data: ExpenseUpdate) -> Expense:
    exp = _get_or_404(db, user_id, expense_id)
    changes = data.model_dump(exclude_unset=True)
    if not changes:
        raise AppError(422, "No fields to update")
    for field in ("description", "amount", "category_id", "expense_date"):
        if field in changes and changes[field] is None:
            raise AppError(422, f"{field} cannot be empty")
    if "category_id" in changes:
        _require_own_category(db, user_id, changes["category_id"])
    for field, value in changes.items():
        setattr(exp, field, value)
    db.commit()
    db.refresh(exp)
    return exp


def delete_expense(db: Session, user_id: int, expense_id: int) -> None:
    exp = _get_or_404(db, user_id, expense_id)
    expense_repository.delete(db, exp)
    db.commit()

from datetime import date
from decimal import Decimal

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models import Category, Expense


def _filters(user_id: int, start: date | None, end: date | None, category_id: int | None = None):
    conds = [Expense.user_id == user_id]
    if start is not None:
        conds.append(Expense.expense_date >= start)
    if end is not None:
        conds.append(Expense.expense_date <= end)  # end date is inclusive
    if category_id is not None:
        conds.append(Expense.category_id == category_id)
    return conds


def get_for_user(db: Session, user_id: int, expense_id: int) -> Expense | None:
    return db.scalar(select(Expense).where(Expense.id == expense_id, Expense.user_id == user_id))


def list_for_user(
    db: Session, user_id: int, page: int, page_size: int,
    start: date | None = None, end: date | None = None, category_id: int | None = None,
) -> tuple[list[Expense], int]:
    conds = _filters(user_id, start, end, category_id)
    total = db.scalar(select(func.count()).select_from(Expense).where(*conds)) or 0
    stmt = (
        select(Expense).where(*conds)
        .order_by(Expense.expense_date.desc(), Expense.id.desc())
        .limit(page_size).offset((page - 1) * page_size)
    )
    return list(db.scalars(stmt).unique()), total


def create(db: Session, user_id: int, **fields) -> Expense:
    exp = Expense(user_id=user_id, **fields)
    db.add(exp)
    db.flush()
    db.refresh(exp)
    return exp


def delete(db: Session, expense: Expense) -> None:
    db.delete(expense)


def count_by_category(db: Session, user_id: int, category_id: int) -> int:
    return db.scalar(
        select(func.count()).select_from(Expense).where(Expense.user_id == user_id, Expense.category_id == category_id)
    ) or 0


def total_and_count(db: Session, user_id: int, start: date, end: date) -> tuple[Decimal, int]:
    row = db.execute(
        select(func.coalesce(func.sum(Expense.amount), 0), func.count(Expense.id)).where(*_filters(user_id, start, end))
    ).one()
    return Decimal(str(row[0])), row[1]


def category_totals(db: Session, user_id: int, start: date, end: date):
    stmt = (
        select(Category.id, Category.name, func.sum(Expense.amount).label("total"), func.count(Expense.id))
        .join(Category, Category.id == Expense.category_id)
        .where(*_filters(user_id, start, end))
        .group_by(Category.id, Category.name)
        .order_by(func.sum(Expense.amount).desc())
    )
    return db.execute(stmt).all()

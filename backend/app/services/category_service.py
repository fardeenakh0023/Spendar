from sqlalchemy.orm import Session

from app.core.errors import AppError
from app.models import Category
from app.repositories import category_repository, expense_repository

DEFAULT_CATEGORIES = ["Food", "Transport", "Bills", "Shopping", "Entertainment", "Recharge", "Others"]


def seed_defaults(db: Session, user_id: int) -> None:
    for name in DEFAULT_CATEGORIES:
        category_repository.create(db, user_id, name)


def list_categories(db: Session, user_id: int) -> list[Category]:
    return category_repository.list_for_user(db, user_id)


def _get_or_404(db: Session, user_id: int, category_id: int) -> Category:
    cat = category_repository.get_for_user(db, user_id, category_id)
    if cat is None:
        raise AppError(404, "Category not found")
    return cat


def create_category(db: Session, user_id: int, name: str) -> Category:
    if category_repository.get_by_name(db, user_id, name):
        raise AppError(409, "You already have a category with this name")
    cat = category_repository.create(db, user_id, name)
    db.commit()
    return cat


def rename_category(db: Session, user_id: int, category_id: int, name: str) -> Category:
    cat = _get_or_404(db, user_id, category_id)
    existing = category_repository.get_by_name(db, user_id, name)
    if existing and existing.id != cat.id:
        raise AppError(409, "You already have a category with this name")
    cat.name = name
    db.commit()
    return cat


def delete_category(db: Session, user_id: int, category_id: int) -> None:
    cat = _get_or_404(db, user_id, category_id)
    used = expense_repository.count_by_category(db, user_id, cat.id)
    if used:
        raise AppError(409, f"This category is used by {used} expense(s). Move or delete them first.")
    category_repository.delete(db, cat)
    db.commit()

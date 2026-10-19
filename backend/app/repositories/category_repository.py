from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Category


def list_for_user(db: Session, user_id: int) -> list[Category]:
    return list(db.scalars(select(Category).where(Category.user_id == user_id).order_by(Category.name)))


def get_for_user(db: Session, user_id: int, category_id: int) -> Category | None:
    return db.scalar(select(Category).where(Category.id == category_id, Category.user_id == user_id))


def get_by_name(db: Session, user_id: int, name: str) -> Category | None:
    return db.scalar(select(Category).where(Category.user_id == user_id, Category.name == name))


def create(db: Session, user_id: int, name: str) -> Category:
    cat = Category(user_id=user_id, name=name)
    db.add(cat)
    db.flush()
    return cat


def delete(db: Session, category: Category) -> None:
    db.delete(category)

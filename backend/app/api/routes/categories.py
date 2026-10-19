from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.dependencies import get_csrf_protected_user, get_current_user
from app.core.database import get_db
from app.models import User
from app.schemas.category import CategoryCreate, CategoryOut, CategoryUpdate
from app.services import category_service

router = APIRouter(prefix="/categories", tags=["categories"])


@router.post("", response_model=CategoryOut, status_code=201)
def create(data: CategoryCreate, user: User = Depends(get_csrf_protected_user), db: Session = Depends(get_db)):
    return category_service.create_category(db, user.id, data.name)


@router.get("", response_model=list[CategoryOut])
def list_all(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return category_service.list_categories(db, user.id)


@router.patch("/{category_id}", response_model=CategoryOut)
def rename(category_id: int, data: CategoryUpdate, user: User = Depends(get_csrf_protected_user),
           db: Session = Depends(get_db)):
    return category_service.rename_category(db, user.id, category_id, data.name)


@router.delete("/{category_id}", status_code=204)
def delete(category_id: int, user: User = Depends(get_csrf_protected_user), db: Session = Depends(get_db)):
    category_service.delete_category(db, user.id, category_id)

from datetime import date

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user
from app.core.database import get_db
from app.models import User
from app.schemas.expense import BreakdownOut, HistoryOut, SummaryOut
from app.services import dashboard_service
from app.services.dashboard_service import DateRange

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


def period_range(
    period: str = Query("month", description="week | month | year | custom"),
    ref_date: date | None = Query(None, description="Any date inside the wanted week/month/year"),
    start_date: date | None = None,
    end_date: date | None = None,
) -> DateRange:
    return dashboard_service.resolve_period(period, ref_date, start_date, end_date)


@router.get("/summary", response_model=SummaryOut)
def summary(rng: DateRange = Depends(period_range), user: User = Depends(get_current_user),
            db: Session = Depends(get_db)):
    return dashboard_service.summary(db, user.id, rng)


@router.get("/category-breakdown", response_model=BreakdownOut)
def category_breakdown(rng: DateRange = Depends(period_range), user: User = Depends(get_current_user),
                       db: Session = Depends(get_db)):
    return dashboard_service.category_breakdown(db, user.id, rng)


@router.get("/history", response_model=HistoryOut)
def history(
    rng: DateRange = Depends(period_range),
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return dashboard_service.history(db, user.id, rng, page, page_size)

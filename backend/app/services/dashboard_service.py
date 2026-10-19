import calendar
from dataclasses import dataclass
from datetime import date, timedelta
from decimal import ROUND_HALF_UP, Decimal

from sqlalchemy.orm import Session

from app.core.errors import AppError
from app.repositories import expense_repository

TWO_PLACES = Decimal("0.01")


@dataclass(frozen=True)
class DateRange:
    period: str
    start: date  # inclusive
    end: date    # inclusive

    @property
    def days(self) -> int:
        return (self.end - self.start).days + 1


def resolve_period(period: str, ref_date: date | None, start: date | None, end: date | None) -> DateRange:
    """Turn a period name into inclusive calendar boundaries.

    week  = Monday..Sunday containing ref_date
    month = 1st..last day of ref_date's month
    year  = 1 Jan..31 Dec of ref_date's year
    custom = start..end exactly as given
    """
    ref = ref_date or date.today()
    if period == "week":
        monday = ref - timedelta(days=ref.weekday())
        return DateRange("week", monday, monday + timedelta(days=6))
    if period == "month":
        last = calendar.monthrange(ref.year, ref.month)[1]
        return DateRange("month", ref.replace(day=1), ref.replace(day=last))
    if period == "year":
        return DateRange("year", date(ref.year, 1, 1), date(ref.year, 12, 31))
    if period == "custom":
        if start is None or end is None:
            raise AppError(422, "start_date and end_date are required for a custom period")
        if start > end:
            raise AppError(422, "start_date must not be after end_date")
        return DateRange("custom", start, end)
    raise AppError(422, "period must be one of: week, month, year, custom")


def _period_dict(rng: DateRange) -> dict:
    return {"period": rng.period, "start_date": rng.start, "end_date": rng.end}


def summary(db: Session, user_id: int, rng: DateRange) -> dict:
    total, count = expense_repository.total_and_count(db, user_id, rng.start, rng.end)
    rows = expense_repository.category_totals(db, user_id, rng.start, rng.end)
    return {
        "period": _period_dict(rng),
        "total_spent": total,
        "expense_count": count,
        "average_per_day": (total / rng.days).quantize(TWO_PLACES, rounding=ROUND_HALF_UP),
        "top_category": rows[0][1] if rows else None,
    }


def category_breakdown(db: Session, user_id: int, rng: DateRange) -> dict:
    total, _ = expense_repository.total_and_count(db, user_id, rng.start, rng.end)
    rows = expense_repository.category_totals(db, user_id, rng.start, rng.end)
    cats = []
    for cat_id, name, cat_total, count in rows:
        cat_total = Decimal(str(cat_total))
        pct = float((cat_total / total * 100).quantize(Decimal("0.1"))) if total else 0.0
        cats.append({"category_id": cat_id, "category_name": name, "total": cat_total, "count": count, "percentage": pct})
    return {"period": _period_dict(rng), "total_spent": total, "categories": cats}


def history(db: Session, user_id: int, rng: DateRange, page: int, page_size: int) -> dict:
    total, count = expense_repository.total_and_count(db, user_id, rng.start, rng.end)
    items, _ = expense_repository.list_for_user(db, user_id, page, page_size, rng.start, rng.end)
    return {
        "period": _period_dict(rng), "total_spent": total, "expense_count": count,
        "items": items, "page": page, "page_size": page_size,
    }

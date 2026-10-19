from datetime import date
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator

Money = Decimal


def _clean_description(v: str) -> str:
    v = " ".join(v.split())
    if not v:
        raise ValueError("must not be empty")
    return v


class ExpenseCreate(BaseModel):
    description: str = Field(max_length=255)
    amount: Decimal = Field(gt=0, max_digits=12, decimal_places=2)
    category_id: int = Field(gt=0)
    expense_date: date

    _clean = field_validator("description")(_clean_description)


class ExpenseUpdate(BaseModel):
    description: Optional[str] = Field(default=None, max_length=255)
    amount: Optional[Decimal] = Field(default=None, gt=0, max_digits=12, decimal_places=2)
    category_id: Optional[int] = Field(default=None, gt=0)
    expense_date: Optional[date] = None

    @field_validator("description")
    @classmethod
    def clean(cls, v):
        return None if v is None else _clean_description(v)


class ExpenseOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    description: str
    amount: Decimal
    category_id: int
    category_name: str
    expense_date: date


class ExpensePage(BaseModel):
    items: list[ExpenseOut]
    total: int
    page: int
    page_size: int


class PeriodOut(BaseModel):
    period: str
    start_date: date
    end_date: date


class SummaryOut(BaseModel):
    period: PeriodOut
    total_spent: Decimal
    expense_count: int
    average_per_day: Decimal
    top_category: Optional[str]


class CategoryTotal(BaseModel):
    category_id: int
    category_name: str
    total: Decimal
    count: int
    percentage: float


class BreakdownOut(BaseModel):
    period: PeriodOut
    total_spent: Decimal
    categories: list[CategoryTotal]


class HistoryOut(BaseModel):
    period: PeriodOut
    total_spent: Decimal
    expense_count: int
    items: list[ExpenseOut]
    page: int
    page_size: int

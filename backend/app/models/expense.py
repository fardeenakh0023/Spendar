from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import Date, DateTime, ForeignKey, Index, Numeric, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Expense(Base):
    __tablename__ = "expenses"
    __table_args__ = (Index("ix_expenses_user_date", "user_id", "expense_date"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    # RESTRICT: a category that still has expenses can never be deleted by accident.
    category_id: Mapped[int] = mapped_column(
        ForeignKey("categories.id", ondelete="RESTRICT"), index=True, nullable=False
    )
    description: Mapped[str] = mapped_column(String(255), nullable=False)
    amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    expense_date: Mapped[date] = mapped_column(Date, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)

    category = relationship("Category", lazy="joined")

    @property
    def category_name(self) -> str:
        return self.category.name

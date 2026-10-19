"""initial schema: users, sessions, categories, expenses

Revision ID: 0001
Revises:
"""
from alembic import op
import sqlalchemy as sa

revision = "0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("username", sa.String(30), nullable=False),
        sa.Column("email", sa.String(255), nullable=False),
        sa.Column("hashed_password", sa.String(255), nullable=False),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.UniqueConstraint("username"),
        sa.UniqueConstraint("email"),
        mysql_charset="utf8mb4",
    )
    op.create_table(
        "user_sessions",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("token_hash", sa.String(64), nullable=False),
        sa.Column("csrf_token", sa.String(64), nullable=False),
        sa.Column("expires_at", sa.DateTime(), nullable=False),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.UniqueConstraint("token_hash"),
        mysql_charset="utf8mb4",
    )
    op.create_index("ix_user_sessions_user_id", "user_sessions", ["user_id"])
    op.create_table(
        "categories",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("name", sa.String(50), nullable=False),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.UniqueConstraint("user_id", "name", name="uq_category_user_name"),
        mysql_charset="utf8mb4",
    )
    op.create_index("ix_categories_user_id", "categories", ["user_id"])
    op.create_table(
        "expenses",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("category_id", sa.Integer(), sa.ForeignKey("categories.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("description", sa.String(255), nullable=False),
        sa.Column("amount", sa.Numeric(12, 2), nullable=False),
        sa.Column("expense_date", sa.Date(), nullable=False),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
        mysql_charset="utf8mb4",
    )
    op.create_index("ix_expenses_category_id", "expenses", ["category_id"])
    op.create_index("ix_expenses_user_date", "expenses", ["user_id", "expense_date"])


def downgrade() -> None:
    op.drop_table("expenses")
    op.drop_table("categories")
    op.drop_table("user_sessions")
    op.drop_table("users")

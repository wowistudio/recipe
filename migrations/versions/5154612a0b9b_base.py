"""base

Revision ID: 5154612a0b9b
Revises: 
Create Date: 2026-03-07 14:46:51.800657

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from recipe.schemas._base import utc_now_naive
from sqlalchemy import text

# revision identifiers, used by Alembic.
revision: str = '5154612a0b9b'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("CREATE EXTENSION IF NOT EXISTS \"uuid-ossp\";")


    op.create_table(
        "recipes",
        sa.Column("id", sa.UUID(), nullable=False, server_default=text("uuid_generate_v4()"), primary_key=True),
        sa.Column("vegetarian", sa.Boolean(), nullable=False, default=False),
        sa.Column("servings", sa.Integer(), nullable=False, default=1),
        sa.Column("instructions", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False, default=utc_now_naive()),
        sa.Column("modified_at", sa.DateTime(), nullable=False, default=utc_now_naive(), onupdate=utc_now_naive()),
    )

    op.create_table("ingredients",
        sa.Column("id", sa.UUID(), nullable=False, server_default=text("uuid_generate_v4()"), primary_key=True),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("unit", sa.String(length=255), nullable=False),
        sa.Column("quantity", sa.Integer(), nullable=False),
        sa.Column("recipe_id", sa.UUID(), sa.ForeignKey("recipes.id"), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False, default=utc_now_naive()),
        sa.Column("modified_at", sa.DateTime(), nullable=False, default=utc_now_naive(), onupdate=utc_now_naive()),
    )


def downgrade() -> None:
    op.drop_table("ingredients")
    op.drop_table("recipes")
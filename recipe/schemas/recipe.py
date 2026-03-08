from typing import TYPE_CHECKING
from uuid import UUID as TUUID
from uuid import uuid4

from sqlalchemy import UUID, Boolean, Integer, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from recipe.schemas._base import Base

if TYPE_CHECKING:
    from recipe.schemas.ingredient import Ingredient


class Recipe(Base):
    __tablename__ = "recipes"

    id: Mapped[TUUID] = mapped_column(UUID, primary_key=True, default=uuid4)
    vegetarian: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    servings: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    instructions: Mapped[str] = mapped_column(Text, nullable=False)

    # relation
    ingredients: Mapped[list["Ingredient"]] = relationship(
        "Ingredient",
        back_populates="recipe",
        lazy="noload",
        cascade="all, delete-orphan",
    )

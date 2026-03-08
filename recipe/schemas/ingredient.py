from typing import TYPE_CHECKING
from uuid import UUID as TUUID
from uuid import uuid4

from sqlalchemy import UUID, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from recipe.schemas._base import Base

if TYPE_CHECKING:
    from recipe.schemas.recipe import Recipe


class Ingredient(Base):
    __tablename__ = "ingredients"

    id: Mapped[TUUID] = mapped_column(UUID, primary_key=True, default=uuid4)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    unit: Mapped[str] = mapped_column(String(255), nullable=False)
    quantity: Mapped[float] = mapped_column(Integer, nullable=False)
    recipe_id: Mapped[TUUID] = mapped_column(
        UUID, ForeignKey("recipes.id"), nullable=False
    )

    # relation
    recipe: Mapped["Recipe"] = relationship(
        "Recipe",
        back_populates="ingredients",
        lazy="noload",
    )

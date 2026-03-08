from uuid import UUID

from pydantic import BaseModel, ConfigDict


class IngredientCreate(BaseModel):
    name: str
    unit: str
    quantity: int


class IngredientUpdate(BaseModel):
    name: str | None = None
    unit: str | None = None
    quantity: int | None = None


class Ingredient(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
    unit: str
    quantity: int

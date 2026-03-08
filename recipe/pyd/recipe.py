from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from recipe.pyd.ingredient import Ingredient, IngredientCreate


class RecipeFilter(BaseModel):
    """Filter for listing recipes. Use via get_recipe_filters dependency as query params."""

    vegetarian: bool | None = None
    servings: int | None = None
    include_ingredients: list[str] = Field(default_factory=list)
    exclude_ingredients: list[str] = Field(default_factory=list)
    instructions_search: str | None = None


class RecipeCreate(BaseModel):
    vegetarian: bool
    servings: int
    instructions: str
    ingredients: list[IngredientCreate] = Field(default_factory=list)


class RecipeUpdate(BaseModel):
    vegetarian: bool | None = None
    servings: int | None = None
    instructions: str | None = None
    ingredients: list[IngredientCreate] | None = None


class Recipe(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    vegetarian: bool
    servings: int
    instructions: str
    ingredients: list[Ingredient] = Field(default_factory=list)

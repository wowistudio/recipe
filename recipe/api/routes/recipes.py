from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from recipe import crud
from recipe.api.deps.get_session import get_db_session
from recipe.api.deps.recipe_filters import get_recipe_filters
from recipe.pyd.recipe import Recipe, RecipeCreate, RecipeFilter, RecipeUpdate

router = APIRouter(tags=["recipes"])


@router.post(
    "/",
    response_model=Recipe,
    status_code=200,
    description="""Create a new recipe.
    """,
    responses={
        200: {"description": "Recipe created successfully"},
        422: {"description": "Invalid recipe data"},
    },
)
async def create_recipe(
    session: Annotated[AsyncSession, Depends(get_db_session)],
    recipe: RecipeCreate,
):
    return await crud.Recipe.create(session, data=recipe)


@router.get(
    "/{recipe_id}",
    response_model=Recipe,
    description="Get a recipe by ID",
    responses={
        200: {"description": "Recipe found"},
        404: {"description": "Recipe not found"},
    },
)
async def get_recipe(
    session: Annotated[AsyncSession, Depends(get_db_session)],
    recipe_id: UUID,
):
    return await crud.Recipe.get_or_404(session, recipe_id)


@router.put(
    "/{recipe_id}",
    response_model=Recipe,
    description="Update an existing recipe by ID",
    responses={
        200: {"description": "Recipe updated successfully"},
        404: {"description": "Recipe not found"},
        422: {"description": "Invalid recipe data"},
    },
)
async def update_recipe(
    session: Annotated[AsyncSession, Depends(get_db_session)],
    recipe_id: UUID,
    recipe: RecipeUpdate,
):
    recipe_obj = await crud.Recipe.get_or_404(session, recipe_id)
    return await crud.Recipe.update(session, db_obj=recipe_obj, data=recipe)


@router.delete(
    "/{recipe_id}",
    status_code=200,
    description="Delete a recipe by ID. Returns 200 on success. Returns 404 if the recipe does not exist.",
    responses={
        200: {"description": "Recipe deleted"},
        404: {"description": "Recipe not found"},
    },
)
async def delete_recipe(
    session: Annotated[AsyncSession, Depends(get_db_session)],
    recipe_id: UUID,
):
    await crud.Recipe.remove(session, id=recipe_id)


@router.get(
    "/",
    response_model=list[Recipe],
    summary="List recipes",
    description="""
        List recipes with optional filters 
        Query parameters: vegetarian, servings, include_ingredients, exclude_ingredients, instructions_search
    """,
    responses={
        200: {"description": "List of recipes"},
        422: {"description": "Invalid filter data"},
    },
)
async def list_recipes(
    session: Annotated[AsyncSession, Depends(get_db_session)],
    filters: Annotated[RecipeFilter, Depends(get_recipe_filters)],
):
    return await crud.Recipe.list(session, filters=filters)

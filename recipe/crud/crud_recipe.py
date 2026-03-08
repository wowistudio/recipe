from __future__ import annotations

from uuid import UUID

from sqlalchemy import delete, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlalchemy.sql.elements import ColumnElement

from recipe import schemas
from recipe.crud._base_public import CrudPublic
from recipe.db.packet import Packet
from recipe.pyd.recipe import Recipe as RecipePyd
from recipe.pyd.recipe import RecipeCreate, RecipeFilter, RecipeUpdate
from recipe.schemas.ingredient import Ingredient


class CrudRecipe(CrudPublic[schemas.Recipe, RecipeCreate, RecipeUpdate]):
    async def update(
        self,
        session: AsyncSession,
        *,
        db_obj: schemas.Recipe,
        data: RecipeUpdate,
    ) -> RecipePyd:
        async with Packet(session) as packet:
            update_data = data.model_dump(exclude_unset=True)
            ingredients_data = update_data.pop("ingredients", None)

            for field, value in update_data.items():
                setattr(db_obj, field, value)

            if ingredients_data is not None:
                db_obj.ingredients.clear()
                db_obj.ingredients.extend(
                    schemas.Ingredient(**ing, recipe_id=db_obj.id)
                    for ing in ingredients_data
                )

            packet.session.add(db_obj)
            await packet.session.flush()

            return RecipePyd.model_validate(db_obj)

    async def get(self, session: AsyncSession, id: UUID) -> schemas.Recipe | None:
        result = await session.execute(
            select(schemas.Recipe)
            .where(schemas.Recipe.id == id)
            .options(selectinload(schemas.Recipe.ingredients))
        )
        return result.unique().scalar_one_or_none()

    async def remove(
        self,
        session: AsyncSession,
        *,
        id: UUID,
        packet: Packet | None = None,
    ) -> schemas.Recipe | None:
        await session.execute(delete(Ingredient).where(Ingredient.recipe_id == id))
        return await super().remove(session, id=id, packet=packet)

    async def create(
        self,
        session: AsyncSession,
        *,
        data: RecipeCreate,
    ) -> RecipePyd:
        async with Packet(session) as packet:
            ingredients_data = data.ingredients
            recipe = data.model_dump(exclude_unset=True, exclude={"ingredients"})

            obj = self.model.from_dict(recipe)
            obj.ingredients = [
                schemas.Ingredient(**ing.model_dump(), recipe_id=obj.id)
                for ing in ingredients_data
            ]
            packet.session.add(obj)
            await session.flush()

            return RecipePyd.model_validate(obj)

    async def list(
        self,
        session: AsyncSession,
        *,
        filters: RecipeFilter | None = None,
        **kwargs,
    ) -> list[schemas.Recipe]:
        return await super().list(
            session, filters=self._build_filters(filters), **kwargs
        )

    def _build_filters(self, f: RecipeFilter | None) -> list[ColumnElement]:
        if not f:
            return []

        clauses: list[ColumnElement] = []

        if f.vegetarian is not None:
            clauses.append(schemas.Recipe.vegetarian == f.vegetarian)

        if f.servings is not None:
            clauses.append(schemas.Recipe.servings == f.servings)
        if f.include_ingredients:
            subq = select(Ingredient.recipe_id).where(
                or_(*[Ingredient.name.ilike(name) for name in f.include_ingredients])
            )
            clauses.append(schemas.Recipe.id.in_(subq))

        if f.exclude_ingredients:
            subq = select(Ingredient.recipe_id).where(
                or_(*[Ingredient.name.ilike(name) for name in f.exclude_ingredients])
            )
            clauses.append(schemas.Recipe.id.notin_(subq))

        if f.instructions_search:
            clauses.append(
                func.to_tsvector("english", schemas.Recipe.instructions).op("@@")(
                    func.websearch_to_tsquery("english", f.instructions_search)
                )
            )
        return clauses


Recipe = CrudRecipe(schemas.Recipe)

from fastapi import Query

from recipe.pyd.recipe import RecipeFilter


def get_recipe_filters(
    vegetarian: bool | None = Query(None, description="Filter by vegetarian"),
    servings: int | None = Query(None, description="Filter by number of servings"),
    include_ingredients: list[str] = Query(
        default=[], description="Recipes that include any of these ingredients"
    ),
    exclude_ingredients: list[str] = Query(
        default=[], description="Recipes that exclude any of these ingredients"
    ),
    instructions_search: str | None = Query(
        None, description="Full-text search in instructions"
    ),
) -> RecipeFilter:
    return RecipeFilter(
        vegetarian=vegetarian,
        servings=servings,
        include_ingredients=include_ingredients,
        exclude_ingredients=exclude_ingredients,
        instructions_search=instructions_search,
    )

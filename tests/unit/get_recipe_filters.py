from recipe.api.deps.recipe_filters import get_recipe_filters


def test_get_recipe_filters_default():
    filters = get_recipe_filters()
    assert filters.vegetarian is None
    assert filters.servings is None
    assert filters.include_ingredients == []
    assert filters.exclude_ingredients == []
    assert filters.instructions_search is None


def test_get_recipe_filters():
    filters = get_recipe_filters(
        vegetarian=True,
        servings=2,
        include_ingredients=["chicken"],
        exclude_ingredients=["chicken"],
        instructions_search="cook",
    )

    assert filters.vegetarian is True
    assert filters.servings == 2
    assert filters.include_ingredients == ["chicken"]
    assert filters.exclude_ingredients == ["chicken"]
    assert filters.instructions_search == "cook"

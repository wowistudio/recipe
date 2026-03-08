import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient

from recipe.api.build import build
from recipe.pyd.ingredient import IngredientCreate
from recipe.pyd.recipe import RecipeCreate

app = build()

apiBase = "/api/recipes"


@pytest_asyncio.fixture
async def client():
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        yield ac


async def create_recipe(client, **kwargs) -> dict:
    defaults = dict(
        vegetarian=True,
        servings=2,
        instructions="Mix and bake.",
        ingredients=[IngredientCreate(name="flour", unit="g", quantity=200)],
    )
    defaults.update(kwargs)
    payload = RecipeCreate(**defaults)
    resp = await client.post(f"{apiBase}/", json=payload.model_dump())
    return resp.json()


async def delete_recipe(client, recipe_id: str):
    await client.delete(f"{apiBase}/{recipe_id}")


@pytest_asyncio.fixture
async def veggie(client):
    r = await create_recipe(
        client, vegetarian=True, servings=2, instructions="Boil water."
    )
    yield r
    await delete_recipe(client, r["id"])


@pytest_asyncio.fixture
async def meat(client):
    r = await create_recipe(
        client,
        vegetarian=False,
        servings=4,
        instructions="Grill the chicken.",
        ingredients=[IngredientCreate(name="chicken", unit="g", quantity=500)],
    )
    yield r
    await delete_recipe(client, r["id"])


@pytest_asyncio.fixture
async def recipes(client, veggie, meat):
    yield {"veggie": veggie, "meat": meat}


@pytest.mark.asyncio
async def test_filter_vegetarian(client, recipes):
    """
    Test that a filter for vegetarian returns the veggie recipe.
    """
    resp = await client.get(f"{apiBase}/", params={"vegetarian": 1})
    assert resp.status_code == 200
    data = resp.json()

    ids = [r["id"] for r in data]
    assert recipes["veggie"]["id"] in ids
    assert recipes["meat"]["id"] not in ids


@pytest.mark.asyncio
async def test_filter_non_vegetarian(client, recipes):
    """
    Test that a filter for non-vegetarian returns the meat recipe.
    """
    resp = await client.get(f"{apiBase}/", params={"vegetarian": 0})
    assert resp.status_code == 200
    data = resp.json()

    ids = [r["id"] for r in data]
    assert recipes["meat"]["id"] in ids
    assert recipes["veggie"]["id"] not in ids


@pytest.mark.asyncio
async def test_filter_servings(client, recipes):
    """
    Test that a filter for 4 servings returns the meat recipe.
    """
    resp = await client.get(f"{apiBase}/", params={"servings": 4})
    assert resp.status_code == 200
    data = resp.json()

    ids = [r["id"] for r in data]
    assert recipes["meat"]["id"] in ids
    assert recipes["veggie"]["id"] not in ids


@pytest.mark.asyncio
async def test_filter_include_ingredients(client, recipes):
    """
    Test that a filter for "chicken" returns the meat recipe with "chicken" in the ingredients.
    """
    resp = await client.get(f"{apiBase}/", params={"include_ingredients": "chicken"})
    assert resp.status_code == 200
    data = resp.json()

    ids = [r["id"] for r in data]
    assert recipes["meat"]["id"] in ids
    assert recipes["veggie"]["id"] not in ids


@pytest.mark.asyncio
async def test_filter_exclude_ingredients(client, recipes):
    """
    Test that a filter for "chicken" returns the veggie recipe with "chicken" in the ingredients.
    The meat recipe should not be returned.
    """
    resp = await client.get(f"{apiBase}/", params={"exclude_ingredients": ["chicken"]})
    assert resp.status_code == 200
    data = resp.json()

    ids = [r["id"] for r in data]
    assert recipes["veggie"]["id"] in ids
    assert recipes["meat"]["id"] not in ids


@pytest.mark.asyncio
async def test_filter_instructions_search(client, recipes):
    """
    Test that a filter for "chicken" returns the meat recipe with "chicken" in the instructions.
    """
    resp = await client.get(f"{apiBase}/", params={"instructions_search": "chicken"})
    assert resp.status_code == 200
    data = resp.json()

    ids = [r["id"] for r in data]
    assert recipes["meat"]["id"] in ids
    assert recipes["veggie"]["id"] not in ids


@pytest.mark.asyncio
async def test_filter_instructions_search_related(client, recipes):
    """
    Test that a related search for "boil" (in this case, "boiling")
    returns the veggie recipe with "boil" in the instructions.
    """
    resp = await client.get(f"{apiBase}/", params={"instructions_search": "boiling"})
    assert resp.status_code == 200
    data = resp.json()
    ids = [r["id"] for r in data]
    assert recipes["veggie"]["id"] in ids
    assert recipes["meat"]["id"] not in ids


@pytest.mark.asyncio
async def test_no_filters_returns_all(client, recipes):
    """
    Test that no filters returns all recipes.
    """
    resp = await client.get(f"{apiBase}/")
    assert resp.status_code == 200
    data = resp.json()

    ids = [r["id"] for r in data]
    assert recipes["veggie"]["id"] in ids
    assert recipes["meat"]["id"] in ids

@pytest.mark.asyncio
async def test_invalid_filter_returns_422(client):
    """
    Test that an invalid filter returns a 422 error.
    """
    resp = await client.get(f"{apiBase}/", params={"servings": "invalid"})
    assert resp.status_code == 422
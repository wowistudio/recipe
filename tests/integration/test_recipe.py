import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient

from recipe.api.build import build
from recipe.pyd.ingredient import IngredientCreate
from recipe.pyd.recipe import RecipeCreate

app = build()

apiBase = "/api/recipes"
payload = RecipeCreate(
    vegetarian=True,
    servings=2,
    instructions="Mix and bake.",
    ingredients=[IngredientCreate(name="flour", unit="g", quantity=200)],
)


@pytest_asyncio.fixture
async def client():
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        yield ac


@pytest_asyncio.fixture
async def recipe(client):
    resp = await client.post(f"{apiBase}/", json=payload.model_dump())
    data = resp.json()
    yield data
    await client.delete(f"{apiBase}/{data['id']}")


@pytest.mark.asyncio
async def test_create_recipe(client):
    """
    Test that a recipe can be created and returns the correct data.
    """
    resp = await client.post(f"{apiBase}/", json=payload.model_dump())
    assert resp.status_code == 200
    data = resp.json()
    assert RecipeCreate(**data) == payload
    assert data["id"] is not None
    assert data["ingredients"][0]["id"] is not None
    await client.delete(f"{apiBase}/{data['id']}")


@pytest.mark.asyncio
async def test_get_recipe(client, recipe):
    """
    Test that a recipe can be retrieved and returns the correct data.
    """
    resp = await client.get(f"{apiBase}/{recipe['id']}")
    assert resp.status_code == 200
    data = resp.json()
    assert data["id"] == recipe["id"]
    assert data["vegetarian"] == recipe["vegetarian"]
    assert data["ingredients"] == recipe["ingredients"]


@pytest.mark.asyncio
async def test_update_recipe(client, recipe):
    """
    Test that a recipe and ingredients can be updated and returns the correct data.
    """
    resp = await client.put(f"{apiBase}/{recipe['id']}", json={"servings": 4, "ingredients": [{"name": "sugar", "unit": "g", "quantity": 100}]})
    assert resp.status_code == 200
    data = resp.json()
    assert data["servings"] == 4
    assert data["ingredients"][0]["name"] == "sugar"


@pytest.mark.asyncio
async def test_delete_recipe(client, recipe):
    """
    Test that a recipe can be deleted
    """
    resp = await client.delete(f"{apiBase}/{recipe['id']}")
    assert resp.status_code == 200
    get_resp = await client.get(f"{apiBase}/{recipe['id']}")
    assert get_resp.status_code == 404

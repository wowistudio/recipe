# Recipe

## Getting started

```shell
# run postgres
docker compose up -d

# sync packages (with uv)
uv sync

# run migrations
uv run alembic upgrade head

# run tests
uv run pytest

# start app
chmod +x ./bin/start.sh
./bin/start.sh

# (optional) POST recipe
curl --location 'localhost:8000/api/recipes/' \
--header 'Content-Type: application/json' \
--data '{
    "servings": 5,
    "instructions": "",
    "vegetarian": true,
    "ingredients": [
        {
            "name": "salmon",
            "unit": "kg",
            "quantity": 50
        }
    ]
}'
```

## Rest Documentation

See `openapi.json`

## Architectural choices
- Sqlalchemy with async connection pool to limit number of connections to db
- Separation of orm & api contracts (sqlachemy models & pydantic models)
- Folder structure: separate api layer from the rest
- Packet (./recipe/db/packet.py) — Context manager to group db operations and commit/rollback
- Store recipe.instructions as text, and make use of Postgres full text search capabilities

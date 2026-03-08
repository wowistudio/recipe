import logging
from contextlib import asynccontextmanager

from fastapi import APIRouter, FastAPI, HTTPException
from fastapi.exceptions import RequestValidationError
from pydantic import ValidationError
from sqlalchemy import text

from recipe.api.middleware import (
    exception_handler,
    http_exception_handler,
    not_found_exception_handler,
    validation_exception_handler,
)
from recipe.api.routes import recipes
from recipe.crud._base_public import NotFoundException
from recipe.db.session import async_engine

logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: validate DB connection
    async with async_engine.connect() as conn:
        await conn.execute(text("SELECT 1"))
    yield



def build() -> FastAPI:
    app = FastAPI(
        title="Recipe API",
        version="1.0.0",
        openapi_url="/openapi.json",
        lifespan=lifespan,
    )

    app.exception_handler(RequestValidationError)(validation_exception_handler)
    app.exception_handler(ValidationError)(validation_exception_handler)
    app.exception_handler(NotFoundException)(not_found_exception_handler)
    app.exception_handler(HTTPException)(http_exception_handler)
    app.exception_handler(Exception)(exception_handler)

    v1 = APIRouter(prefix="/api")
    v1.include_router(recipes.router, prefix="/recipes")
    app.include_router(v1)

    return app

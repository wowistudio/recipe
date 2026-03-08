from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession

from recipe.db.session import SessionMaker


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """Yield an async database session to be used in dependency injection.

    Yields:
    ------
        AsyncSession: An async database session

    """
    async with SessionMaker() as session:
        try:
            yield session
        finally:
            await session.close()

from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from recipe.core.settings import settings

async_engine = create_async_engine(settings.db.database_url)

SessionMaker = async_sessionmaker(autocommit=False, autoflush=False, bind=async_engine)

"""Base CRUD class for system-wide public resources."""

from typing import Generic, TypeVar
from uuid import UUID

from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql.elements import ColumnElement

from recipe.db.packet import Packet
from recipe.schemas._base import Base

ModelType = TypeVar("ModelType", bound=Base)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)


class NotFoundException(Exception):
    def __init__(self, message: str | None = "Object not found"):
        self.message = message
        super().__init__(self.message)


class CrudPublic(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    """CRUD for system-wide public resources."""

    def __init__(self, model: type[ModelType]):
        """Initialize the CRUD object.

        Args:
        ----
            model (Type[ModelType]): The model to be used in the CRUD operations.
        """
        self.model = model

    async def get(self, session: AsyncSession, id: UUID) -> ModelType | None:
        """Get object by ID.

        Args:
        ----
            session (AsyncSession): The database session.
            id (UUID): The UUID of the object to get.

        Returns:
        -------
            ModelType | None: The object with the given ID.
        """
        result = await session.execute(select(self.model).where(self.model.id == id))
        db_obj = result.unique().scalar_one_or_none()
        return db_obj

    async def get_or_404(self, session: AsyncSession, id: UUID) -> ModelType:
        """Get object by ID or raise 404 error.

        Args:
        ----
            session (AsyncSession): The database session.
            id (UUID): The UUID of the object to get.
        """
        db_obj = await self.get(session, id)
        if not db_obj:
            raise NotFoundException(f"Object with ID {id} not found")
        return db_obj

    async def create(
        self,
        session: AsyncSession,
        *,
        data: CreateSchemaType,
        packet: Packet | None = None,
    ) -> ModelType:
        """Create public resource.

        Args:
        ----
            session (AsyncSession): The database session.
            data (CreateSchemaType): The object to create.
            packet (Packet | None): The packet to use for the transaction.

        Returns:
        -------
            ModelType: The created object.
        """
        _data = data.model_dump(exclude_unset=True)
        _db_obj = self.model.from_dict(_data)
        session.add(_db_obj)

        if not packet:
            await session.commit()
            await session.refresh(_db_obj)

        return _db_obj

    async def update(
        self,
        session: AsyncSession,
        *,
        db_obj: ModelType,
        data: UpdateSchemaType,
        packet: Packet | None = None,
    ) -> ModelType:
        """Update public resource.

        Args:
        ----
            session (AsyncSession): The database session.
            db_obj (ModelType): The object to update.
            data (UpdateSchemaType): The new object data.
            packet (UnitOfWork | None): The unit of work to use for the transaction.

        Returns:
        -------
            ModelType: The updated object.
        """
        _data = data.model_dump(exclude_unset=True)

        for field, value in _data.items():
            setattr(db_obj, field, value)

        if not packet:
            await session.commit()
            await session.refresh(db_obj)

        return db_obj

    async def remove(
        self,
        session: AsyncSession,
        *,
        id: UUID,
        packet: Packet | None = None,
    ) -> ModelType | None:
        """Delete public resource.

        Args:
        ----
            session (AsyncSession): The database session.
            id (UUID): The UUID of the object to delete.
            packet (Packet | None): The packet to use for the transaction.

        Returns:
        -------
            ModelType | None: The deleted object.
        """
        result = await session.execute(select(self.model).where(self.model.id == id))
        db_obj = result.unique().scalar_one_or_none()

        if db_obj is None:
            raise NotFoundException(f"Object with ID {id} not found")

        await session.delete(db_obj)

        if not packet:
            await session.commit()

        return db_obj

    async def list(
        self,
        session: AsyncSession,
        *,
        skip: int = 0,
        limit: int = 100,
        filters: list[ColumnElement[bool]] | None = None,
        disable_limit: bool = True,
    ) -> list[ModelType]:
        """List public resources, optionally filtered by filters.

        Args:
        ----
            session (AsyncSession): The database session.
            skip (int): The number of objects to skip.
            limit (int): The number of objects to return.
            filters (list[ColumnElement[bool]] | None): The filters to apply to the query.
            disable_limit (bool): Disable the limit parameter by default.

        Returns:
        -------
            list[ModelType]: A list of objects.
        """
        query = select(self.model)

        if filters:
            query = query.where(*filters)

        query = query.offset(skip)
        if not disable_limit:
            query = query.limit(limit)

        result = await session.execute(query)
        return list(result.unique().scalars().all())

from sqlalchemy.ext.asyncio import AsyncSession


class Packet:
    """Packet for database transactions.
    Can be used to group database operations and commit or rollback them together.
    The operations are committed or rolled back as soon as the context manager exits.

    Usage:
    -----
    ```python
    async with Packet(session) as packet:
        # ...
    ```
    """

    def __init__(self, session_or_packet: "AsyncSession | Packet"):
        self.nested = isinstance(session_or_packet, Packet)
        self.session = (
            session_or_packet.session
            if isinstance(session_or_packet, Packet)
            else session_or_packet
        )
        self._committed = False
        self._rolledback = False

    @property
    def committed(self) -> bool:
        """
        Check if the packet has been committed.
        """
        return self._committed

    async def commit(self) -> None:
        """
        Commit the packet.
        If the packet has already been committed or rolled back, this method does nothing.
        """
        if self.nested or self._committed or self._rolledback:
            return

        await self.session.commit()
        self._committed = True

    async def rollback(self) -> None:
        """
        Rollback the packet.
        If the packet has already been committed or rolled back, this method does nothing.
        """
        if self.nested or self._committed or self._rolledback:
            return
        await self.session.rollback()
        self._rolledback = True

    async def __aenter__(self) -> "Packet":
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        if self.nested:
            return
        if exc_type is not None:
            await self.rollback()
        else:
            await self.commit()

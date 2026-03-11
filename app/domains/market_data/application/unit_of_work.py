from typing import Protocol
from sqlalchemy.ext.asyncio import AsyncSession
from app.infrastructure.database import AsyncSessionLocal
from app.domains.market_data.domain.repositories import MarketDataRepository
from app.domains.market_data.infrastructure.repositories import PostgresMarketDataRepository

class AbstractUnitOfWork(Protocol):
    market_data: MarketDataRepository

    async def __aenter__(self) -> "AbstractUnitOfWork": ...
    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None: ...
    async def commit(self) -> None: ...
    async def rollback(self) -> None: ...

class SqlAlchemyUnitOfWork:
    def __init__(self):
        self.session_factory = AsyncSessionLocal

    async def __aenter__(self):
        self.session: AsyncSession = self.session_factory()
        self.market_data = PostgresMarketDataRepository(self.session)
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            await self.rollback()
        await self.session.close()

    async def commit(self):
        await self.session.commit()

    async def rollback(self):
        await self.session.rollback()

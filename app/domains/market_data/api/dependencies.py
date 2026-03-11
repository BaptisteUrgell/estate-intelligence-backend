from collections.abc import AsyncGenerator
from typing import Annotated

from fastapi import Depends

from app.domains.market_data.application.services import MarketDataService
from app.domains.market_data.application.unit_of_work import SqlAlchemyUnitOfWork


async def get_uow() -> AsyncGenerator[SqlAlchemyUnitOfWork, None]:
    yield SqlAlchemyUnitOfWork()

UoWDep = Annotated[SqlAlchemyUnitOfWork, Depends(get_uow)]

def get_market_data_service(uow: UoWDep) -> MarketDataService:
    return MarketDataService(uow=uow)

MarketDataServiceDep = Annotated[MarketDataService, Depends(get_market_data_service)]


from typing import Any

from app.domains.market_data.application.unit_of_work import AbstractUnitOfWork
from app.domains.market_data.domain.entities import (
    AnalysisResult,
    CellHistoryPoint,
    MarketDataPoint,
)


class MarketDataService:
    def __init__(self, uow: AbstractUnitOfWork):
        self.uow = uow

    async def get_resolutions(self) -> list[int]:
        async with self.uow:
            return await self.uow.market_data.get_resolutions()

    async def get_periods(self, resolution: int, granularity: str) -> list[str]:
        async with self.uow:
            return await self.uow.market_data.get_periods(resolution, granularity)

    async def get_geojson(self, resolution: int) -> dict[str, Any]:
        async with self.uow:
            return await self.uow.market_data.get_geojson(resolution)

    async def get_map_data(
        self, resolution: int, granularity: str, period: str, mode: str
    ) -> list[MarketDataPoint]:
        async with self.uow:
            return await self.uow.market_data.get_map_data(resolution, granularity, period, mode)

    async def get_cell_history(
        self, grid_id: int, resolution: int, granularity: str
    ) -> list[CellHistoryPoint]:
        async with self.uow:
            return await self.uow.market_data.get_cell_history(grid_id, resolution, granularity)

    async def perform_marker_analysis(
        self, lat: float, lon: float, price: float, resolution: int, granularity: str, period: str
    ) -> AnalysisResult:
        from app.domains.market_data.domain.exceptions import GridCellNotFoundError

        async with self.uow:
            cell = await self.uow.market_data.get_nearest_grid_cell(lat, lon, resolution)
            if not cell:
                raise GridCellNotFoundError(lat, lon, resolution)

            market_price = await self.uow.market_data.get_market_price_for_cell(
                cell.id, granularity, period
            )

            if market_price is None:
                return AnalysisResult(
                    nearest_grid_id=cell.grid_id,
                    market_price=None,
                    diff_euros=None,
                    diff_pct=None,
                    is_good_deal=False,
                    message="Pas de données pour cette période",
                )

            diff_euros = price - market_price
            diff_pct = (diff_euros / market_price) * 100
            is_good_deal = diff_euros < 0

            if is_good_deal:
                message = f"Bonne affaire ! ({abs(diff_pct):.1f}% en dessous du marché)"
            else:
                message = f"Trop cher (+{diff_pct:.1f}% au-dessus du marché)"

            return AnalysisResult(
                nearest_grid_id=cell.grid_id,
                market_price=market_price,
                diff_euros=diff_euros,
                diff_pct=diff_pct,
                is_good_deal=is_good_deal,
                message=message,
            )

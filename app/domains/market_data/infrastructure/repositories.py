from typing import List, Optional, Dict, Any
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.domains.market_data.domain.repositories import MarketDataRepository
from app.domains.market_data.domain.entities import GridCell, MarketDataPoint, CellHistoryPoint
from app.domains.market_data.infrastructure.models import GridCellModel, MarketDataModel

class PostgresMarketDataRepository(MarketDataRepository):
    def __init__(self, session: AsyncSession):
        self._session = session

    async def get_resolutions(self) -> List[int]:
        stmt = select(GridCellModel.resolution).distinct().order_by(GridCellModel.resolution)
        result = await self._session.execute(stmt)
        return [row[0] for row in result.all()]

    async def get_periods(self, resolution: int, granularity: str) -> List[str]:
        stmt = (
            select(MarketDataModel.period)
            .join(GridCellModel, GridCellModel.id == MarketDataModel.grid_cell_id)
            .where(GridCellModel.resolution == resolution)
            .where(MarketDataModel.granularity == granularity)
            .distinct()
            .order_by(MarketDataModel.period)
        )
        result = await self._session.execute(stmt)
        return [row[0] for row in result.all()]

    async def get_geojson(self, resolution: int) -> Dict[str, Any]:
        stmt = select(GridCellModel.geojson_feature).where(GridCellModel.resolution == resolution)
        result = await self._session.execute(stmt)
        features = [row[0] for row in result.all()]
        
        if not features:
            return {}
            
        return {
            "type": "FeatureCollection",
            "features": features
        }

    async def get_map_data(self, resolution: int, granularity: str, period: str, mode: str) -> List[MarketDataPoint]:
        col = MarketDataModel.evolution if mode == "tendance" else MarketDataModel.price
        
        stmt = (
            select(GridCellModel.grid_id, col)
            .join(MarketDataModel, GridCellModel.id == MarketDataModel.grid_cell_id)
            .where(GridCellModel.resolution == resolution)
            .where(MarketDataModel.granularity == granularity)
            .where(MarketDataModel.period == period)
            .where(col.is_not(None))
        )
        result = await self._session.execute(stmt)
        return [MarketDataPoint(id=row[0], val=row[1]) for row in result.all()]

    async def get_cell_history(self, grid_id: int, resolution: int, granularity: str) -> List[CellHistoryPoint]:
        stmt = (
            select(MarketDataModel.period, MarketDataModel.price, MarketDataModel.evolution)
            .join(GridCellModel, GridCellModel.id == MarketDataModel.grid_cell_id)
            .where(GridCellModel.resolution == resolution)
            .where(GridCellModel.grid_id == grid_id)
            .where(MarketDataModel.granularity == granularity)
            .order_by(MarketDataModel.period)
        )
        result = await self._session.execute(stmt)
        return [CellHistoryPoint(period=row[0], price=row[1], evolution=row[2]) for row in result.all()]

    async def get_nearest_grid_cell(self, lat: float, lon: float, resolution: int) -> Optional[GridCell]:
        stmt = (
            select(GridCellModel)
            .where(GridCellModel.resolution == resolution)
            .order_by(
                func.power(GridCellModel.center_lat - lat, 2) + func.power(GridCellModel.center_lon - lon, 2)
            )
            .limit(1)
        )
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()
        if not model:
            return None
        return GridCell(
            id=model.id,
            resolution=model.resolution,
            grid_id=model.grid_id,
            center_lat=model.center_lat,
            center_lon=model.center_lon,
            geojson_feature=model.geojson_feature
        )

    async def get_market_price_for_cell(self, grid_cell_id: int, granularity: str, period: str) -> Optional[float]:
        stmt = (
            select(MarketDataModel.price)
            .where(MarketDataModel.grid_cell_id == grid_cell_id)
            .where(MarketDataModel.granularity == granularity)
            .where(MarketDataModel.period == period)
        )
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

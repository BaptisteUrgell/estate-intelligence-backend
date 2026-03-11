from typing import List, Optional, Protocol, Dict, Any
from .entities import GridCell, MarketDataPoint, CellHistoryPoint

class MarketDataRepository(Protocol):
    async def get_resolutions(self) -> List[int]:
        ...
        
    async def get_periods(self, resolution: int, granularity: str) -> List[str]:
        ...
        
    async def get_geojson(self, resolution: int) -> Dict[str, Any]:
        ...
        
    async def get_map_data(self, resolution: int, granularity: str, period: str, mode: str) -> List[MarketDataPoint]:
        ...
        
    async def get_cell_history(self, grid_id: int, resolution: int, granularity: str) -> List[CellHistoryPoint]:
        ...
        
    async def get_nearest_grid_cell(self, lat: float, lon: float, resolution: int) -> Optional[GridCell]:
        ...
        
    async def get_market_price_for_cell(self, grid_cell_id: int, granularity: str, period: str) -> Optional[float]:
        ...

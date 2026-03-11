from dataclasses import dataclass
from typing import Optional, Dict, Any, List

@dataclass
class GridCell:
    id: int
    resolution: int
    grid_id: int
    center_lat: float
    center_lon: float
    geojson_feature: Dict[str, Any]

@dataclass
class MarketData:
    id: int
    grid_cell_id: int
    granularity: str
    period: str
    price: Optional[float]
    evolution: Optional[float]
    log_price: Optional[float]

@dataclass
class MarketDataPoint:
    id: int
    val: float

@dataclass
class CellHistoryPoint:
    period: str
    price: Optional[float]
    evolution: Optional[float]

@dataclass
class AnalysisResult:
    nearest_grid_id: int
    market_price: Optional[float]
    diff_euros: Optional[float]
    diff_pct: Optional[float]
    is_good_deal: bool
    message: str

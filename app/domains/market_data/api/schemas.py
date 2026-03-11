from pydantic import BaseModel, ConfigDict, Field


class MapDataResponse(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    id: int
    val: float


class CellHistoryResponse(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    period: str
    price: float | None = None
    evolution: float | None = None


class MarkerAnalysisCreate(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    lat: float = Field(..., ge=-90, le=90)
    lon: float = Field(..., ge=-180, le=180)
    price: float = Field(..., gt=0)
    resolution: int = Field(..., gt=0)
    granularity: str
    period: str


class MarkerAnalysisResponse(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    nearest_grid_id: int
    market_price: float | None = None
    diff_euros: float | None = None
    diff_pct: float | None = None
    is_good_deal: bool
    message: str

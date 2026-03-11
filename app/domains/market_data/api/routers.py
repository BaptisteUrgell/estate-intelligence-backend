from fastapi import APIRouter, HTTPException, Query

from app.domains.market_data.api.dependencies import MarketDataServiceDep
from app.domains.market_data.api.schemas import (
    CellHistoryResponse,
    MapDataResponse,
    MarkerAnalysisCreate,
    MarkerAnalysisResponse,
)

router = APIRouter()


@router.get("/meta/resolutions", response_model=list[int])
async def get_resolutions(service: MarketDataServiceDep):
    return await service.get_resolutions()


@router.get("/meta/periods", response_model=list[str])
async def get_periods(
    service: MarketDataServiceDep,
    granularity: str = Query(..., description="Granularité temporelle (ex: 1y, 6m, 2y)"),
    resolution: int = Query(50, description="Résolution de la grille"),
):
    periods = await service.get_periods(resolution, granularity)
    if not periods:
        raise HTTPException(
            status_code=404, detail="Granularité non trouvée ou aucune période disponible"
        )
    return periods


@router.get("/map/geojson")
async def get_map_geojson(
    service: MarketDataServiceDep,
    resolution: int = Query(..., description="Résolution de la grille"),
):
    geojson = await service.get_geojson(resolution)
    if not geojson:
        raise HTTPException(status_code=404, detail="GeoJSON non trouvé pour cette résolution")
    return geojson


@router.get("/map/data", response_model=list[MapDataResponse])
async def get_map_data(
    service: MarketDataServiceDep,
    resolution: int = Query(...),
    granularity: str = Query(...),
    period: str = Query(...),
    mode: str = Query(..., description="Mode de visualisation (tendance ou prix)"),
):
    data = await service.get_map_data(resolution, granularity, period, mode)
    return [MapDataResponse(id=p.id, val=p.val) for p in data]


@router.get("/cell/{grid_id}/history", response_model=list[CellHistoryResponse])
async def get_cell_history(
    grid_id: int,
    service: MarketDataServiceDep,
    resolution: int = Query(...),
    granularity: str = Query(...),
):
    history = await service.get_cell_history(grid_id, resolution, granularity)
    return [
        CellHistoryResponse(period=p.period, price=p.price, evolution=p.evolution) for p in history
    ]


@router.post("/analyze/marker", response_model=MarkerAnalysisResponse)
async def perform_marker_analysis(
    req: MarkerAnalysisCreate, service: MarketDataServiceDep
):
    from app.domains.market_data.domain.exceptions import GridCellNotFoundError

    try:
        result = await service.perform_marker_analysis(
            req.lat, req.lon, req.price, req.resolution, req.granularity, req.period
        )
    except GridCellNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))

    return MarkerAnalysisResponse(
        nearest_grid_id=result.nearest_grid_id,
        market_price=result.market_price,
        diff_euros=result.diff_euros,
        diff_pct=result.diff_pct,
        is_good_deal=result.is_good_deal,
        message=result.message,
    )

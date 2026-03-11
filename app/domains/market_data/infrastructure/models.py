from typing import Any
from uuid import UUID

from sqlalchemy import ForeignKey, Index, String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from typing_extensions import TypedDict
from uuid_extensions import uuid7


class GeojsonFeature(TypedDict):
    type: str
    features: list[dict[str, Any]]


class MarketDataBase(DeclarativeBase):
    type_annotation_map = {
        TypedDict[str, Any]: JSONB,
        UUID: PG_UUID(as_uuid=True, default=uuid7),
    }


class GridCellModel(MarketDataBase):
    __tablename__ = "grid_cells"

    id: Mapped[UUID] = mapped_column(primary_key=True)
    resolution: Mapped[int]
    grid_id: Mapped[UUID]
    center_lat: Mapped[float]
    center_lon: Mapped[float]
    geojson_feature: Mapped[dict[str, Any]]

    market_data: Mapped[list["MarketDataModel"]] = relationship(
        back_populates="grid_cell", cascade="all, delete-orphan"
    )

    __table_args__ = (
        Index("ix_grid_cells_resolution_grid_id", "resolution", "grid_id", unique=True),
    )


class MarketDataModel(MarketDataBase):
    __tablename__ = "market_data"

    id: Mapped[UUID] = mapped_column(primary_key=True)
    grid_cell_id: Mapped[UUID] = mapped_column(ForeignKey("grid_cells.id", ondelete="CASCADE"))
    granularity: Mapped[str] = mapped_column(String(10))
    period: Mapped[str] = mapped_column(String(20))
    price: Mapped[float | None]
    evolution: Mapped[float | None]
    log_price: Mapped[float | None]

    grid_cell: Mapped["GridCellModel"] = relationship(back_populates="market_data")

    __table_args__ = (
        Index("ix_market_data_lookup", "grid_cell_id", "granularity", "period", unique=True),
    )

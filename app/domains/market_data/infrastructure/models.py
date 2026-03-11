from typing import Any
from uuid import UUID

from geoalchemy2 import Geometry
from sqlalchemy import ForeignKey, Index, String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from uuid_extensions import uuid7

from app.infrastructure.database.mixins import AuditMixin


class MarketDataBase(DeclarativeBase):
    type_annotation_map = {
        dict[str, Any]: JSONB,
        UUID: PG_UUID(as_uuid=True),
    }


class GridCellModel(MarketDataBase, AuditMixin):
    __tablename__ = "grid_cells"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid7)
    h3_index: Mapped[str] = mapped_column(String, unique=True, index=True)
    resolution: Mapped[int]

    # Using GeoAlchemy2 for PostGIS
    geometry: Mapped[Any] = mapped_column(Geometry("POLYGON", srid=4326))

    metrics: Mapped[list["GridMetricModel"]] = relationship(
        back_populates="grid_cell", cascade="all, delete-orphan"
    )


class GridMetricModel(MarketDataBase, AuditMixin):
    __tablename__ = "grid_metrics"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid7)
    grid_cell_id: Mapped[UUID] = mapped_column(ForeignKey("grid_cells.id", ondelete="CASCADE"))
    granularity: Mapped[str] = mapped_column(String(50))
    period: Mapped[str] = mapped_column(String(50))

    price_per_sqm: Mapped[float | None]
    evolution_pct: Mapped[float | None]

    grid_cell: Mapped["GridCellModel"] = relationship(back_populates="metrics")

    __table_args__ = (
        Index("idx_unique_metric", "grid_cell_id", "granularity", "period", unique=True),
        Index("idx_period_fast_search", "period"),
    )

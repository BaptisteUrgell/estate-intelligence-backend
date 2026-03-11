from typing import Any
from uuid import UUID

from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from uuid_extensions import uuid7


class MapConfigBase(DeclarativeBase):
    type_annotation_map = {
        dict[str, Any]: JSONB,
        UUID: PG_UUID(as_uuid=True, default=uuid7),
    }


class MapGranularityModel(MapConfigBase):
    __tablename__ = "map_granularities"

    id: Mapped[UUID] = mapped_column(primary_key=True)
    resolution_value: Mapped[int] = mapped_column(unique=True)
    is_default: Mapped[bool] = mapped_column(default=False)

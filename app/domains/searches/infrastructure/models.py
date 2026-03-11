from datetime import datetime
from enum import StrEnum
from uuid import UUID

from sqlalchemy import DateTime, Enum, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from uuid_extensions import uuid7

from app.infrastructure.database.mixins import AuditMixin


class SearchBase(DeclarativeBase):
    type_annotation_map = {UUID: PG_UUID(as_uuid=True)}


class PropertyTypeEnum(StrEnum):
    appartement = "appartement"
    maison = "maison"


class SearchModel(SearchBase, AuditMixin):
    __tablename__ = "searches"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid7)
    profile_id: Mapped[UUID]
    name: Mapped[str | None] = mapped_column(String)
    epicenter_lat: Mapped[float]
    epicenter_lon: Mapped[float]

    deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    properties: Mapped[list["SearchPropertyModel"]] = relationship(
        back_populates="search", cascade="all, delete-orphan"
    )


class SearchPropertyModel(SearchBase, AuditMixin):
    __tablename__ = "search_properties"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid7)
    search_id: Mapped[UUID] = mapped_column(ForeignKey("searches.id", ondelete="CASCADE"))
    title: Mapped[str] = mapped_column(String)
    type: Mapped[PropertyTypeEnum] = mapped_column(
        Enum(PropertyTypeEnum, native_enum=True, create_type=True)
    )

    # Localisation
    lat: Mapped[float]
    lon: Mapped[float]

    # Caractéristiques principales
    surface: Mapped[float]
    total_price: Mapped[float]
    price_per_sqm: Mapped[float | None]  # calculated
    agency_name: Mapped[str | None] = mapped_column(String)

    # Données financières
    annual_charges: Mapped[float | None]
    energy_costs: Mapped[float | None]
    property_tax: Mapped[float | None]

    deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    search: Mapped["SearchModel"] = relationship(back_populates="properties")

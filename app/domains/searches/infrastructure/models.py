from uuid import UUID

from sqlalchemy import ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from uuid_extensions import uuid7


class SearchBase(DeclarativeBase):
    type_annotation_map = {UUID: PG_UUID(as_uuid=True)}


class SearchModel(SearchBase):
    __tablename__ = "searches"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid7)
    profile_id: Mapped[UUID] = mapped_column(ForeignKey("profiles.id", ondelete="CASCADE"))
    center_lat: Mapped[float]
    center_lon: Mapped[float]

    points: Mapped[list["SearchPointModel"]] = relationship(
        back_populates="search", cascade="all, delete-orphan"
    )


class SearchPointModel(SearchBase):
    __tablename__ = "search_points"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid7)
    search_id: Mapped[UUID] = mapped_column(ForeignKey("searches.id", ondelete="CASCADE"))
    latitude: Mapped[float]
    longitude: Mapped[float]
    price_per_m2: Mapped[float]
    total_surface: Mapped[float]
    property_type: Mapped[str] = mapped_column(String)  # "Appartement" ou "Maison"

    search: Mapped["SearchModel"] = relationship(back_populates="points")

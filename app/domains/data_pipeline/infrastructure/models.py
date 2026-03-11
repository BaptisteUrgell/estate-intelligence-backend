from datetime import date
from uuid import UUID

from sqlalchemy import Date, Float, Index, Integer, String
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from uuid_extensions import uuid7

from app.infrastructure.database.mixins import AuditMixin


class DataPipelineBase(DeclarativeBase):
    type_annotation_map = {UUID: PG_UUID(as_uuid=True)}


class RawTransactionModel(DataPipelineBase, AuditMixin):
    __tablename__ = "raw_transactions"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid7)

    id_mutation: Mapped[str | None] = mapped_column(String)
    date_mutation: Mapped[date | None] = mapped_column(Date)
    numero_disposition: Mapped[str | None] = mapped_column(String)
    nature_mutation: Mapped[str | None] = mapped_column(String)
    valeur_fonciere: Mapped[float | None] = mapped_column(Float)

    # Adresse
    adresse_numero: Mapped[str | None] = mapped_column(String)
    adresse_suffixe: Mapped[str | None] = mapped_column(String)
    adresse_nom_voie: Mapped[str | None] = mapped_column(String)
    adresse_code_voie: Mapped[str | None] = mapped_column(String)
    code_postal: Mapped[str | None] = mapped_column(String)
    code_commune: Mapped[str | None] = mapped_column(String)
    nom_commune: Mapped[str | None] = mapped_column(String)
    code_departement: Mapped[str | None] = mapped_column(String)
    ancien_code_commune: Mapped[str | None] = mapped_column(String)
    ancien_nom_commune: Mapped[str | None] = mapped_column(String)

    # Cadastre
    id_parcelle: Mapped[str | None] = mapped_column(String)
    ancien_id_parcelle: Mapped[str | None] = mapped_column(String)
    numero_volume: Mapped[str | None] = mapped_column(String)

    # Lots de copropriété
    lot1_numero: Mapped[str | None] = mapped_column(String)
    lot1_surface_carrez: Mapped[float | None] = mapped_column(Float)
    lot2_numero: Mapped[str | None] = mapped_column(String)
    lot2_surface_carrez: Mapped[float | None] = mapped_column(Float)
    lot3_numero: Mapped[str | None] = mapped_column(String)
    lot3_surface_carrez: Mapped[float | None] = mapped_column(Float)
    lot4_numero: Mapped[str | None] = mapped_column(String)
    lot4_surface_carrez: Mapped[float | None] = mapped_column(Float)
    lot5_numero: Mapped[str | None] = mapped_column(String)
    lot5_surface_carrez: Mapped[float | None] = mapped_column(Float)
    nombre_lots: Mapped[int | None] = mapped_column(Integer)

    # Caractéristiques du bien
    code_type_local: Mapped[str | None] = mapped_column(String)
    type_local: Mapped[str | None] = mapped_column(String)
    surface_reelle_bati: Mapped[float | None] = mapped_column(Float)
    nombre_pieces_principales: Mapped[int | None] = mapped_column(Integer)

    # Terrain
    code_nature_culture: Mapped[str | None] = mapped_column(String)
    nature_culture: Mapped[str | None] = mapped_column(String)
    code_nature_culture_speciale: Mapped[str | None] = mapped_column(String)
    nature_culture_speciale: Mapped[str | None] = mapped_column(String)
    surface_terrain: Mapped[float | None] = mapped_column(Float)

    # Coordonnées GPS
    longitude: Mapped[float | None] = mapped_column(Float)
    latitude: Mapped[float | None] = mapped_column(Float)

    __table_args__ = (
        Index("idx_raw_mutation", "id_mutation"),
        Index("idx_raw_gps", "latitude", "longitude"),
    )

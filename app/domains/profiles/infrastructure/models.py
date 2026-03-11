from datetime import datetime
from uuid import UUID

from sqlalchemy import DateTime, String
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

from app.infrastructure.database.mixins import AuditMixin


class ProfileBase(DeclarativeBase):
    type_annotation_map = {UUID: PG_UUID(as_uuid=True)}


class ProfileModel(ProfileBase, AuditMixin):
    __tablename__ = "profiles"

    id: Mapped[UUID] = mapped_column(primary_key=True)
    first_name: Mapped[str | None] = mapped_column(String)
    last_name: Mapped[str | None] = mapped_column(String)
    contact_email: Mapped[str | None] = mapped_column(String)
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

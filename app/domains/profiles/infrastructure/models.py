from datetime import datetime
from uuid import UUID

from sqlalchemy import DateTime, String, func
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from uuid_extensions import uuid7


class ProfileBase(DeclarativeBase):
    type_annotation_map = {UUID: PG_UUID(as_uuid=True)}


class ProfileModel(ProfileBase):
    __tablename__ = "profiles"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid7)
    email: Mapped[str] = mapped_column(String, unique=True, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

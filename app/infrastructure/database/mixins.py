from datetime import UTC, datetime

from sqlalchemy import DateTime
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import Mapped, mapped_column


class AuditMixin:
    """
    Mixin transversal providing standardized audit fields (`created_at`, `updated_at`).
    """

    _created_at: Mapped[datetime] = mapped_column(
        "created_at",
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC),
    )

    @hybrid_property
    def created_at(self) -> datetime:
        return self._created_at


class SoftDeleteMixin:
    """
    Mixin providing a field for soft delete.
    """

    deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), default=None)

    @hybrid_property
    def is_deleted(self) -> bool:
        return self.deleted_at.is_not(None)

    @is_deleted.inplace.setter
    def _is_deleted_setter(self, value: bool) -> None:
        self.deleted_at = datetime.now(UTC) if value else None

    @is_deleted.inplace.update_expression
    @classmethod
    def _is_deleted_update(cls, value: bool) -> list[tuple]:
        return

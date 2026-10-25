from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import Boolean, DateTime, ForeignKey, Index, String, Text, func, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.extensions import Model

if TYPE_CHECKING:
    from app.models.user import User


class UserPaymentMethod(Model):
    __tablename__ = "user_payment_methods"
    __table_args__ = (Index("idx_user_payment_methods_user_id", "user_id"),)

    id: Mapped[UUID] = mapped_column(
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )
    user_id: Mapped[UUID] = mapped_column(
        ForeignKey("users.id"),
        nullable=False,
    )
    provider_token: Mapped[str] = mapped_column(Text, nullable=False)
    last_four: Mapped[str | None] = mapped_column(String(4))
    is_default: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        server_default=text("false"),
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    user: Mapped[User] = relationship(back_populates="payment_methods")

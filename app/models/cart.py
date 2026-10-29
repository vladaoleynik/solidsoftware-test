import uuid
from datetime import datetime
from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, Index, Text, func, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.extensions import Model
from app.models.enums import CartStatus

if TYPE_CHECKING:
    from app.models.cart_item import CartItem
    from app.models.user import User


class Cart(Model):
    __tablename__ = "carts"
    __table_args__ = (
        CheckConstraint(
            "status IN ('active', 'checked_out', 'abandoned')",
            name="ck_carts_status",
        ),
        Index("idx_carts_user_id", "user_id"),
    )

    id: Mapped[UUID] = mapped_column(
        primary_key=True,
        default=uuid.uuid4,
        server_default=text("gen_random_uuid()"),
    )
    user_id: Mapped[UUID] = mapped_column(
        ForeignKey("users.id"),
        nullable=False,
    )
    status: Mapped[CartStatus] = mapped_column(
        Text,
        nullable=False,
        default=CartStatus.ACTIVE,
        server_default=text("'active'"),
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    user: Mapped[User] = relationship(back_populates="carts")
    items: Mapped[list[CartItem]] = relationship(
        back_populates="cart",
        cascade="all, delete-orphan",
    )

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import DateTime, Text, func, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.extensions import Model

if TYPE_CHECKING:
    from app.models.cart import Cart
    from app.models.user_payment_method import UserPaymentMethod


class User(Model):
    __tablename__ = "users"

    id: Mapped[UUID] = mapped_column(
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )
    email: Mapped[str] = mapped_column(Text, unique=True, nullable=False)
    name: Mapped[str] = mapped_column(Text, nullable=False)
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

    carts: Mapped[list[Cart]] = relationship(back_populates="user")
    payment_methods: Mapped[list[UserPaymentMethod]] = relationship(
        back_populates="user",
    )

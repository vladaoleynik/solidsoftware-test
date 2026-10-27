from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    ForeignKey,
    Index,
    Numeric,
    String,
    Text,
    func,
    text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.extensions import Model

if TYPE_CHECKING:
    from app.models.cart import Cart
    from app.models.user import User
    from app.models.user_payment_method import UserPaymentMethod


class Payment(Model):
    __tablename__ = "payments"
    __table_args__ = (
        CheckConstraint(
            "status IN ('pending', 'completed', 'failed', 'refunded')",
            name="ck_payments_status",
        ),
        Index("idx_payments_user_id", "user_id"),
        Index("idx_payments_cart_id", "cart_id"),
    )

    id: Mapped[UUID] = mapped_column(
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )
    user_id: Mapped[UUID] = mapped_column(
        ForeignKey("users.id"),
        nullable=False,
    )
    cart_id: Mapped[UUID] = mapped_column(
        ForeignKey("carts.id"),
        nullable=False,
    )
    payment_method_id: Mapped[UUID] = mapped_column(
        ForeignKey("user_payment_methods.id"),
        nullable=False,
    )
    amount: Mapped[Decimal] = mapped_column(
        Numeric(10, 2),
        nullable=False,
    )
    currency: Mapped[str] = mapped_column(
        String(3),
        nullable=False,
        server_default=text("'USD'"),
    )
    status: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        server_default=text("'pending'"),
    )
    # External payment provider's transaction ID (e.g., Stripe, PayPal)
    # Used for reconciliation, refunds, and dispute resolution
    transaction_id: Mapped[str | None] = mapped_column(Text)
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

    user: Mapped[User] = relationship()
    cart: Mapped[Cart] = relationship()
    payment_method: Mapped[UserPaymentMethod] = relationship()

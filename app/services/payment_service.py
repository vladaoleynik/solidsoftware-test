from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from uuid import UUID

from app.extensions import db
from app.models import Cart, Payment, UserPaymentMethod
from app.services.cart_total_calculator import CartTotalCalculator
from app.services.payment_provider import PaymentProvider


class PaymentStatus:
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"
    REFUNDED = "refunded"


class CartStatus:
    ACTIVE = "active"
    CHECKED_OUT = "checked_out"
    ABANDONED = "abandoned"


class PaymentError(Exception):
    """Base class for payment service errors."""


class CartNotFoundError(PaymentError):
    """Raised when the cart does not exist."""


class CartDoesNotBelongToUserError(PaymentError):
    """Raised when the cart belongs to another user."""


class CartAlreadyCheckedOutError(PaymentError):
    """Raised when the cart was already paid for."""


class PaymentMethodNotFoundError(PaymentError):
    """Raised when the payment method does not exist."""


class PaymentMethodDoesNotBelongToUserError(PaymentError):
    """Raised when the payment method belongs to another user."""


@dataclass(frozen=True)
class ProcessPaymentResult:
    payment_id: UUID
    status: str
    transaction_id: str | None
    failure_reason: str | None


class PaymentService:
    def __init__(
        self,
        payment_provider: PaymentProvider,
        cart_total_calculator: CartTotalCalculator,
    ) -> None:
        self.payment_provider = payment_provider
        self.cart_total_calculator = cart_total_calculator

    def process_payment(
        self,
        *,
        user_id: UUID,
        cart_id: UUID,
        payment_method_id: UUID,
        currency: str = "USD",
    ) -> ProcessPaymentResult:
        cart = self._get_user_cart(user_id=user_id, cart_id=cart_id)
        payment_method = self._get_user_payment_method(
            user_id=user_id,
            payment_method_id=payment_method_id,
        )

        self._ensure_cart_can_be_paid(cart)

        amount = self.cart_total_calculator.calculate_total(cart_id)

        payment = self._create_pending_payment(
            user_id=user_id,
            cart_id=cart_id,
            payment_method_id=payment_method_id,
            amount=amount,
            currency=currency,
        )

        provider_result = self.payment_provider.process_payment(
            provider_token=payment_method.provider_token,
            amount=amount,
            currency=currency,
        )

        failure_reason = provider_result.failure_reason

        if provider_result.success:
            payment.status = PaymentStatus.COMPLETED
            payment.transaction_id = provider_result.transaction_id
            cart.status = CartStatus.CHECKED_OUT
            failure_reason = None
        else:
            payment.status = PaymentStatus.FAILED

        db.session.commit()

        return ProcessPaymentResult(
            payment_id=payment.id,
            status=payment.status,
            transaction_id=payment.transaction_id,
            failure_reason=failure_reason,
        )

    def _get_user_cart(self, *, user_id: UUID, cart_id: UUID) -> Cart:
        cart = db.session.get(Cart, cart_id)

        if cart is None:
            raise CartNotFoundError

        if cart.user_id != user_id:
            raise CartDoesNotBelongToUserError

        return cart

    def _get_user_payment_method(
        self,
        *,
        user_id: UUID,
        payment_method_id: UUID,
    ) -> UserPaymentMethod:
        payment_method = db.session.get(UserPaymentMethod, payment_method_id)

        if payment_method is None:
            raise PaymentMethodNotFoundError

        if payment_method.user_id != user_id:
            raise PaymentMethodDoesNotBelongToUserError

        return payment_method

    def _ensure_cart_can_be_paid(self, cart: Cart) -> None:
        if cart.status == CartStatus.CHECKED_OUT:
            raise CartAlreadyCheckedOutError

    def _create_pending_payment(
        self,
        *,
        user_id: UUID,
        cart_id: UUID,
        payment_method_id: UUID,
        amount: Decimal,
        currency: str,
    ) -> Payment:
        payment = Payment(
            user_id=user_id,
            cart_id=cart_id,
            payment_method_id=payment_method_id,
            amount=amount,
            currency=currency,
            status=PaymentStatus.PENDING,
        )

        db.session.add(payment)
        db.session.flush()

        return payment

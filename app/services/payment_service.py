from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from uuid import UUID

from app.extensions import db
from app.models import Cart, Payment, UserPaymentMethod
from app.models.enums import CartStatus, PaymentStatus
from app.services.cart_total_calculator import CartTotalCalculator
from app.services.payment_provider import PaymentProvider


class PaymentError(Exception):
    """Base class for payment service errors."""

    message = "An unexpected payment error occurred"
    status_code = 500

    def __init__(
        self, message: str | None = None, status_code: int | None = None
    ) -> None:
        if message is not None:
            self.message = message
        if status_code is not None:
            self.status_code = status_code
        super().__init__(self.message)


class CartNotFoundError(PaymentError):
    """Raised when the cart does not exist."""

    message = "Cart not found"
    status_code = 404


class EmptyCartError(PaymentError):
    """Raised when the cart has no items."""

    message = "Cart is empty"
    status_code = 400


class PaymentAlreadyInProgressError(PaymentError):
    """Raised when there is already a pending payment for the cart."""

    message = "Payment already in progress"
    status_code = 400


class PaymentMethodNotFoundError(PaymentError):
    """Raised when the payment method does not exist."""

    message = "Payment method not found"
    status_code = 404


@dataclass(frozen=True)
class ProcessPaymentResult:
    payment_id: UUID
    status: PaymentStatus
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
    ) -> ProcessPaymentResult:
        try:
            return self._do_process_payment(user_id=user_id)
        except PaymentError:
            db.session.rollback()
            raise
        except Exception as e:
            db.session.rollback()
            raise PaymentError(f"Internal payment service error: {str(e)}") from e

    def _do_process_payment(self, user_id: UUID) -> ProcessPaymentResult:
        # 1. Start transaction and lock cart
        cart = self._get_active_user_cart(user_id=user_id)
        payment_method = self._get_default_user_payment_method(user_id=user_id)

        self._ensure_cart_can_be_paid(cart)

        cart_total = self.cart_total_calculator.calculate_total(cart.id)

        # 2. Create pending payment and commit it before calling the provider
        # This ensures we have a record of the attempt if the provider call fails/hangs.
        payment = self._create_pending_payment(
            user_id=user_id,
            cart_id=cart.id,
            payment_method_id=payment_method.id,
            amount=cart_total.amount,
            currency=cart_total.currency,
        )

        # Commit to release the lock on the cart and persist the pending payment.
        db.session.commit()

        # 3. Call external payment provider
        provider_result = self.payment_provider.process_payment(
            provider_token=payment_method.provider_token,
            amount=cart_total.amount,
            currency=cart_total.currency,
        )

        # 4. Update payment and cart status based on provider result
        # Re-fetch them in a new transaction to update their state.
        updated_payment = db.session.get(Payment, payment.id, with_for_update=True)
        updated_cart = db.session.get(Cart, cart.id, with_for_update=True)

        if updated_payment is None or updated_cart is None:
            raise PaymentError("Payment or cart not found during finalization")

        payment = updated_payment
        cart = updated_cart

        if provider_result.success:
            payment.status = PaymentStatus.COMPLETED
            payment.transaction_id = provider_result.transaction_id
            cart.status = CartStatus.CHECKED_OUT
            failure_reason = None
        else:
            payment.status = PaymentStatus.FAILED
            failure_reason = provider_result.failure_reason

        # Finalize the transaction
        db.session.commit()

        return ProcessPaymentResult(
            payment_id=payment.id,
            status=payment.status,
            transaction_id=payment.transaction_id,
            failure_reason=failure_reason,
        )

    def _get_active_user_cart(self, *, user_id: UUID) -> Cart:
        cart = (
            db.session.query(Cart)
            .filter_by(user_id=user_id, status=CartStatus.ACTIVE)
            .order_by(Cart.created_at.desc())
            .with_for_update()
            .first()
        )

        if cart is None:
            raise CartNotFoundError("Active cart not found")

        return cart

    def _get_default_user_payment_method(self, *, user_id: UUID) -> UserPaymentMethod:
        # Try to find default one
        payment_method = (
            db.session.query(UserPaymentMethod)
            .filter_by(user_id=user_id, is_default=True)
            .first()
        )

        if payment_method is None:
            # Fallback to the most recently added one
            payment_method = (
                db.session.query(UserPaymentMethod)
                .filter_by(user_id=user_id)
                .order_by(UserPaymentMethod.created_at.desc())
                .first()
            )

        if payment_method is None:
            raise PaymentMethodNotFoundError("No payment method found for user")

        return payment_method

    def _ensure_cart_can_be_paid(self, cart: Cart) -> None:
        if not cart.items:
            raise EmptyCartError

        # Check if there's already a pending payment for this cart to prevent
        # double charging while the first request is waiting for the provider.
        existing_pending_payment = (
            db.session.query(Payment)
            .filter_by(cart_id=cart.id, status=PaymentStatus.PENDING)
            .first()
        )

        if existing_pending_payment:
            raise PaymentAlreadyInProgressError

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

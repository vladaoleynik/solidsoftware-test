from decimal import Decimal

import pytest

from app.extensions import db
from app.models import Cart, Payment
from app.models.enums import CartStatus, PaymentStatus
from app.services.cart_total_calculator import CartTotal, StubCartTotalCalculator
from app.services.payment_provider import MockPaymentProvider
from app.services.payment_service import (
    CartNotFoundError,
    EmptyCartError,
    PaymentMethodNotFoundError,
    PaymentService,
)
from tests.factories import (
    CartFactory,
    CartItemFactory,
    UserFactory,
    UserPaymentMethodFactory,
)


@pytest.fixture
def payment_service():
    return PaymentService(
        payment_provider=MockPaymentProvider(),
        cart_total_calculator=StubCartTotalCalculator(),
    )


@pytest.fixture
def user(app):
    return UserFactory()


@pytest.fixture
def cart(user):
    cart = CartFactory(user=user)
    CartItemFactory(cart=cart)
    return cart


@pytest.fixture
def payment_method(user):
    return UserPaymentMethodFactory(user=user)


def test_process_payment_success(payment_service, user, cart, payment_method):
    result = payment_service.process_payment(user_id=user.id)

    assert result.status == PaymentStatus.COMPLETED
    assert result.transaction_id.startswith("txn_")
    assert result.failure_reason is None

    # Verify DB state
    db_payment = db.session.get(Payment, result.payment_id)
    assert db_payment.status == PaymentStatus.COMPLETED
    assert db_payment.amount == Decimal("100.00")
    assert db_payment.currency == "USD"

    db_cart = db.session.get(Cart, cart.id)
    assert db_cart.status == CartStatus.CHECKED_OUT


def test_process_payment_failure_insufficient_funds(
    payment_service, user, cart, payment_method
):
    payment_method.provider_token = "pm_mock_insufficient_funds"
    db.session.commit()

    result = payment_service.process_payment(user_id=user.id)

    assert result.status == PaymentStatus.FAILED
    assert result.failure_reason == "insufficient_funds"

    # Verify DB state
    db_payment = db.session.get(Payment, result.payment_id)
    assert db_payment.status == PaymentStatus.FAILED

    db_cart = db.session.get(Cart, cart.id)
    assert db_cart.status == CartStatus.ACTIVE


def test_process_payment_cart_not_found(payment_service, user, payment_method):
    with pytest.raises(CartNotFoundError):
        payment_service.process_payment(user_id=user.id)


def test_process_payment_cart_wrong_user(payment_service, cart, payment_method):
    other_user = UserFactory()
    # other_user has no cart
    with pytest.raises(CartNotFoundError):
        payment_service.process_payment(user_id=other_user.id)


def test_process_payment_cart_already_checked_out(
    payment_service, user, cart, payment_method
):
    cart.status = CartStatus.CHECKED_OUT
    db.session.commit()

    with pytest.raises(CartNotFoundError):
        payment_service.process_payment(user_id=user.id)


def test_process_payment_cart_empty(payment_service, user, payment_method):
    # Ensure this is the active cart for the user
    CartFactory(user=user)
    # No items added to this cart

    with pytest.raises(EmptyCartError):
        payment_service.process_payment(user_id=user.id)


def test_process_payment_method_not_found(payment_service, user, cart):
    # user has no payment method
    with pytest.raises(PaymentMethodNotFoundError):
        payment_service.process_payment(user_id=user.id)


def test_process_payment_method_wrong_user(payment_service, user, cart, payment_method):
    other_user = UserFactory()
    # Create a cart for other_user
    CartFactory(user=other_user, status=CartStatus.ACTIVE)
    CartItemFactory(
        cart=db.session.query(Cart).filter_by(user_id=other_user.id).first()
    )

    # other_user has no payment method (payment_method belongs to 'user')
    with pytest.raises(PaymentMethodNotFoundError):
        payment_service.process_payment(user_id=other_user.id)


def test_process_payment_automatic_lookup(payment_service, user, cart, payment_method):
    # Ensure this is the default payment method
    payment_method.is_default = True
    db.session.commit()

    result = payment_service.process_payment(user_id=user.id)

    assert result.status == PaymentStatus.COMPLETED
    assert result.transaction_id.startswith("txn_")

    db_payment = db.session.get(Payment, result.payment_id)
    assert db_payment.cart_id == cart.id
    assert db_payment.payment_method_id == payment_method.id


def test_process_payment_automatic_lookup_no_active_cart(
    payment_service, user, payment_method
):
    payment_method.is_default = True
    db.session.commit()

    # User has no cart at all
    with pytest.raises(CartNotFoundError) as exc:
        payment_service.process_payment(user_id=user.id)
    assert "Active cart not found" in str(exc.value)


def test_process_payment_automatic_lookup_no_payment_method(
    payment_service, user, cart
):
    # User has a cart but no payment method
    with pytest.raises(PaymentMethodNotFoundError) as exc:
        payment_service.process_payment(user_id=user.id)
    assert "No payment method found for user" in str(exc.value)


def test_process_payment_different_currency(user, cart, payment_method):
    class EURCartTotalCalculator:
        def calculate_total(self, cart_id):
            return CartTotal(amount=Decimal("85.00"), currency="EUR")

    service = PaymentService(
        payment_provider=MockPaymentProvider(),
        cart_total_calculator=EURCartTotalCalculator(),
    )

    result = service.process_payment(user_id=user.id)

    assert result.status == PaymentStatus.COMPLETED
    db_payment = db.session.get(Payment, result.payment_id)
    assert db_payment.amount == Decimal("85.00")
    assert db_payment.currency == "EUR"

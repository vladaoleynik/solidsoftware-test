from decimal import Decimal
from uuid import uuid4

import pytest

from app.extensions import db
from app.models import Cart, Payment
from app.services.cart_total_calculator import StubCartTotalCalculator
from app.services.payment_provider import MockPaymentProvider
from app.services.payment_service import (
    CartAlreadyCheckedOutError,
    CartDoesNotBelongToUserError,
    CartNotFoundError,
    CartStatus,
    PaymentMethodDoesNotBelongToUserError,
    PaymentMethodNotFoundError,
    PaymentService,
    PaymentStatus,
)
from tests.factories import CartFactory, UserFactory, UserPaymentMethodFactory


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
    return CartFactory(user=user)


@pytest.fixture
def payment_method(user):
    return UserPaymentMethodFactory(user=user)


def test_process_payment_success(payment_service, user, cart, payment_method):
    result = payment_service.process_payment(
        user_id=user.id, cart_id=cart.id, payment_method_id=payment_method.id
    )

    assert result.status == PaymentStatus.COMPLETED
    assert result.transaction_id.startswith("txn_")
    assert result.failure_reason is None

    # Verify DB state
    db_payment = db.session.get(Payment, result.payment_id)
    assert db_payment.status == PaymentStatus.COMPLETED
    assert db_payment.amount == Decimal("100.00")

    db_cart = db.session.get(Cart, cart.id)
    assert db_cart.status == CartStatus.CHECKED_OUT


def test_process_payment_failure_insufficient_funds(
    payment_service, user, cart, payment_method
):
    payment_method.provider_token = "pm_mock_insufficient_funds"
    db.session.commit()

    result = payment_service.process_payment(
        user_id=user.id, cart_id=cart.id, payment_method_id=payment_method.id
    )

    assert result.status == PaymentStatus.FAILED
    assert result.failure_reason == "insufficient_funds"

    # Verify DB state
    db_payment = db.session.get(Payment, result.payment_id)
    assert db_payment.status == PaymentStatus.FAILED

    db_cart = db.session.get(Cart, cart.id)
    assert db_cart.status == CartStatus.ACTIVE


def test_process_payment_cart_not_found(payment_service, user, payment_method):
    with pytest.raises(CartNotFoundError):
        payment_service.process_payment(
            user_id=user.id, cart_id=uuid4(), payment_method_id=payment_method.id
        )


def test_process_payment_cart_wrong_user(payment_service, cart, payment_method):
    other_user = UserFactory()

    with pytest.raises(CartDoesNotBelongToUserError):
        payment_service.process_payment(
            user_id=other_user.id, cart_id=cart.id, payment_method_id=payment_method.id
        )


def test_process_payment_cart_already_checked_out(
    payment_service, user, cart, payment_method
):
    cart.status = CartStatus.CHECKED_OUT
    db.session.commit()

    with pytest.raises(CartAlreadyCheckedOutError):
        payment_service.process_payment(
            user_id=user.id, cart_id=cart.id, payment_method_id=payment_method.id
        )


def test_process_payment_method_not_found(payment_service, user, cart):
    with pytest.raises(PaymentMethodNotFoundError):
        payment_service.process_payment(
            user_id=user.id, cart_id=cart.id, payment_method_id=uuid4()
        )


def test_process_payment_method_wrong_user(payment_service, user, cart, payment_method):
    other_user = UserFactory()

    # Create a cart for other_user so we don't fail at cart check
    other_cart = CartFactory(user=other_user)

    with pytest.raises(PaymentMethodDoesNotBelongToUserError):
        payment_service.process_payment(
            user_id=other_user.id,
            cart_id=other_cart.id,
            payment_method_id=payment_method.id,
        )

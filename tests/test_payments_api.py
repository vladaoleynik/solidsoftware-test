from app.models import Cart, Payment
from app.models.enums import CartStatus, PaymentStatus
from tests.factories import (
    CartFactory,
    CartItemFactory,
    UserFactory,
    UserPaymentMethodFactory,
)


def test_checkout_api_success(client, app):
    user = UserFactory()
    cart = CartFactory(user=user)
    CartItemFactory(cart=cart)
    UserPaymentMethodFactory(user=user)

    response = client.post(
        "/api/payments/checkout",
        json={
            "user_id": str(user.id),
        },
    )

    assert response.status_code == 200
    data = response.get_json()
    assert data["status"] == PaymentStatus.COMPLETED
    assert data["transaction_id"].startswith("txn_")
    assert data["failure_reason"] is None

    with app.app_context():
        from app.extensions import db

        db.session.expire_all()
        updated_cart = db.session.get(Cart, cart.id)
        assert updated_cart.status == CartStatus.CHECKED_OUT


def test_checkout_api_failure_insufficient_funds(client, app):
    user = UserFactory()
    cart = CartFactory(user=user)
    CartItemFactory(cart=cart)
    UserPaymentMethodFactory(user=user, provider_token="pm_mock_insufficient_funds")

    response = client.post(
        "/api/payments/checkout",
        json={
            "user_id": str(user.id),
        },
    )

    assert response.status_code == 400
    data = response.get_json()
    assert data["status"] == PaymentStatus.FAILED
    assert data["failure_reason"] == "insufficient_funds"


def test_checkout_api_invalid_uuid(client):
    response = client.post(
        "/api/payments/checkout",
        json={
            "user_id": "not-a-uuid",
        },
    )
    assert response.status_code == 400
    assert "Invalid input" in response.get_json()["error"]


def test_checkout_api_missing_user_id(client):
    response = client.post("/api/payments/checkout", json={})
    assert response.status_code == 400
    assert "Invalid input" in response.get_json()["error"]


def test_checkout_api_automatic_lookup(client):
    user = UserFactory()
    cart = CartFactory(user=user)
    CartItemFactory(cart=cart)
    UserPaymentMethodFactory(user=user, is_default=True)

    response = client.post("/api/payments/checkout", json={"user_id": str(user.id)})

    assert response.status_code == 200
    data = response.get_json()
    assert data["status"] == PaymentStatus.COMPLETED


def test_checkout_api_empty_cart(client):
    user = UserFactory()
    CartFactory(user=user)
    UserPaymentMethodFactory(user=user)

    response = client.post(
        "/api/payments/checkout",
        json={
            "user_id": str(user.id),
        },
    )

    assert response.status_code == 400
    assert "Cart is empty" in response.get_json()["error"]


def test_checkout_api_cart_not_found(client):
    user = UserFactory()
    UserPaymentMethodFactory(user=user)

    response = client.post(
        "/api/payments/checkout",
        json={
            "user_id": str(user.id),
        },
    )

    assert response.status_code == 404
    assert "Active cart not found" in response.get_json()["error"]


def test_checkout_api_cart_wrong_user(client):
    user = UserFactory()
    other_user = UserFactory()
    CartFactory(user=other_user)
    UserPaymentMethodFactory(user=user)

    response = client.post(
        "/api/payments/checkout",
        json={
            "user_id": str(user.id),
        },
    )

    assert response.status_code == 404
    assert "Active cart not found" in response.get_json()["error"]


def test_checkout_api_cart_already_checked_out(client):
    user = UserFactory()
    cart = CartFactory(user=user, status=CartStatus.CHECKED_OUT)
    CartItemFactory(cart=cart)
    UserPaymentMethodFactory(user=user)

    response = client.post(
        "/api/payments/checkout",
        json={
            "user_id": str(user.id),
        },
    )

    assert response.status_code == 404
    assert "Active cart not found" in response.get_json()["error"]


def test_checkout_api_payment_method_not_found(client):
    user = UserFactory()
    cart = CartFactory(user=user)
    CartItemFactory(cart=cart)

    response = client.post(
        "/api/payments/checkout",
        json={
            "user_id": str(user.id),
        },
    )

    assert response.status_code == 404
    assert "No payment method found for user" in response.get_json()["error"]


def test_checkout_api_payment_method_wrong_user(client):
    user = UserFactory()
    other_user = UserFactory()
    cart = CartFactory(user=user)
    CartItemFactory(cart=cart)
    UserPaymentMethodFactory(user=other_user)

    response = client.post(
        "/api/payments/checkout",
        json={
            "user_id": str(user.id),
        },
    )

    assert response.status_code == 404
    assert "No payment method found for user" in response.get_json()["error"]


def test_checkout_api_payment_already_in_progress(client):
    user = UserFactory()
    cart = CartFactory(user=user)
    CartItemFactory(cart=cart)
    payment_method = UserPaymentMethodFactory(user=user)

    # Create a pending payment manually
    from decimal import Decimal

    from app.extensions import db
    from app.models.enums import PaymentStatus

    with client.application.app_context():
        payment = Payment(
            user_id=user.id,
            cart_id=cart.id,
            payment_method_id=payment_method.id,
            amount=Decimal("100.00"),
            status=PaymentStatus.PENDING,
        )
        db.session.add(payment)
        db.session.commit()

    response = client.post(
        "/api/payments/checkout",
        json={
            "user_id": str(user.id),
        },
    )

    assert response.status_code == 400
    assert "Payment already in progress" in response.get_json()["error"]


def test_checkout_api_empty_body(client):
    response = client.post(
        "/api/payments/checkout", data=None, content_type="application/json"
    )
    assert response.status_code == 400
    assert "Invalid request format" in response.get_json()["error"]

    # Let's try sending something that isn't JSON
    response = client.post(
        "/api/payments/checkout", data="not json", content_type="application/json"
    )
    assert response.status_code == 400
    assert "Invalid request format" in response.get_json()["error"]

from decimal import Decimal

from app.services.payment_provider import MockPaymentProvider


def test_mock_payment_provider_success():
    provider = MockPaymentProvider()
    result = provider.process_payment("pm_mock_success", Decimal("100.00"), "USD")

    assert result.success is True
    assert result.transaction_id.startswith("txn_")
    assert result.failure_reason is None


def test_mock_payment_provider_insufficient_funds():
    provider = MockPaymentProvider()
    result = provider.process_payment(
        "pm_mock_insufficient_funds", Decimal("100.00"), "USD"
    )

    assert result.success is False
    assert result.transaction_id is None
    assert result.failure_reason == "insufficient_funds"


def test_mock_payment_provider_provider_error():
    provider = MockPaymentProvider()
    result = provider.process_payment(
        "pm_mock_provider_error", Decimal("100.00"), "USD"
    )

    assert result.success is False
    assert result.transaction_id is None
    assert result.failure_reason == "provider_error"


def test_mock_payment_provider_unknown_token():
    provider = MockPaymentProvider()
    result = provider.process_payment("pm_unknown", Decimal("100.00"), "USD")

    assert result.success is False
    assert result.transaction_id is None
    assert result.failure_reason == "unknown_payment_method"

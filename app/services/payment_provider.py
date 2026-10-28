from dataclasses import dataclass
from decimal import Decimal
from typing import Protocol
from uuid import uuid4


@dataclass(frozen=True)
class PaymentResult:
    success: bool
    transaction_id: str | None = None
    failure_reason: str | None = None


class PaymentProvider(Protocol):
    def process_payment(
        self,
        provider_token: str,
        amount: Decimal,
        currency: str,
    ) -> PaymentResult:
        """Process a payment through the payment provider."""


class MockPaymentProvider:
    """Mock payment provider for testing.

    Behavior based on provider_token:
    - "pm_mock_success" succeeds
    - "pm_mock_insufficient_funds" fails with insufficient_funds
    - "pm_mock_provider_error" fails with provider_error
    - Any other token fails with unknown_payment_method
    """

    def process_payment(
        self,
        provider_token: str,
        amount: Decimal,
        currency: str,
    ) -> PaymentResult:
        if provider_token == "pm_mock_success":
            return PaymentResult(
                success=True,
                transaction_id=f"txn_{uuid4().hex[:16]}",
            )

        if provider_token == "pm_mock_insufficient_funds":
            return PaymentResult(
                success=False,
                failure_reason="insufficient_funds",
            )

        if provider_token == "pm_mock_provider_error":
            return PaymentResult(
                success=False,
                failure_reason="provider_error",
            )

        return PaymentResult(
            success=False,
            failure_reason="unknown_payment_method",
        )

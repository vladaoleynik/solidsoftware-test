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
        self, provider_token: str, amount: Decimal, currency: str
    ) -> PaymentResult:
        """Process a payment through the payment provider."""


class MockPaymentProvider:
    """
    Mock payment provider for testing.

    Behavior based on provider_token:
    - Tokens ending with "fail" will fail
    - All other tokens will succeed
    """

    def process_payment(
        self, provider_token: str, amount: Decimal, currency: str
    ) -> PaymentResult:
        # Simulate payment failure for tokens ending with "fail"
        if provider_token.endswith("fail"):
            return PaymentResult(
                success=False,
                transaction_id=None,
                failure_reason="Payment declined by provider",
            )

        # Simulate successful payment
        return PaymentResult(
            success=True, transaction_id=f"txn_{uuid4().hex[:16]}", failure_reason=None
        )

from dataclasses import dataclass
from decimal import Decimal
from typing import Protocol
from uuid import UUID


@dataclass(frozen=True)
class CartTotal:
    amount: Decimal
    currency: str


class CartTotalCalculator(Protocol):
    def calculate_total(self, cart_id: UUID) -> CartTotal:
        """Return the amount and currency that must be charged for the cart."""


class StubCartTotalCalculator:
    """Placeholder for the existing total calculation service.

    The real implementation is outside the scope of this task.
    """

    def calculate_total(self, cart_id: UUID) -> CartTotal:
        return CartTotal(amount=Decimal("100.00"), currency="USD")

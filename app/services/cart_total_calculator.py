from decimal import Decimal
from typing import Protocol
from uuid import UUID


class CartTotalCalculator(Protocol):
    def calculate_total(self, cart_id: UUID) -> Decimal:
        """Return the amount that must be charged for the cart."""


class StubCartTotalCalculator:
    """Placeholder for the existing total calculation service.

    The real implementation is outside the scope of this task.
    """

    def calculate_total(self, cart_id: UUID) -> Decimal:
        return Decimal("100.00")

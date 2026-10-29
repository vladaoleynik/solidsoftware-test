from uuid import UUID

from flask import Blueprint, Response, jsonify, request
from pydantic import BaseModel, ValidationError

from app.models.enums import PaymentStatus
from app.services.cart_total_calculator import StubCartTotalCalculator
from app.services.payment_provider import MockPaymentProvider
from app.services.payment_service import (
    PaymentError,
    PaymentService,
)

payments_bp = Blueprint("payments", __name__, url_prefix="/api/payments")


class CheckoutRequest(BaseModel):
    user_id: UUID


def get_payment_service() -> PaymentService:
    """Dependency injection helper for PaymentService."""
    # In a real app, this could be resolved from a DI container
    # or initialized using app configuration.
    return PaymentService(
        payment_provider=MockPaymentProvider(),
        cart_total_calculator=StubCartTotalCalculator(),
    )


@payments_bp.post("/checkout")
def checkout() -> tuple[Response, int]:
    try:
        data = request.get_json()
    except Exception:
        return jsonify({"error": "Invalid request format"}), 400

    if data is None:
        return jsonify({"error": "Missing request body"}), 400

    try:
        checkout_data = CheckoutRequest(**data)
    except ValidationError as e:
        return jsonify({"error": "Invalid input", "details": e.errors()}), 400

    # In a real app, we should use the authenticated user's ID
    # For now, we use the one from request.
    user_id = checkout_data.user_id

    service = get_payment_service()

    try:
        result = service.process_payment(
            user_id=user_id,
        )

        status_code = 200 if result.status == PaymentStatus.COMPLETED else 400
        return jsonify(
            {
                "payment_id": str(result.payment_id),
                "status": str(result.status),
                "transaction_id": result.transaction_id,
                "failure_reason": result.failure_reason,
            }
        ), status_code

    except PaymentError as e:
        return jsonify({"error": e.message}), e.status_code
    except Exception:
        return jsonify({"error": "Internal server error"}), 500

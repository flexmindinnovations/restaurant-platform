import uuid
from decimal import Decimal
from typing import Any

from modules.payments.application.ports.payment_gateway import PaymentGateway
from shared.domain.exceptions import ValidationException


class MockGateway(PaymentGateway):
    def __init__(self, should_fail: bool = False, failure_reason: str = "Card declined") -> None:
        self.should_fail = should_fail
        self.failure_reason = failure_reason

    async def authorize(
        self,
        amount: Decimal,
        currency: str,
        payment_method_token: str,
        customer_id: uuid.UUID,
    ) -> tuple[str, dict[str, Any]]:
        if self.should_fail or payment_method_token == "tok_fail":
            raise ValidationException(self.failure_reason)

        tx_id = f"pi_mock_{uuid.uuid4().hex[:8]}"
        response = {
            "id": tx_id,
            "status": "requires_capture",
            "amount": int(amount * 100),
            "currency": currency,
            "payment_method": "pm_mock_visa",
            "customer": str(customer_id),
            "charge_method": "manual",
        }
        return tx_id, response

    async def capture(self, gateway_transaction_id: str) -> dict[str, Any]:
        if self.should_fail:
            raise ValidationException("Capture failed")

        return {
            "id": gateway_transaction_id,
            "status": "succeeded",
            "captured": True,
        }

    async def void(self, gateway_transaction_id: str) -> dict[str, Any]:
        if self.should_fail:
            raise ValidationException("Cancel/Void failed")

        return {
            "id": gateway_transaction_id,
            "status": "canceled",
        }

    async def refund(self, gateway_transaction_id: str, amount: Decimal) -> dict[str, Any]:
        if self.should_fail:
            raise ValidationException("Refund failed")

        return {
            "id": f"re_mock_{uuid.uuid4().hex[:8]}",
            "payment_intent": gateway_transaction_id,
            "amount": int(amount * 100),
            "status": "succeeded",
        }

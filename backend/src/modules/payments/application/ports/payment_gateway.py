import abc
import uuid
from decimal import Decimal
from typing import Any


class PaymentGateway(abc.ABC):
    @abc.abstractmethod
    async def authorize(
        self,
        amount: Decimal,
        currency: str,
        payment_method_token: str,
        customer_id: uuid.UUID,
    ) -> tuple[str, dict[str, Any]]:
        """Authorize a payment.

        Returns tuple of (gateway_transaction_id, gateway_response).
        """

    @abc.abstractmethod
    async def capture(self, gateway_transaction_id: str) -> dict[str, Any]:
        """Capture an authorized payment.

        Returns gateway_response.
        """

    @abc.abstractmethod
    async def void(self, gateway_transaction_id: str) -> dict[str, Any]:
        """Void an authorized payment.

        Returns gateway_response.
        """

    @abc.abstractmethod
    async def refund(self, gateway_transaction_id: str, amount: Decimal) -> dict[str, Any]:
        """Refund a captured payment.

        Returns gateway_response.
        """

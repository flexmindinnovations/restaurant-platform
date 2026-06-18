import asyncio
import uuid
from decimal import Decimal
from typing import Any

import stripe

from modules.payments.application.ports.payment_gateway import PaymentGateway
from shared.domain.exceptions import ValidationException


class StripeGateway(PaymentGateway):
    def __init__(self, secret_key: str) -> None:
        self._secret_key = secret_key

    def _get_client(self) -> stripe.StripeClient:
        # Create a client instance with the secret key
        return stripe.StripeClient(self._secret_key)

    async def authorize(
        self,
        amount: Decimal,
        currency: str,
        payment_method_token: str,
        customer_id: uuid.UUID,
    ) -> tuple[str, dict[str, Any]]:
        amount_cents = int(amount * 100)
        client = self._get_client()

        def _call() -> stripe.PaymentIntent:
            return client.payment_intents.create(
                params={
                    "amount": amount_cents,
                    "currency": currency.lower(),
                    "payment_method": payment_method_token,
                    "capture_method": "manual",
                    "confirm": True,
                    "automatic_payment_methods": {"enabled": True, "allow_redirects": "never"},
                    "metadata": {"customer_id": str(customer_id)},
                }
            )

        try:
            intent = await asyncio.to_thread(_call)
            return intent.id, intent.to_dict()
        except Exception as e:
            raise ValidationException(f"Stripe authorize failed: {e}") from e

    async def capture(self, gateway_transaction_id: str) -> dict[str, Any]:
        client = self._get_client()

        def _call() -> stripe.PaymentIntent:
            return client.payment_intents.capture(
                intent=gateway_transaction_id,
            )

        try:
            intent = await asyncio.to_thread(_call)
            return intent.to_dict()
        except Exception as e:
            raise ValidationException(f"Stripe capture failed: {e}") from e

    async def void(self, gateway_transaction_id: str) -> dict[str, Any]:
        client = self._get_client()

        def _call() -> stripe.PaymentIntent:
            return client.payment_intents.cancel(
                intent=gateway_transaction_id,
            )

        try:
            intent = await asyncio.to_thread(_call)
            return intent.to_dict()
        except Exception as e:
            raise ValidationException(f"Stripe void failed: {e}") from e

    async def refund(self, gateway_transaction_id: str, amount: Decimal) -> dict[str, Any]:
        amount_cents = int(amount * 100)
        client = self._get_client()

        def _call() -> stripe.Refund:
            return client.refunds.create(
                params={
                    "payment_intent": gateway_transaction_id,
                    "amount": amount_cents,
                }
            )

        try:
            refund_obj = await asyncio.to_thread(_call)
            return refund_obj.to_dict()
        except Exception as e:
            raise ValidationException(f"Stripe refund failed: {e}") from e

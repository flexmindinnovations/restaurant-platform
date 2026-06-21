import uuid
from decimal import Decimal

import pytest

from modules.payments.domain.entities.payment import Payment
from modules.payments.domain.value_objects.payment_status import PaymentStatus
from shared.domain.exceptions import ValidationException
from shared.domain.value_objects import Money


def test_payment_initiation():
    order_id = uuid.uuid4()
    customer_id = uuid.uuid4()
    restaurant_id = uuid.uuid4()
    amount = Money(Decimal("25.50"), "INR")

    payment = Payment.initiate(
        order_id=order_id,
        customer_id=customer_id,
        restaurant_id=restaurant_id,
        amount=amount,
        payment_method_type="CARD",
    )

    assert payment.status == PaymentStatus.PENDING
    assert payment.amount == amount
    assert payment.order_id == order_id


def test_payment_state_transitions():
    p = Payment.initiate(uuid.uuid4(), uuid.uuid4(), uuid.uuid4(), Money(Decimal("10.00"), "INR"), "CARD")

    p.authorize("tx_123", {"brand": "Visa"})
    assert p.status == PaymentStatus.AUTHORIZED
    assert p.gateway_transaction_id == "tx_123"

    p.capture({"status": "succeeded"})
    assert p.status == PaymentStatus.CAPTURED
    assert p.captured_at is not None

    p.refund(Decimal("10.00"), {"status": "refunded"})
    assert p.status == PaymentStatus.REFUNDED
    assert p.refunded_at is not None


def test_invalid_payment_state_transitions():
    p = Payment.initiate(uuid.uuid4(), uuid.uuid4(), uuid.uuid4(), Money(Decimal("10.00"), "INR"), "CARD")

    with pytest.raises(ValidationException):
        p.capture({"status": "failed"})


def test_void_payment():
    p = Payment.initiate(uuid.uuid4(), uuid.uuid4(), uuid.uuid4(), Money(Decimal("10.00"), "INR"), "CARD")
    p.authorize("tx_123", {})
    p.void({"status": "voided"})
    assert p.status == PaymentStatus.VOIDED

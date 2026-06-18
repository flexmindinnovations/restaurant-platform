from decimal import Decimal

from shared.domain.value_objects import Money


def create_price(amount: Decimal, currency: str = "USD") -> Money:
    if amount <= 0:
        raise ValueError("Price must be greater than zero")
    return Money(amount=amount, currency=currency)

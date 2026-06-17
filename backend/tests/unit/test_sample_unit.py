from decimal import Decimal

import pytest

from shared.domain.value_objects import Money


def test_money_addition() -> None:
    """Test that two Money objects of the same currency can be added."""
    m1 = Money(Decimal("10.00"), "USD")
    m2 = Money(Decimal("5.50"), "USD")
    result = m1.add(m2)
    assert result.amount == Decimal("15.50")
    assert result.currency == "USD"


def test_money_negative_amount_raises_value_error() -> None:
    """Test that creating a Money object with a negative amount raises ValueError."""
    with pytest.raises(ValueError, match="Money amount cannot be negative"):
        Money(Decimal("-1.00"), "USD")

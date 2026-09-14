from decimal import Decimal
import pytest

from src.bounded_contexts.menu_catalog.domain.exceptions.menu_exceptions import (
    InvalidPriceError,
)
from src.bounded_contexts.menu_catalog.domain.value_objects.money import (
    CURRENCY,
    Money,
)


def test_money_creation_with_decimal() -> None:
    money = Money(Decimal("10.50"), CURRENCY.EUR)

    assert money.amount == Decimal("10.50")
    assert money.currency == CURRENCY.EUR


def test_money_auto_converts_float_and_str_to_decimal() -> None:
    money_from_str = Money("12.00", CURRENCY.EUR)  # type: ignore[arg-type]
    money_from_float = Money(15.5, CURRENCY.EUR)  # type: ignore[arg-type]

    assert isinstance(money_from_str.amount, Decimal)
    assert money_from_str.amount == Decimal("12.00")
    assert isinstance(money_from_float.amount, Decimal)
    assert money_from_float.amount == Decimal("15.5")


def test_money_raises_error_for_negative_amount() -> None:
    with pytest.raises(InvalidPriceError, match="Amount cannot be negative"):
        Money(Decimal("-5.00"), CURRENCY.EUR)


def test_money_addition_same_currency() -> None:
    m1 = Money(Decimal("10.25"), CURRENCY.EUR)
    m2 = Money(Decimal("5.75"), CURRENCY.EUR)

    result = m1 + m2

    assert result.amount == Decimal("16.00")
    assert result.currency == CURRENCY.EUR


def test_money_addition_different_currency_raises_error() -> None:
    m1 = Money(Decimal("10.00"), CURRENCY.EUR)
    m2 = Money(Decimal("10.00"), CURRENCY.USD)

    with pytest.raises(ValueError, match="Cannot add Money with different currencies"):
        _ = m1 + m2


def test_money_string_representation() -> None:
    money = Money(Decimal("10.50"), CURRENCY.EUR)

    assert str(money) == "10.50 EUR"

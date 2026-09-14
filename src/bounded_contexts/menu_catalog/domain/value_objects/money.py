# domain\value_objects\money.py

from dataclasses import dataclass
from decimal import Decimal
from enum import Enum

from src.bounded_contexts.menu_catalog.domain.exceptions.menu_exceptions import (
    InvalidPriceError,
)


class CURRENCY(Enum):
    EUR = "EUR"
    USD = "USD"


@dataclass(frozen=True)
class Money:
    amount: Decimal
    currency: CURRENCY

    def __post_init__(self) -> None:

        """ Convert to Decimal if float,str is passed """

        if not isinstance(self.amount, Decimal):
            object.__setattr__(self, "amount", Decimal(str(self.amount)))

        if self.amount < Decimal("0"):
            msg = f"Amount cannot be negative: {self.amount}"
            raise InvalidPriceError(msg)

    def __add__(self, other: "Money") -> "Money":
        if self.currency != other.currency:
            msg = (
                "Cannot add Money with different currencies: "
                f"{self.currency} vs {other.currency}"
            )
            raise ValueError(msg)

        return Money(self.amount + other.amount, self.currency)

    def __str__(self) -> str:
        return f"{self.amount} {self.currency.value}"

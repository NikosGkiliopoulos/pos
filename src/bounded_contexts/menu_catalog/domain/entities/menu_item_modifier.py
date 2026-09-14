# domain/entities/menu_item_modifier.py

from dataclasses import dataclass

from src.bounded_contexts.menu_catalog.domain.value_objects.identifiers import (
    ModifierId,)

from src.bounded_contexts.menu_catalog.domain.value_objects.money import Money
from src.bounded_contexts.menu_catalog.domain.exceptions.menu_exceptions import (
    EmptyModifierNameError,)


@dataclass(eq=False)
class MenuItemModifier:
    """
    Child entity representing an optional add-on for a MenuItem
    (e.g. "Extra cheese", "No onion").

    Lives only within the MenuItem aggregate boundary — has no
    independent repository of its own.
    """
    modifier_id: ModifierId
    name: str
    price_addition: Money

    def __post_init__(self) -> None:
        if not self.name.strip():
            raise EmptyModifierNameError("Modifier name cannot be empty")

    def rename(self, new_name: str) -> None:
        if not new_name.strip():
            raise EmptyModifierNameError("Modifier name cannot be empty")
        self.name = new_name

    def change_price_addition(self, new_price_addition: Money) -> None:
        self.price_addition = new_price_addition

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, MenuItemModifier):
            return NotImplemented
        return self.modifier_id == other.modifier_id

    def __hash__(self) -> int:
        return hash(self.modifier_id)

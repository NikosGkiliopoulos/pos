# domain/entities/menu_item_variant.py

from dataclasses import dataclass

from src.bounded_contexts.menu_catalog.domain.value_objects.identifiers import VariantId
from src.bounded_contexts.menu_catalog.domain.value_objects.money import Money
from src.bounded_contexts.menu_catalog.domain.exceptions.menu_exceptions import (
    EmptyVariantNameError,)


@dataclass(eq=False)
class MenuItemVariant:
    """
    Child entity representing a variant option of a MenuItem
    (e.g. "Single" / "Double" for a coffee).

    Lives only within the MenuItem aggregate boundary — has no
    independent repository of its own.
    """
    variant_id: VariantId
    name: str
    price_modifier: Money

    def __post_init__(self) -> None:
        if not self.name.strip():
            raise EmptyVariantNameError("Variant name cannot be empty")

    def rename(self, new_name: str) -> None:
        if not new_name.strip():
            raise EmptyVariantNameError("Variant name cannot be empty")
        self.name = new_name

    def change_price_modifier(self, new_price_modifier: Money) -> None:
        self.price_modifier = new_price_modifier

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, MenuItemVariant):
            return False
        return self.variant_id == other.variant_id

    def __hash__(self) -> int:
        return hash(self.variant_id)

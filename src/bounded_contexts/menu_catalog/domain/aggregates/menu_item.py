from dataclasses import dataclass, field

from src.bounded_contexts.menu_catalog.domain.entities.menu_item_modifier import (
    MenuItemModifier,
)
from src.bounded_contexts.menu_catalog.domain.entities.menu_item_variant import (
    MenuItemVariant,
)
from src.bounded_contexts.menu_catalog.domain.events.menu_events import (
    DomainEvent,
    MenuItemAvailabilityChangedEvent,
    MenuItemCreatedEvent,
    MenuItemModifierAddedEvent,
    MenuItemModifierPriceAdditionUpdatedEvent,
    MenuItemModifierRemovedEvent,
    MenuItemModifierRenamedEvent,
    MenuItemPriceUpdatedEvent,
    MenuItemRecategorizedEvent,
    MenuItemRemovedEvent,
    MenuItemRenamedEvent,
    MenuItemVariantAddedEvent,
    MenuItemVariantPriceModifierUpdatedEvent,
    MenuItemVariantRemovedEvent,
    MenuItemVariantRenamedEvent,
)
from src.bounded_contexts.menu_catalog.domain.exceptions.menu_exceptions import (
    DuplicateModifierNameError,
    DuplicateVariantNameError,
    EmptyMenuItemNameError,
    ModifierNotFoundError,
    VariantNotFoundError,
)
from src.bounded_contexts.menu_catalog.domain.value_objects.identifiers import (
    CategoryId,
    MenuItemId,
    ModifierId,
    VariantId,
)
from src.bounded_contexts.menu_catalog.domain.value_objects.money import Money


@dataclass(eq=False)
class MenuItem:
    """Aggregate Root representing a single menu item (e.g. "Margherita Pizza")."""

    item_id: MenuItemId
    name: str
    base_price: Money
    category_id: CategoryId
    is_available: bool = True
    variants: list[MenuItemVariant] = field(default_factory=list)
    modifiers: list[MenuItemModifier] = field(default_factory=list)
    _events: list[DomainEvent] = field(default_factory=list, init=False, repr=False)

    def __post_init__(self) -> None:
        if not self.name.strip():
            raise EmptyMenuItemNameError("Menu item name cannot be empty")

    @classmethod
    def create(
        cls, name: str, base_price: Money, category_id: CategoryId
    ) -> "MenuItem":
        item_id = MenuItemId.generate()
        item = cls(
            item_id=item_id,
            name=name,
            base_price=base_price,
            category_id=category_id,
        )
        item._events.append(
            MenuItemCreatedEvent(
                item_id=item_id,
                name=name,
                price=base_price,
                category_id=category_id,
            )
        )
        return item

    def rename(self, new_name: str) -> None:
        if not new_name.strip():
            raise EmptyMenuItemNameError("Menu item name cannot be empty")
        if self.name == new_name:
            return

        old_name = self.name
        self.name = new_name
        self._events.append(
            MenuItemRenamedEvent(
                item_id=self.item_id,
                old_name=old_name,
                new_name=new_name,
            )
        )

    def change_category(self, new_category_id: CategoryId) -> None:
        if self.category_id == new_category_id:
            return

        old_category_id = self.category_id
        self.category_id = new_category_id
        self._events.append(
            MenuItemRecategorizedEvent(
                item_id=self.item_id,
                old_category_id=old_category_id,
                new_category_id=new_category_id,
            )
        )

    def update_price(self, new_price: Money) -> None:
        if self.base_price == new_price:
            return

        old_price = self.base_price
        self.base_price = new_price
        self._events.append(
            MenuItemPriceUpdatedEvent(
                item_id=self.item_id,
                old_price=old_price,
                new_price=new_price,
            )
        )

    def set_availability(self, is_available: bool) -> None:
        if self.is_available == is_available:
            return

        self.is_available = is_available
        self._events.append(
            MenuItemAvailabilityChangedEvent(
                item_id=self.item_id, is_available=is_available
            )
        )

    def remove(self) -> None:
        self._events.append(MenuItemRemovedEvent(item_id=self.item_id))

    # --- Variant management ---

    def add_variant(self, name: str, price_modifier: Money) -> VariantId:
        if any(v.name == name for v in self.variants):
            raise DuplicateVariantNameError(
                f"Variant '{name}' already exists on this menu item"
            )
        variant_id = VariantId.generate()
        variant = MenuItemVariant(
            variant_id=variant_id, name=name, price_modifier=price_modifier
        )
        self.variants.append(variant)
        self._events.append(
            MenuItemVariantAddedEvent(
                item_id=self.item_id,
                variant_id=variant_id,
                name=name,
                price_modifier=price_modifier,
            )
        )
        return variant_id

    def update_variant(
        self, variant_id: VariantId, new_name: str, new_price_modifier: Money
    ) -> None:
        variant = self._find_variant(variant_id)

        if variant.name != new_name:
            if any(v.name == new_name for v in self.variants):
                raise DuplicateVariantNameError(
                    f"Variant '{new_name}' already exists on this menu item"
                )
            old_name = variant.name
            variant.rename(new_name)
            self._events.append(
                MenuItemVariantRenamedEvent(
                    item_id=self.item_id,
                    variant_id=variant_id,
                    old_name=old_name,
                    new_name=new_name,
                )
            )

        if variant.price_modifier != new_price_modifier:
            old_price_modifier = variant.price_modifier
            variant.change_price_modifier(new_price_modifier)
            self._events.append(
                MenuItemVariantPriceModifierUpdatedEvent(
                    item_id=self.item_id,
                    variant_id=variant_id,
                    old_price_modifier=old_price_modifier,
                    new_price_modifier=new_price_modifier,
                )
            )

    def remove_variant(self, variant_id: VariantId) -> None:
        variant = self._find_variant(variant_id)
        self.variants.remove(variant)
        self._events.append(
            MenuItemVariantRemovedEvent(item_id=self.item_id, variant_id=variant_id)
        )

    def get_price_for_variant(self, variant_id: VariantId) -> Money:
        variant = self._find_variant(variant_id)
        return self.base_price + variant.price_modifier

    def _find_variant(self, variant_id: VariantId) -> MenuItemVariant:
        for variant in self.variants:
            if variant.variant_id == variant_id:
                return variant
        raise VariantNotFoundError(f"Variant {variant_id} not found on this menu item")

    # --- Modifier management ---

    def add_modifier(self, name: str, price_addition: Money) -> ModifierId:
        if any(m.name == name for m in self.modifiers):
            raise DuplicateModifierNameError(
                f"Modifier '{name}' already exists on this menu item"
            )
        modifier_id = ModifierId.generate()
        modifier = MenuItemModifier(
            modifier_id=modifier_id, name=name, price_addition=price_addition
        )
        self.modifiers.append(modifier)
        self._events.append(
            MenuItemModifierAddedEvent(
                item_id=self.item_id,
                modifier_id=modifier_id,
                name=name,
                price_addition=price_addition,
            )
        )
        return modifier_id

    def update_modifier(
        self, modifier_id: ModifierId, new_name: str, new_price_addition: Money
    ) -> None:
        modifier = self._find_modifier(modifier_id)

        if modifier.name != new_name:
            if any(m.name == new_name for m in self.modifiers):
                raise DuplicateModifierNameError(
                    f"Modifier '{new_name}' already exists on this menu item"
                )
            old_name = modifier.name
            modifier.rename(new_name)
            self._events.append(
                MenuItemModifierRenamedEvent(
                    item_id=self.item_id,
                    modifier_id=modifier_id,
                    old_name=old_name,
                    new_name=new_name,
                )
            )

        if modifier.price_addition != new_price_addition:
            old_price_addition = modifier.price_addition
            modifier.change_price_addition(new_price_addition)
            self._events.append(
                MenuItemModifierPriceAdditionUpdatedEvent(
                    item_id=self.item_id,
                    modifier_id=modifier_id,
                    old_price_addition=old_price_addition,
                    new_price_addition=new_price_addition,
                )
            )

    def remove_modifier(self, modifier_id: ModifierId) -> None:
        modifier = self._find_modifier(modifier_id)
        self.modifiers.remove(modifier)
        self._events.append(
            MenuItemModifierRemovedEvent(item_id=self.item_id, modifier_id=modifier_id)
        )

    def _find_modifier(self, modifier_id: ModifierId) -> MenuItemModifier:
        for modifier in self.modifiers:
            if modifier.modifier_id == modifier_id:
                return modifier
        raise ModifierNotFoundError(
            f"Modifier {modifier_id} not found on this menu item"
        )

    # --- Events ---

    def collect_events(self) -> list[DomainEvent]:
        events = list(self._events)
        self._events.clear()
        return events

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, MenuItem):
            return False
        return self.item_id == other.item_id

    def __hash__(self) -> int:
        return hash(self.item_id)

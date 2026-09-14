# domain/events/menu_events.py

from dataclasses import dataclass, field
from datetime import datetime, timezone

from src.bounded_contexts.menu_catalog.domain.value_objects.identifiers import (
    CategoryId,
    MenuItemId,
    ModifierId,
    VariantId,
)
from src.bounded_contexts.menu_catalog.domain.value_objects.money import Money


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


@dataclass(frozen=True, kw_only=True)
class DomainEvent:
    """Base class for all domain events in this context."""
    occurred_at: datetime = field(default_factory=_utc_now)


# --- MenuItem events ---

@dataclass(frozen=True, kw_only=True)
class MenuItemCreatedEvent(DomainEvent):
    item_id: MenuItemId
    name: str
    price: Money
    category_id: CategoryId


@dataclass(frozen=True, kw_only=True)
class MenuItemRenamedEvent(DomainEvent):
    item_id: MenuItemId
    old_name: str
    new_name: str


@dataclass(frozen=True, kw_only=True)
class MenuItemRecategorizedEvent(DomainEvent):
    item_id: MenuItemId
    old_category_id: CategoryId
    new_category_id: CategoryId


@dataclass(frozen=True, kw_only=True)
class MenuItemPriceUpdatedEvent(DomainEvent):
    item_id: MenuItemId
    old_price: Money
    new_price: Money


@dataclass(frozen=True, kw_only=True)
class MenuItemAvailabilityChangedEvent(DomainEvent):
    item_id: MenuItemId
    is_available: bool


@dataclass(frozen=True, kw_only=True)
class MenuItemRemovedEvent(DomainEvent):
    item_id: MenuItemId


# --- Category events ---

@dataclass(frozen=True, kw_only=True)
class CategoryCreatedEvent(DomainEvent):
    category_id: CategoryId
    name: str


@dataclass(frozen=True, kw_only=True)
class CategoryRenamedEvent(DomainEvent):
    category_id: CategoryId
    old_name: str
    new_name: str


@dataclass(frozen=True, kw_only=True)
class CategoryRemovedEvent(DomainEvent):
    category_id: CategoryId


# --- Variant events ---

@dataclass(frozen=True, kw_only=True)
class MenuItemVariantAddedEvent(DomainEvent):
    item_id: MenuItemId
    variant_id: VariantId
    name: str
    price_modifier: Money


@dataclass(frozen=True, kw_only=True)
class MenuItemVariantRemovedEvent(DomainEvent):
    item_id: MenuItemId
    variant_id: VariantId


@dataclass(frozen=True, kw_only=True)
class MenuItemVariantRenamedEvent(DomainEvent):
    item_id: MenuItemId
    variant_id: VariantId
    old_name: str
    new_name: str


@dataclass(frozen=True, kw_only=True)
class MenuItemVariantPriceModifierUpdatedEvent(DomainEvent):
    item_id: MenuItemId
    variant_id: VariantId
    old_price_modifier: Money
    new_price_modifier: Money


# --- Modifier events ---

@dataclass(frozen=True, kw_only=True)
class MenuItemModifierAddedEvent(DomainEvent):
    item_id: MenuItemId
    modifier_id: ModifierId
    name: str
    price_addition: Money


@dataclass(frozen=True, kw_only=True)
class MenuItemModifierRemovedEvent(DomainEvent):
    item_id: MenuItemId
    modifier_id: ModifierId


@dataclass(frozen=True, kw_only=True)
class MenuItemModifierRenamedEvent(DomainEvent):
    item_id: MenuItemId
    modifier_id: ModifierId
    old_name: str
    new_name: str


@dataclass(frozen=True, kw_only=True)
class MenuItemModifierPriceAdditionUpdatedEvent(DomainEvent):
    item_id: MenuItemId
    modifier_id: ModifierId
    old_price_addition: Money
    new_price_addition: Money

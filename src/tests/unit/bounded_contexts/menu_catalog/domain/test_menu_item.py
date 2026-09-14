from decimal import Decimal
import pytest

from src.bounded_contexts.menu_catalog.domain.aggregates.menu_item import MenuItem
from src.bounded_contexts.menu_catalog.domain.events.menu_events import (
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
    ModifierId,
    VariantId,
)
from src.bounded_contexts.menu_catalog.domain.value_objects.money import (
    CURRENCY,
    Money,
)


@pytest.fixture()
def category_id() -> CategoryId:
    return CategoryId.generate()


@pytest.fixture()
def base_price() -> Money:
    return Money(Decimal("10.00"), CURRENCY.EUR)


def test_menu_item_creation_emits_event(
    category_id: CategoryId, base_price: Money
) -> None:
    item = MenuItem.create(
        name="Espresso", base_price=base_price, category_id=category_id
    )

    assert item.name == "Espresso"
    assert item.base_price == base_price
    assert item.is_available is True

    events = item.collect_events()
    assert len(events) == 1
    assert isinstance(events[0], MenuItemCreatedEvent)
    assert events[0].item_id == item.item_id


def test_menu_item_empty_name_raises_error(
    category_id: CategoryId, base_price: Money
) -> None:
    with pytest.raises(EmptyMenuItemNameError):
        MenuItem.create(name="   ", base_price=base_price, category_id=category_id)


def test_rename_and_recategorize_item(
    category_id: CategoryId, base_price: Money
) -> None:
    item = MenuItem.create(
        name="Espresso", base_price=base_price, category_id=category_id
    )
    item.collect_events()

    item.rename("Double Espresso")
    new_cat_id = CategoryId.generate()
    item.change_category(new_cat_id)

    assert item.name == "Double Espresso"
    assert item.category_id == new_cat_id

    events = item.collect_events()
    assert len(events) == 2
    assert isinstance(events[0], MenuItemRenamedEvent)
    assert events[0].old_name == "Espresso"
    assert events[0].new_name == "Double Espresso"

    assert isinstance(events[1], MenuItemRecategorizedEvent)
    assert events[1].old_category_id == category_id
    assert events[1].new_category_id == new_cat_id


def test_update_price_emits_event(
    category_id: CategoryId, base_price: Money
) -> None:
    item = MenuItem.create(
        name="Espresso", base_price=base_price, category_id=category_id
    )
    item.collect_events()

    new_price = Money(Decimal("12.00"), CURRENCY.EUR)
    item.update_price(new_price)

    assert item.base_price == new_price
    events = item.collect_events()
    assert len(events) == 1
    assert isinstance(events[0], MenuItemPriceUpdatedEvent)


def test_set_availability(category_id: CategoryId, base_price: Money) -> None:
    item = MenuItem.create(
        name="Espresso", base_price=base_price, category_id=category_id
    )
    item.collect_events()

    item.set_availability(False)
    assert item.is_available is False

    events = item.collect_events()
    assert len(events) == 1
    assert isinstance(events[0], MenuItemAvailabilityChangedEvent)


def test_remove_menu_item_emits_event(
    category_id: CategoryId, base_price: Money
) -> None:
    item = MenuItem.create(
        name="Espresso", base_price=base_price, category_id=category_id
    )
    item.collect_events()

    item.remove()

    events = item.collect_events()
    assert len(events) == 1
    assert isinstance(events[0], MenuItemRemovedEvent)


def test_add_and_update_variant(
    category_id: CategoryId, base_price: Money
) -> None:
    item = MenuItem.create(
        name="Espresso", base_price=base_price, category_id=category_id
    )
    item.collect_events()

    mod_price = Money(Decimal("1.50"), CURRENCY.EUR)
    var_id = item.add_variant(name="Double", price_modifier=mod_price)

    assert len(item.variants) == 1
    assert item.get_price_for_variant(var_id) == Money(Decimal("11.50"), CURRENCY.EUR)

    new_mod_price = Money(Decimal("2.00"), CURRENCY.EUR)
    item.update_variant(
        variant_id=var_id, new_name="Triple", new_price_modifier=new_mod_price
    )

    events = item.collect_events()
    assert isinstance(events[0], MenuItemVariantAddedEvent)
    assert isinstance(events[1], MenuItemVariantRenamedEvent)
    assert isinstance(events[2], MenuItemVariantPriceModifierUpdatedEvent)


def test_add_duplicate_variant_raises_error(
    category_id: CategoryId, base_price: Money
) -> None:
    item = MenuItem.create(
        name="Espresso", base_price=base_price, category_id=category_id
    )
    item.add_variant(name="Double", price_modifier=Money(Decimal("1.00"), CURRENCY.EUR))

    with pytest.raises(DuplicateVariantNameError):
        item.add_variant(name="Double",
                         price_modifier=Money(Decimal("2.00"), CURRENCY.EUR))


def test_remove_variant(category_id: CategoryId, base_price: Money) -> None:
    item = MenuItem.create(
        name="Espresso", base_price=base_price, category_id=category_id
    )
    var_id = item.add_variant(
        name="Double", price_modifier=Money(Decimal("1.00"), CURRENCY.EUR)
    )
    item.collect_events()

    item.remove_variant(var_id)
    assert len(item.variants) == 0

    events = item.collect_events()
    assert len(events) == 1
    assert isinstance(events[0], MenuItemVariantRemovedEvent)


def test_variant_not_found_raises_error(
    category_id: CategoryId, base_price: Money
) -> None:
    item = MenuItem.create(
        name="Espresso", base_price=base_price, category_id=category_id
    )
    fake_variant_id = VariantId.generate()

    with pytest.raises(VariantNotFoundError):
        item.get_price_for_variant(fake_variant_id)


def test_add_update_and_remove_modifier(
    category_id: CategoryId, base_price: Money
) -> None:
    item = MenuItem.create(
        name="Burger", base_price=base_price, category_id=category_id
    )
    item.collect_events()

    mod_id = item.add_modifier(
        name="Extra Cheese", price_addition=Money(Decimal("0.80"), CURRENCY.EUR)
    )
    assert len(item.modifiers) == 1

    item.update_modifier(
        modifier_id=mod_id,
        new_name="Double Cheese",
        new_price_addition=Money(Decimal("1.20"), CURRENCY.EUR),
    )

    item.remove_modifier(mod_id)
    assert len(item.modifiers) == 0

    events = item.collect_events()
    assert len(events) == 4
    assert isinstance(events[0], MenuItemModifierAddedEvent)
    assert isinstance(events[1], MenuItemModifierRenamedEvent)
    assert isinstance(events[2], MenuItemModifierPriceAdditionUpdatedEvent)
    assert isinstance(events[3], MenuItemModifierRemovedEvent)


def test_add_duplicate_modifier_raises_error(
    category_id: CategoryId, base_price: Money
) -> None:
    item = MenuItem.create(
        name="Burger", base_price=base_price, category_id=category_id
    )
    item.add_modifier(
        name="Extra Cheese", price_addition=Money(Decimal("0.80"), CURRENCY.EUR)
    )

    with pytest.raises(DuplicateModifierNameError):
        item.add_modifier(
            name="Extra Cheese", price_addition=Money(Decimal("1.00"), CURRENCY.EUR)
        )


def test_modifier_not_found_raises_error(
    category_id: CategoryId, base_price: Money
) -> None:
    item = MenuItem.create(
        name="Burger", base_price=base_price, category_id=category_id
    )
    fake_mod_id = ModifierId.generate()

    with pytest.raises(ModifierNotFoundError):
        item.remove_modifier(fake_mod_id)


def test_item_equality(category_id: CategoryId, base_price: Money) -> None:
    item1 = MenuItem.create(
        name="Espresso", base_price=base_price, category_id=category_id
    )
    item2 = MenuItem.create(
        name="Espresso", base_price=base_price, category_id=category_id
    )

    assert item1 == item1
    assert item1 != item2
    assert item1 != "not_a_menu_item"

import pytest

from src.bounded_contexts.menu_catalog.domain.aggregates.category import Category
from src.bounded_contexts.menu_catalog.domain.events.menu_events import (
    CategoryCreatedEvent,
    CategoryRemovedEvent,
    CategoryRenamedEvent,
)
from src.bounded_contexts.menu_catalog.domain.exceptions.menu_exceptions import (
    EmptyCategoryNameError,
)
from src.bounded_contexts.menu_catalog.domain.value_objects.identifiers import (
    CategoryId,)


def test_category_creation_emits_created_event() -> None:
    cat_id = CategoryId.generate()
    category = Category.create(category_id=cat_id, name="Beverages", display_order=1)

    assert category.category_id == cat_id
    assert category.name == "Beverages"
    assert category.display_order == 1

    events = category.collect_events()
    assert len(events) == 1
    assert isinstance(events[0], CategoryCreatedEvent)
    assert events[0].category_id == cat_id
    assert events[0].name == "Beverages"


def test_category_rename_emits_renamed_event_with_old_name() -> None:
    cat_id = CategoryId.generate()
    category = Category.create(category_id=cat_id, name="Drinks")
    category.collect_events()  # Clear creation event

    category.rename("Hot Drinks")

    assert category.name == "Hot Drinks"
    events = category.collect_events()
    assert len(events) == 1
    assert isinstance(events[0], CategoryRenamedEvent)
    assert events[0].old_name == "Drinks"
    assert events[0].new_name == "Hot Drinks"


def test_category_rename_same_name_does_not_emit_event() -> None:
    cat_id = CategoryId.generate()
    category = Category.create(category_id=cat_id, name="Drinks")
    category.collect_events()

    category.rename("Drinks")

    assert len(category.collect_events()) == 0


def test_category_rename_empty_raises_error() -> None:
    cat_id = CategoryId.generate()
    category = Category.create(category_id=cat_id, name="Drinks")

    with pytest.raises(EmptyCategoryNameError):
        category.rename("   ")


def test_category_remove_emits_removed_event() -> None:
    cat_id = CategoryId.generate()
    category = Category.create(category_id=cat_id, name="Desserts")
    category.collect_events()

    category.remove()

    events = category.collect_events()
    assert len(events) == 1
    assert isinstance(events[0], CategoryRemovedEvent)
    assert events[0].category_id == cat_id


def test_category_collect_events_clears_queue() -> None:
    cat_id = CategoryId.generate()
    category = Category.create(category_id=cat_id, name="Snacks")

    first_collect = category.collect_events()
    second_collect = category.collect_events()

    assert len(first_collect) == 1
    assert len(second_collect) == 0


def test_category_equality() -> None:
    cat_id = CategoryId.generate()
    cat1 = Category(category_id=cat_id, name="Drinks")
    cat2 = Category(category_id=cat_id, name="Beverages")
    cat3 = Category(category_id=CategoryId.generate(), name="Drinks")

    assert cat1 == cat2
    assert cat1 != cat3
    assert cat1 != "not_a_category"

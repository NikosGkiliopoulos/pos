from decimal import Decimal
import pytest

from src.bounded_contexts.menu_catalog.domain.aggregates.menu_item import MenuItem
from src.bounded_contexts.menu_catalog.domain.value_objects.identifiers import (
    CategoryId,
)
from src.bounded_contexts.menu_catalog.domain.value_objects.money import (
    CURRENCY,
    Money,
)
from src.tests.unit.bounded_contexts.menu_catalog.fakes import FakeUnitOfWork


@pytest.mark.asyncio
async def test_fake_unit_of_work_transaction() -> None:
    uow = FakeUnitOfWork()
    category_id = CategoryId.generate()
    price = Money(Decimal("5.00"), CURRENCY.EUR)

    async with uow:
        item = MenuItem.create(
            name="Freddo Espresso", base_price=price, category_id=category_id
        )
        await uow.menu_items.save(item)
        await uow.commit()

    assert uow.committed is True
    retrieved = await uow.menu_items.find_by_id(item.item_id)
    assert retrieved is not None
    assert retrieved.name == "Freddo Espresso"

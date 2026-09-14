from src.bounded_contexts.menu_catalog.domain.aggregates.category import Category
from src.bounded_contexts.menu_catalog.domain.aggregates.menu_item import MenuItem
from src.bounded_contexts.menu_catalog.domain.repositories.category_repository import (
    CategoryRepository,
)
from src.bounded_contexts.menu_catalog.domain.repositories.menu_item_repository import (
    MenuItemRepository,
)
from src.bounded_contexts.menu_catalog.domain.repositories.unit_of_work import (
    UnitOfWork,
)
from src.bounded_contexts.menu_catalog.domain.value_objects.identifiers import (
    CategoryId,
    MenuItemId,
)


class FakeCategoryRepository(CategoryRepository):
    def __init__(self) -> None:
        self._categories: dict[CategoryId, Category] = {}

    async def save(self, category: Category) -> None:
        self._categories[category.category_id] = category

    async def find_by_id(self, category_id: CategoryId) -> Category | None:
        return self._categories.get(category_id)

    async def exists_by_name(self, name: str) -> bool:
        return any(cat.name == name for cat in self._categories.values())

    async def find_all(self) -> list[Category]:
        return list(self._categories.values())

    async def delete(self, category_id: CategoryId) -> None:
        self._categories.pop(category_id, None)


class FakeMenuItemRepository(MenuItemRepository):
    def __init__(self) -> None:
        self._items: dict[MenuItemId, MenuItem] = {}

    async def save(self, menu_item: MenuItem) -> None:
        self._items[menu_item.item_id] = menu_item

    async def find_by_id(self, item_id: MenuItemId) -> MenuItem | None:
        return self._items.get(item_id)

    async def exists_by_name_in_category(
        self, name: str, category_id: CategoryId
    ) -> bool:
        return any(
            item.name == name and item.category_id == category_id
            for item in self._items.values()
        )

    async def find_by_category(self, category_id: CategoryId) -> list[MenuItem]:
        return [
            item
            for item in self._items.values()
            if item.category_id == category_id
        ]

    async def find_all(self) -> list[MenuItem]:
        return list(self._items.values())

    async def delete(self, item_id: MenuItemId) -> None:
        self._items.pop(item_id, None)


class FakeUnitOfWork(UnitOfWork):
    def __init__(self) -> None:
        self.categories = FakeCategoryRepository()
        self.menu_items = FakeMenuItemRepository()
        self.committed = False

    async def commit(self) -> None:
        self.committed = True

    async def rollback(self) -> None:
        pass

from abc import ABC, abstractmethod
from types import TracebackType
from typing import Self

from src.bounded_contexts.menu_catalog.domain.repositories.category_repository import (
    CategoryRepository,
)
from src.bounded_contexts.menu_catalog.domain.repositories.menu_item_repository import (
    MenuItemRepository,
)


class UnitOfWork(ABC):
    """Abstract Async Interface for the Unit of Work pattern.

    Ensures atomic transactions across repositories and manages the Python
    async context manager lifecycle (__aenter__ / __aexit__).
    """

    categories: CategoryRepository
    menu_items: MenuItemRepository

    async def __aenter__(self) -> Self:
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        if exc_type is not None:
            await self.rollback()

    @abstractmethod
    async def commit(self) -> None:
        """Commit all changes made during the transaction."""
        pass

    @abstractmethod
    async def rollback(self) -> None:
        """Rollback the transaction, discarding uncommitted changes."""
        pass

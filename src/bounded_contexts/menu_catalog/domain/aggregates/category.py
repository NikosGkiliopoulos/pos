from dataclasses import dataclass, field

from src.bounded_contexts.menu_catalog.domain.events.menu_events import (
    CategoryCreatedEvent,
    CategoryRemovedEvent,
    CategoryRenamedEvent,
    DomainEvent,
)
from src.bounded_contexts.menu_catalog.domain.exceptions.menu_exceptions import (
    EmptyCategoryNameError,)

from src.bounded_contexts.menu_catalog.domain.value_objects.identifiers import (
    CategoryId,)


@dataclass(eq=False)
class Category:
    category_id: CategoryId
    name: str
    display_order: int = 0
    _events: list[DomainEvent] = field(default_factory=list, init=False, repr=False)

    def __post_init__(self) -> None:
        if not self.name.strip():
            raise EmptyCategoryNameError("Category name cannot be empty")

    @classmethod
    def create(cls,
               category_id: CategoryId,
               name: str,
               display_order: int = 0) -> "Category":

        category = cls(category_id=category_id, name=name, display_order=display_order)
        category._events.append(
            CategoryCreatedEvent(category_id=category_id, name=name)
        )
        return category

    def rename(self, new_name: str) -> None:
        if not new_name.strip():
            raise EmptyCategoryNameError("Category name cannot be empty")
        if self.name == new_name:
            return

        old_name = self.name
        self.name = new_name
        self._events.append(
            CategoryRenamedEvent(
                category_id=self.category_id,
                old_name=old_name,
                new_name=new_name,
            )
        )

    def reorder(self, new_position: int) -> None:
        if self.display_order == new_position:
            return
        self.display_order = new_position

    def remove(self) -> None:
        """Emits event indicating that the category has been removed.

        Note: Validation against associated MenuItems (CategoryNotEmptyError)
        must be performed by a Domain Service or Application Service prior
        to calling this method, as Category does not hold references to MenuItems.
        """
        self._events.append(CategoryRemovedEvent(category_id=self.category_id))

    def collect_events(self) -> list[DomainEvent]:
        events = list(self._events)
        self._events.clear()
        return events

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Category):
            return False
        return self.category_id == other.category_id

    def __hash__(self) -> int:
        return hash(self.category_id)

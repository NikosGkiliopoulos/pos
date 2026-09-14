# domain/events/event_bus.py

from abc import ABC, abstractmethod
from collections.abc import Sequence

from src.bounded_contexts.menu_catalog.domain.events.menu_events import DomainEvent


class EventBus(ABC):
    """Abstract interface for publishing domain events.

    Concrete implementations (in-process dispatcher, message queue, etc.)
    live in the infrastructure layer. The domain and application layers
    only depend on this interface, never on a specific messaging technology.
    """

    @abstractmethod
    async def publish(self, event: DomainEvent) -> None:
        """Publish a single domain event to all interested subscribers."""
        raise NotImplementedError

    @abstractmethod
    async def publish_all(self, events: Sequence[DomainEvent]) -> None:
        """Publish multiple domain events, e.g. everything raised
        by an aggregate during one use case.
        """
        raise NotImplementedError

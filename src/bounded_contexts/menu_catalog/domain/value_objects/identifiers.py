# domain/value_objects/identifiers.py

from dataclasses import dataclass
from uuid import UUID, uuid4


@dataclass(frozen=True)
class MenuItemId:
    value: UUID

    @staticmethod
    def generate() -> "MenuItemId":
        return MenuItemId(uuid4())

    def __str__(self) -> str:
        return str(self.value)


@dataclass(frozen=True)
class CategoryId:
    value: UUID

    @staticmethod
    def generate() -> "CategoryId":
        return CategoryId(uuid4())

    def __str__(self) -> str:
        return str(self.value)


@dataclass(frozen=True)
class VariantId:
    value: UUID

    @staticmethod
    def generate() -> "VariantId":
        return VariantId(uuid4())

    def __str__(self) -> str:
        return str(self.value)


@dataclass(frozen=True)
class ModifierId:
    value: UUID

    @staticmethod
    def generate() -> "ModifierId":
        return ModifierId(uuid4())

    def __str__(self) -> str:
        return str(self.value)

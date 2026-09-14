# domain/exceptions/menu_exceptions.py


class MenuCatalogError(Exception):
    """Base exception for all Menu Catalog domain errors."""
    pass


# --- Money / Pricing ---

class InvalidPriceError(MenuCatalogError):
    """Raised when a price/amount is invalid
    (e.g. negative or exceeds maximum limit).
    """
    pass


class CurrencyMismatchError(MenuCatalogError):
    """Raised when performing operations on Money objects
    with different currencies.
    """
    pass


# --- Category ---

class EmptyCategoryNameError(MenuCatalogError):
    """Raised when a category name is empty or blank."""
    pass


class InvalidCategoryNameError(MenuCatalogError):
    """Raised when a category name violates formatting or length rules."""
    pass


class CategoryNotFoundError(MenuCatalogError):
    """Raised when a category cannot be found by its ID."""
    pass


class DuplicateCategoryNameError(MenuCatalogError):
    """Raised when a category with the same name already exists."""
    pass


class CategoryNotEmptyError(MenuCatalogError):
    """Raised when attempting to delete a category
    that still contains menu items.
    """
    pass


# --- MenuItem ---

class EmptyMenuItemNameError(MenuCatalogError):
    """Raised when a menu item name is empty or blank."""
    pass


class MenuItemNotFoundError(MenuCatalogError):
    """Raised when a menu item cannot be found by its ID."""
    pass


class DuplicateMenuItemNameError(MenuCatalogError):
    """Raised when a menu item name already exists
    within the same category.
    """
    pass


# --- Variant ---

class EmptyVariantNameError(MenuCatalogError):
    """Raised when a variant name is empty or blank."""
    pass


class DuplicateVariantNameError(MenuCatalogError):
    """Raised when a variant name already exists on the same menu item."""
    pass


class VariantNotFoundError(MenuCatalogError):
    """Raised when a variant cannot be found on a menu item."""
    pass


# --- Modifier ---

class EmptyModifierNameError(MenuCatalogError):
    """Raised when a modifier name is empty or blank."""
    pass


class DuplicateModifierNameError(MenuCatalogError):
    """Raised when a modifier name already exists within the same item."""
    pass


class ModifierNotFoundError(MenuCatalogError):
    """Raised when a modifier cannot be found on a menu item."""
    pass

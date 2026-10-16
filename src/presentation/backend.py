"""Backend interface for the DRAIE UI.

The presentation layer only ever talks to the application through this
interface.  Every method raises ``NotImplementedError`` by default so that you
can implement the real behaviour in the business / data-access layers without
touching the UI.

How to wire up your own backend
-------------------------------
1. Create a class that subclasses :class:`Backend`.
2. Implement the methods below (return dictionaries, see the docstrings).
3. Return an instance of your class from :func:`get_backend`.

The keys used in the record dictionaries must match the field keys declared by
the views (``id``, ``name``, ``category``, ...).
"""

from __future__ import annotations


def _todo(what: str) -> NotImplementedError:
    return NotImplementedError(
        f"{what} is not implemented yet.\n\n"
        "Implement it in your Backend subclass and return it from "
        "src/presentation/backend.get_backend()."
    )


class Backend:
    """Abstract gateway between the UI and your business/data layers."""

    # ------------------------------------------------------------------
    # Dashboard
    # ------------------------------------------------------------------
    def get_summary(self) -> dict:
        """Return headline figures for the dashboard.

        Expected keys: ``resources``, ``regions``, ``allocations``, ``users``,
        ``low_stock``.
        """
        raise _todo("Backend.get_summary()")

    # ------------------------------------------------------------------
    # Inventory (resources)
    # ------------------------------------------------------------------
    def list_resources(self) -> list[dict]:
        """Return every resource.

        Each dict: ``id, name, category, quantity, unit, region,
        reorder_level, status``.
        """
        raise _todo("Backend.list_resources()")

    def add_resource(self, data: dict) -> None:
        raise _todo("Backend.add_resource()")

    def update_resource(self, resource_id, data: dict) -> None:
        raise _todo("Backend.update_resource()")

    def delete_resource(self, resource_id) -> None:
        raise _todo("Backend.delete_resource()")

    # ------------------------------------------------------------------
    # Regions
    # ------------------------------------------------------------------
    def list_regions(self) -> list[dict]:
        """Each dict: ``id, name, district, coordinator, population,
        risk_level``."""
        raise _todo("Backend.list_regions()")

    def add_region(self, data: dict) -> None:
        raise _todo("Backend.add_region()")

    def update_region(self, region_id, data: dict) -> None:
        raise _todo("Backend.update_region()")

    def delete_region(self, region_id) -> None:
        raise _todo("Backend.delete_region()")

    # ------------------------------------------------------------------
    # Allocations
    # ------------------------------------------------------------------
    def list_allocations(self) -> list[dict]:
        """Each dict: ``id, resource, region, quantity, priority, date,
        status``."""
        raise _todo("Backend.list_allocations()")

    def add_allocation(self, data: dict) -> None:
        raise _todo("Backend.add_allocation()")

    def update_allocation(self, allocation_id, data: dict) -> None:
        raise _todo("Backend.update_allocation()")

    def delete_allocation(self, allocation_id) -> None:
        raise _todo("Backend.delete_allocation()")

    # ------------------------------------------------------------------
    # Users & roles
    # ------------------------------------------------------------------
    def list_users(self) -> list[dict]:
        """Each dict: ``id, name, username, role, region, status``."""
        raise _todo("Backend.list_users()")

    def add_user(self, data: dict) -> None:
        raise _todo("Backend.add_user()")

    def update_user(self, user_id, data: dict) -> None:
        raise _todo("Backend.update_user()")

    def delete_user(self, user_id) -> None:
        raise _todo("Backend.delete_user()")


def get_backend() -> Backend:
    """Return the backend used by the UI.

    Replace the return value with your own ``Backend`` subclass once the
    business and data-access layers are ready.
    """
    return Backend()

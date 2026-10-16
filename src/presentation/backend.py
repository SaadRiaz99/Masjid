"""Backend interface for the DRAIE UI.

The presentation layer only ever talks to the application through this
interface.  :class:`Backend` declares *what* the UI needs;
:class:`CsvBackend` is the real implementation that wires the CSV tables in
``data/`` to the business services.

Wiring up a different backend
-----------------------------
1. Create a class that subclasses :class:`Backend`.
2. Implement the methods below (return dictionaries, see the docstrings).
3. Return an instance of your class from :func:`get_backend`.

The keys used in the record dictionaries must match the field keys declared
by the views (``id``, ``name``, ``category``, ...).
"""

from __future__ import annotations

from ..business import (
    Actor,
    AllocationService,
    InventoryService,
    RegionService,
    UserService,
    build_summary,
)
from ..data_access import Database


class Backend:
    """Abstract gateway between the UI and the business/data layers."""

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


class CsvBackend(Backend):
    """The shipped backend: CSV tables in ``data/`` + business services.

    ``actor`` decides which role the UI acts as.  It defaults to ``Admin``
    so the desktop app behaves like a full-featured local tool; pass a
    different :class:`~src.business.permissions.Actor` to act as someone
    else (that is how the authorization tests run).
    """

    def __init__(self, data_dir=None, actor: Actor | None = None):
        self.database = Database(data_dir)
        self.actor = actor or Actor(role="Admin")

        self.inventory = InventoryService(self.database.resources, self.actor)
        self.regions = RegionService(self.database.regions, self.actor)
        self.allocations = AllocationService(
            self.database.allocations, self.inventory, self.regions, self.actor
        )
        self.users = UserService(self.database.users, self.actor)

    # ------------------------------------------------------------------
    # Dashboard
    # ------------------------------------------------------------------
    def get_summary(self) -> dict:
        return build_summary(self.inventory, self.regions, self.allocations, self.users)

    # ------------------------------------------------------------------
    # Inventory (resources)
    # ------------------------------------------------------------------
    def list_resources(self) -> list[dict]:
        return self.inventory.list()

    def add_resource(self, data: dict) -> None:
        self.inventory.create(data)

    def update_resource(self, resource_id, data: dict) -> None:
        self.inventory.update(resource_id, data)

    def delete_resource(self, resource_id) -> None:
        self.inventory.delete(resource_id)

    # ------------------------------------------------------------------
    # Regions
    # ------------------------------------------------------------------
    def list_regions(self) -> list[dict]:
        return self.regions.list()

    def add_region(self, data: dict) -> None:
        self.regions.create(data)

    def update_region(self, region_id, data: dict) -> None:
        self.regions.update(region_id, data)

    def delete_region(self, region_id) -> None:
        self.regions.delete(region_id)

    # ------------------------------------------------------------------
    # Allocations
    # ------------------------------------------------------------------
    def list_allocations(self) -> list[dict]:
        return self.allocations.list()

    def add_allocation(self, data: dict) -> None:
        self.allocations.create(data)

    def update_allocation(self, allocation_id, data: dict) -> None:
        self.allocations.update(allocation_id, data)

    def delete_allocation(self, allocation_id) -> None:
        self.allocations.delete(allocation_id)

    # ------------------------------------------------------------------
    # Users & roles
    # ------------------------------------------------------------------
    def list_users(self) -> list[dict]:
        return self.users.list()

    def add_user(self, data: dict) -> None:
        self.users.create(data)

    def update_user(self, user_id, data: dict) -> None:
        self.users.update(user_id, data)

    def delete_user(self, user_id) -> None:
        self.users.delete(user_id)


def _todo(what: str) -> NotImplementedError:
    return NotImplementedError(
        f"{what} is not implemented yet.\n\n"
        "Implement it in your Backend subclass and return it from "
        "src/presentation/backend.get_backend()."
    )


def get_backend() -> Backend:
    """Return the backend used by the UI: CSV files + business services."""
    return CsvBackend()

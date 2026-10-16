"""Business rules for allocations - the heart of the application.

An allocation ties a resource to a region.  While it is active it *holds*
stock, so ``inventory.list()`` always shows what is still free to dispatch.
"""

from __future__ import annotations

from ..models import Allocation
from .errors import ValidationError
from .inventory import InventoryService
from .permissions import Actor, ensure_in_scope, in_scope, require
from .regions import RegionService


class AllocationService:
    """Create, read, update and delete allocations.

    Rules enforced here:
    * only the allowed roles may act (see :mod:`business.permissions`);
    * coordinators only work with allocations for their own region;
    * the resource and region must already exist;
    * active allocations hold stock - creating one deducts it, cancelling or
      deleting one gives it back, and editing the quantity moves the
      difference.
    """

    entity = "allocation"

    def __init__(
        self,
        store,
        inventory: InventoryService,
        regions: RegionService,
        actor: Actor | None = None,
    ):
        self.store = store
        self.inventory = inventory
        self.regions = regions
        self.actor = actor or Actor()

    # ------------------------------------------------------------------
    # Reading
    # ------------------------------------------------------------------
    def list(self) -> list[dict]:
        require(self.actor, self.entity, "read")
        return [
            allocation.to_row()
            for allocation in self._records()
            if in_scope(self.actor, allocation.region)
        ]

    def get(self, allocation_id) -> dict:
        require(self.actor, self.entity, "read")
        allocation = self._find(allocation_id)
        ensure_in_scope(self.actor, allocation.region)
        return allocation.to_row()

    # ------------------------------------------------------------------
    # Writing
    # ------------------------------------------------------------------
    def create(self, data: dict) -> dict:
        require(self.actor, self.entity, "create")
        allocation = Allocation.from_row(data)
        self._check_references(allocation)
        ensure_in_scope(self.actor, allocation.region)

        if allocation.is_active:
            self.inventory.reserve(allocation.resource, allocation.quantity)

        allocation.id = self.store.next_id()
        self.store.insert(allocation.to_row())
        return allocation.to_row()

    def update(self, allocation_id, data: dict) -> dict:
        require(self.actor, self.entity, "update")
        existing = self._find(allocation_id)
        ensure_in_scope(self.actor, existing.region)

        merged = {**existing.to_row(), **{k: v for k, v in data.items() if k != "id"}}
        updated = Allocation.from_row(merged)
        updated.id = existing.id
        self._check_references(updated)
        ensure_in_scope(self.actor, updated.region)

        self._settle_stock(existing, updated)
        self._replace(updated)
        return updated.to_row()

    def delete(self, allocation_id) -> None:
        require(self.actor, self.entity, "delete")
        existing = self._find(allocation_id)
        ensure_in_scope(self.actor, existing.region)

        if existing.is_active:
            self.inventory.release(existing.resource, existing.quantity)

        self.store.save(
            [row for row in self.store.all() if str(row.get("id")) != str(existing.id)]
        )

    # ------------------------------------------------------------------
    # Internals
    # ------------------------------------------------------------------
    def _settle_stock(self, existing: Allocation, updated: Allocation) -> None:
        """Move stock around so it always matches the two versions."""
        if existing.is_active and updated.is_active:
            if existing.resource.casefold() != updated.resource.casefold():
                # Switching resource: grab the new one first so a failure
                # leaves the data untouched, then free the old one.
                self.inventory.reserve(updated.resource, updated.quantity)
                self.inventory.release(existing.resource, existing.quantity)
            else:
                difference = updated.quantity - existing.quantity
                if difference > 0:
                    self.inventory.reserve(updated.resource, difference)
                elif difference < 0:
                    self.inventory.release(updated.resource, -difference)
        elif existing.is_active:
            self.inventory.release(existing.resource, existing.quantity)
        elif updated.is_active:
            self.inventory.reserve(updated.resource, updated.quantity)

    def _check_references(self, allocation: Allocation) -> None:
        if self.inventory.find_by_name(allocation.resource) is None:
            raise ValidationError(f"Unknown resource: {allocation.resource!r}.")
        self.regions.require_by_name(allocation.region)

    def _records(self) -> list[Allocation]:
        return [Allocation.from_row(row) for row in self.store.all()]

    def _find(self, allocation_id) -> Allocation:
        for allocation in self._records():
            if str(allocation.id) == str(allocation_id):
                return allocation
        raise ValidationError(f"Allocation with id {allocation_id} was not found.")

    def _replace(self, updated: Allocation) -> None:
        rows = self.store.all()
        for index, row in enumerate(rows):
            if str(row.get("id")) == str(updated.id):
                rows[index] = updated.to_row()
        self.store.save(rows)

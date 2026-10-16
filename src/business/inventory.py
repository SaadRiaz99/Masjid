"""Business rules for inventory resources."""

from __future__ import annotations

from ..models import Resource
from .errors import ValidationError
from .permissions import Actor, ensure_in_scope, in_scope, require


class InventoryService:
    """Create, read, update and delete resources - and move their stock.

    Rules enforced here:
    * only the allowed roles may act (see :mod:`business.permissions`);
    * coordinators only see and touch resources in their own region;
    * resource names are unique, so allocations can refer to them by name;
    * ``status`` is always derived from the stock numbers.
    """

    entity = "resource"

    def __init__(self, store, actor: Actor | None = None):
        self.store = store
        self.actor = actor or Actor()

    # ------------------------------------------------------------------
    # Reading
    # ------------------------------------------------------------------
    def list(self) -> list[dict]:
        """Every resource the actor is allowed to see."""
        require(self.actor, self.entity, "read")
        return [
            resource.to_row()
            for resource in self._records()
            if in_scope(self.actor, resource.region)
        ]

    def get(self, resource_id) -> dict:
        """One resource by id, or raise if it is missing / out of scope."""
        require(self.actor, self.entity, "read")
        resource = self._find(resource_id)
        ensure_in_scope(self.actor, resource.region)
        return resource.to_row()

    def find_by_name(self, name: str) -> Resource | None:
        """Look a resource up by its (unique) name."""
        wanted = (name or "").strip().casefold()
        for resource in self._records():
            if resource.name.casefold() == wanted:
                return resource
        return None

    # ------------------------------------------------------------------
    # Writing
    # ------------------------------------------------------------------
    def create(self, data: dict) -> dict:
        require(self.actor, self.entity, "create")
        resource = Resource.from_row(data)
        ensure_in_scope(self.actor, resource.region)
        self._ensure_name_free(resource.name)
        resource.id = self.store.next_id()
        self.store.insert(resource.to_row())
        return resource.to_row()

    def update(self, resource_id, data: dict) -> dict:
        require(self.actor, self.entity, "update")
        existing = self._find(resource_id)
        ensure_in_scope(self.actor, existing.region)

        merged = {**existing.to_row(), **{k: v for k, v in data.items() if k != "id"}}
        resource = Resource.from_row(merged)
        resource.id = existing.id
        ensure_in_scope(self.actor, resource.region)
        if resource.name.casefold() != existing.name.casefold():
            self._ensure_name_free(resource.name)

        self._replace(resource)
        return resource.to_row()

    def delete(self, resource_id) -> None:
        require(self.actor, self.entity, "delete")
        existing = self._find(resource_id)
        ensure_in_scope(self.actor, existing.region)
        self._write_all(
            row for row in self.store.all() if str(row.get("id")) != str(existing.id)
        )

    # ------------------------------------------------------------------
    # Stock movements (used by the allocation service)
    # ------------------------------------------------------------------
    def reserve(self, resource_name: str, amount: int) -> None:
        """Take stock out because an allocation now holds it."""
        resource = self._require_by_name(resource_name)
        resource.use_stock(amount)
        self._replace(resource)

    def release(self, resource_name: str, amount: int) -> None:
        """Give stock back because an allocation was cancelled or removed."""
        resource = self._require_by_name(resource_name)
        resource.add_stock(amount)
        self._replace(resource)

    # ------------------------------------------------------------------
    # Internals
    # ------------------------------------------------------------------
    def _records(self) -> list[Resource]:
        return [Resource.from_row(row) for row in self.store.all()]

    def _find(self, resource_id) -> Resource:
        for resource in self._records():
            if str(resource.id) == str(resource_id):
                return resource
        raise ValidationError(f"Resource with id {resource_id} was not found.")

    def _require_by_name(self, name: str) -> Resource:
        resource = self.find_by_name(name)
        if resource is None:
            raise ValidationError(f"Unknown resource: {name!r}.")
        return resource

    def _ensure_name_free(self, name: str) -> None:
        if self.find_by_name(name) is not None:
            raise ValidationError(f"A resource named {name!r} already exists.")

    def _replace(self, resource: Resource) -> None:
        rows = self.store.all()
        for index, row in enumerate(rows):
            if str(row.get("id")) == str(resource.id):
                rows[index] = resource.to_row()
                break
        else:
            rows.append(resource.to_row())
        self._write_all(rows)

    def _write_all(self, rows) -> None:
        self.store.save(list(rows))

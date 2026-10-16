"""Business rules for regions."""

from __future__ import annotations

from ..models import Region
from .errors import ValidationError
from .permissions import Actor, require


class RegionService:
    """Create, read, update and delete regions.

    Rules enforced here:
    * only the allowed roles may act (see :mod:`business.permissions`);
    * region names are unique, because resources and allocations refer to
      regions by name;
    * coordinators have read-only access to regions.
    """

    entity = "region"

    def __init__(self, store, actor: Actor | None = None):
        self.store = store
        self.actor = actor or Actor()

    # ------------------------------------------------------------------
    # Reading
    # ------------------------------------------------------------------
    def list(self) -> list[dict]:
        """Every region (coordinators see all of them - they need the map)."""
        require(self.actor, self.entity, "read")
        return [region.to_row() for region in self._records()]

    def get(self, region_id) -> dict:
        require(self.actor, self.entity, "read")
        return self._find(region_id).to_row()

    def find_by_name(self, name: str) -> Region | None:
        """Look a region up by its (unique) name."""
        wanted = (name or "").strip().casefold()
        for region in self._records():
            if region.name.casefold() == wanted:
                return region
        return None

    def require_by_name(self, name: str) -> Region:
        """Same as :meth:`find_by_name` but raises when it does not exist."""
        region = self.find_by_name(name)
        if region is None:
            raise ValidationError(f"Unknown region: {name!r}.")
        return region

    # ------------------------------------------------------------------
    # Writing
    # ------------------------------------------------------------------
    def create(self, data: dict) -> dict:
        require(self.actor, self.entity, "create")
        region = Region.from_row(data)
        self._ensure_name_free(region.name)
        region.id = self.store.next_id()
        self.store.insert(region.to_row())
        return region.to_row()

    def update(self, region_id, data: dict) -> dict:
        require(self.actor, self.entity, "update")
        existing = self._find(region_id)

        merged = {**existing.to_row(), **{k: v for k, v in data.items() if k != "id"}}
        region = Region.from_row(merged)
        region.id = existing.id
        if region.name.casefold() != existing.name.casefold():
            self._ensure_name_free(region.name)

        rows = self.store.all()
        for index, row in enumerate(rows):
            if str(row.get("id")) == str(region.id):
                rows[index] = region.to_row()
        self.store.save(rows)
        return region.to_row()

    def delete(self, region_id) -> None:
        require(self.actor, self.entity, "delete")
        existing = self._find(region_id)
        self.store.save(
            [row for row in self.store.all() if str(row.get("id")) != str(existing.id)]
        )

    # ------------------------------------------------------------------
    # Internals
    # ------------------------------------------------------------------
    def _records(self) -> list[Region]:
        return [Region.from_row(row) for row in self.store.all()]

    def _find(self, region_id) -> Region:
        for region in self._records():
            if str(region.id) == str(region_id):
                return region
        raise ValidationError(f"Region with id {region_id} was not found.")

    def _ensure_name_free(self, name: str) -> None:
        if self.find_by_name(name) is not None:
            raise ValidationError(f"A region named {name!r} already exists.")

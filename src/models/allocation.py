"""Allocation - a dispatch of a resource to a region."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from typing import ClassVar

from .common import as_int, as_text, one_of, require_text

PRIORITIES = ("Low", "Medium", "High", "Critical")
STATUSES = ("Pending", "Approved", "In Transit", "Delivered", "Cancelled")

#: Statuses that hold stock out of the inventory (everything except cancelled).
ACTIVE_STATUSES = ("Pending", "Approved", "In Transit", "Delivered")


@dataclass
class Allocation:
    """A promise to send ``quantity`` units of a resource to a region.

    An allocation is *active* unless it has been cancelled.  Active
    allocations hold the stock they promise, so the inventory always shows
    what is still physically available to dispatch.
    """

    FIELDS: ClassVar[tuple[str, ...]] = (
        "id", "resource", "region", "quantity", "priority", "date", "status",
    )

    id: int | None = None
    resource: str = ""
    region: str = ""
    quantity: int = 0
    priority: str = "Medium"
    date: str = ""
    status: str = "Pending"

    def __post_init__(self):
        self.validate()

    def validate(self) -> "Allocation":
        """Normalise every field and raise ``ValueError`` when one is wrong."""
        self.resource = require_text(self.resource, "Resource")
        self.region = require_text(self.region, "Region")
        self.quantity = as_int(self.quantity, "quantity")
        self.priority = one_of(self.priority, "priority", PRIORITIES, default="Medium")
        self.date = self._validate_date(self.date)
        self.status = one_of(self.status, "status", STATUSES, default="Pending")

        if self.quantity <= 0:
            raise ValueError("quantity must be greater than zero.")
        return self

    @staticmethod
    def _validate_date(value) -> str:
        text = as_text(value, "date")
        if not text:
            raise ValueError("date is required (YYYY-MM-DD).")
        try:
            date.fromisoformat(text)
        except ValueError:
            raise ValueError("date must be in YYYY-MM-DD format.") from None
        return text

    # ------------------------------------------------------------------
    # Derived values
    # ------------------------------------------------------------------
    @property
    def is_active(self) -> bool:
        """True while the allocation still holds stock."""
        return self.status in ACTIVE_STATUSES

    # ------------------------------------------------------------------
    # CSV row mapping
    # ------------------------------------------------------------------
    def to_row(self) -> dict:
        return {
            "id": self.id,
            "resource": self.resource,
            "region": self.region,
            "quantity": self.quantity,
            "priority": self.priority,
            "date": self.date,
            "status": self.status,
        }

    @classmethod
    def from_row(cls, row: dict) -> "Allocation":
        raw_id = row.get("id")
        record_id = None if raw_id in (None, "") else as_int(raw_id, "id")
        return cls(
            id=record_id,
            resource=row.get("resource", ""),
            region=row.get("region", ""),
            quantity=row.get("quantity", 0),
            priority=row.get("priority", ""),
            date=row.get("date", ""),
            status=row.get("status", ""),
        )

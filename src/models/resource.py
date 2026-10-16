"""Inventory resource - a stock item stored in a region."""

from __future__ import annotations

from dataclasses import dataclass
from typing import ClassVar

from .common import as_int, as_text, one_of, require_text

CATEGORIES = ("Medicine", "Food", "Water", "Shelter", "Equipment", "Clothing", "Other")
UNITS = ("pcs", "boxes", "kg", "liters", "packs", "units")
STATUSES = ("In Stock", "Low", "Out of Stock")


@dataclass
class Resource:
    """A single stocked resource.

    ``status`` is never taken from user input: it is always derived from
    ``quantity`` and ``reorder_level`` so the dashboard and the table can
    never disagree with each other.
    """

    FIELDS: ClassVar[tuple[str, ...]] = (
        "id", "name", "category", "quantity", "unit", "region", "reorder_level",
        "status",
    )

    id: int | None = None
    name: str = ""
    category: str = "Other"
    quantity: int = 0
    unit: str = "pcs"
    region: str = ""
    reorder_level: int = 0
    status: str = "In Stock"

    def __post_init__(self):
        self.validate()

    # ------------------------------------------------------------------
    # Validation
    # ------------------------------------------------------------------
    def validate(self) -> "Resource":
        """Normalise every field and raise ``ValueError`` when one is wrong."""
        self.name = require_text(self.name, "Resource name")
        self.category = one_of(self.category, "category", CATEGORIES, default="Other")
        self.unit = one_of(self.unit, "unit", UNITS, default="pcs")
        self.quantity = as_int(self.quantity, "quantity")
        self.reorder_level = as_int(self.reorder_level, "reorder_level", default=0)
        self.region = as_text(self.region, "region")

        if self.quantity < 0:
            raise ValueError("quantity cannot be negative.")
        if self.reorder_level < 0:
            raise ValueError("reorder_level cannot be negative.")

        self.status = self.status_for(self.quantity, self.reorder_level)
        return self

    # ------------------------------------------------------------------
    # Stock movements
    # ------------------------------------------------------------------
    def add_stock(self, amount: int) -> None:
        """Receive ``amount`` more units into stock."""
        amount = as_int(amount, "amount to add")
        if amount <= 0:
            raise ValueError("Amount to add must be positive.")
        self.quantity += amount
        self.status = self.status_for(self.quantity, self.reorder_level)

    def use_stock(self, amount: int) -> None:
        """Take ``amount`` units out of stock."""
        amount = as_int(amount, "amount to use")
        if amount <= 0:
            raise ValueError("Amount to use must be positive.")
        if amount > self.quantity:
            raise ValueError(
                f"Not enough stock for {self.name}: "
                f"requested {amount}, only {self.quantity} available."
            )
        self.quantity -= amount
        self.status = self.status_for(self.quantity, self.reorder_level)

    # ------------------------------------------------------------------
    # Derived values
    # ------------------------------------------------------------------
    @staticmethod
    def status_for(quantity: int, reorder_level: int) -> str:
        """Work out the stock status from the current numbers."""
        if quantity <= 0:
            return "Out of Stock"
        if reorder_level > 0 and quantity <= reorder_level:
            return "Low"
        return "In Stock"

    @property
    def is_low(self) -> bool:
        """True when the item needs reordering."""
        return self.status in ("Low", "Out of Stock")

    # ------------------------------------------------------------------
    # CSV row mapping
    # ------------------------------------------------------------------
    def to_row(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "category": self.category,
            "quantity": self.quantity,
            "unit": self.unit,
            "region": self.region,
            "reorder_level": self.reorder_level,
            "status": self.status,
        }

    @classmethod
    def from_row(cls, row: dict) -> "Resource":
        raw_id = row.get("id")
        record_id = None if raw_id in (None, "") else as_int(raw_id, "id")
        return cls(
            id=record_id,
            name=row.get("name", ""),
            category=row.get("category", ""),
            quantity=row.get("quantity", 0),
            unit=row.get("unit", ""),
            region=row.get("region", ""),
            reorder_level=row.get("reorder_level", 0),
            status=row.get("status", ""),
        )

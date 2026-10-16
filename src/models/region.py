"""Geographic region that receives relief resources."""

from __future__ import annotations

from dataclasses import dataclass
from typing import ClassVar

from .common import as_int, as_text, one_of, require_text

RISK_LEVELS = ("Low", "Medium", "High", "Critical")


@dataclass
class Region:
    """An area served by the relief operation."""

    FIELDS: ClassVar[tuple[str, ...]] = (
        "id", "name", "district", "coordinator", "population", "risk_level",
    )

    id: int | None = None
    name: str = ""
    district: str = ""
    coordinator: str = ""
    population: int = 0
    risk_level: str = "Low"

    def __post_init__(self):
        self.validate()

    def validate(self) -> "Region":
        """Normalise every field and raise ``ValueError`` when one is wrong."""
        self.name = require_text(self.name, "Region name")
        self.district = as_text(self.district, "district")
        self.coordinator = as_text(self.coordinator, "coordinator")
        self.population = as_int(self.population, "population", default=0)
        self.risk_level = one_of(self.risk_level, "risk_level", RISK_LEVELS, default="Low")

        if self.population < 0:
            raise ValueError("population cannot be negative.")
        return self

    # ------------------------------------------------------------------
    # CSV row mapping
    # ------------------------------------------------------------------
    def to_row(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "district": self.district,
            "coordinator": self.coordinator,
            "population": self.population,
            "risk_level": self.risk_level,
        }

    @classmethod
    def from_row(cls, row: dict) -> "Region":
        raw_id = row.get("id")
        record_id = None if raw_id in (None, "") else as_int(raw_id, "id")
        return cls(
            id=record_id,
            name=row.get("name", ""),
            district=row.get("district", ""),
            coordinator=row.get("coordinator", ""),
            population=row.get("population", 0),
            risk_level=row.get("risk_level", ""),
        )

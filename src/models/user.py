"""System user and their role."""

from __future__ import annotations

from dataclasses import dataclass
from typing import ClassVar

from .common import as_int, as_text, one_of, require_text

ROLES = ("Admin", "Manager", "Coordinator", "Viewer")
STATUSES = ("Active", "Inactive")


@dataclass
class User:
    """An account that can sign in to the application.

    ``region`` is only meaningful for coordinators: it is the region their
    work is limited to.
    """

    FIELDS: ClassVar[tuple[str, ...]] = (
        "id", "name", "username", "role", "region", "status",
    )

    id: int | None = None
    name: str = ""
    username: str = ""
    role: str = "Viewer"
    region: str = ""
    status: str = "Active"

    def __post_init__(self):
        self.validate()

    def validate(self) -> "User":
        """Normalise every field and raise ``ValueError`` when one is wrong."""
        self.name = require_text(self.name, "Full name")
        self.username = require_text(self.username, "Username")
        self.role = one_of(self.role, "role", ROLES, default="Viewer")
        self.region = as_text(self.region, "region")
        self.status = one_of(self.status, "status", STATUSES, default="Active")
        return self

    # ------------------------------------------------------------------
    # CSV row mapping
    # ------------------------------------------------------------------
    def to_row(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "username": self.username,
            "role": self.role,
            "region": self.region,
            "status": self.status,
        }

    @classmethod
    def from_row(cls, row: dict) -> "User":
        raw_id = row.get("id")
        record_id = None if raw_id in (None, "") else as_int(raw_id, "id")
        return cls(
            id=record_id,
            name=row.get("name", ""),
            username=row.get("username", ""),
            role=row.get("role", ""),
            region=row.get("region", ""),
            status=row.get("status", ""),
        )

"""Domain models for DRAIE.

Each model is a dataclass with a ``validate`` method plus ``to_row`` /
``from_row`` helpers for talking to the CSV tables.
"""

from __future__ import annotations

from .allocation import PRIORITIES, Allocation
from .region import RISK_LEVELS, Region
from .resource import CATEGORIES, UNITS, Resource
from .user import ROLES, User

__all__ = [
    "Allocation",
    "CATEGORIES",
    "PRIORITIES",
    "RISK_LEVELS",
    "Region",
    "Resource",
    "ROLES",
    "UNITS",
    "User",
]

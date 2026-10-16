"""Business layer: the rules the application lives by.

The presentation layer never talks to CSV files directly - it goes through
a backend that is built from the services exported here.
"""

from __future__ import annotations

from .allocations import AllocationService
from .dashboard import build_summary
from .errors import AuthorizationError, ValidationError
from .inventory import InventoryService
from .permissions import ACTIONS, Actor, can, in_scope, require
from .regions import RegionService
from .users import UserService

__all__ = [
    "ACTIONS",
    "Actor",
    "AllocationService",
    "AuthorizationError",
    "InventoryService",
    "RegionService",
    "UserService",
    "ValidationError",
    "build_summary",
    "can",
    "in_scope",
    "require",
]

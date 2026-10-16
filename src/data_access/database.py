"""Bundle of CSV tables backing the application.

A ``Database`` gives every service its own :class:`~data_access.csv_store.CsvStore`
pointing at the right file, so nothing else in the codebase needs to know
where the data lives.
"""

from __future__ import annotations

from pathlib import Path

from ..models import Allocation, Region, Resource, User
from .csv_store import CsvStore

#: Project root, i.e. the folder that holds ``src`` and ``data``.
PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_DATA_DIR = PROJECT_ROOT / "data"


class Database:
    """The four tables the application persists."""

    def __init__(self, data_dir=None):
        folder = Path(data_dir) if data_dir else DEFAULT_DATA_DIR
        folder.mkdir(parents=True, exist_ok=True)

        self.resources = CsvStore(folder / "resources.csv", Resource.FIELDS)
        self.regions = CsvStore(folder / "regions.csv", Region.FIELDS)
        self.allocations = CsvStore(folder / "allocations.csv", Allocation.FIELDS)
        self.users = CsvStore(folder / "users.csv", User.FIELDS)

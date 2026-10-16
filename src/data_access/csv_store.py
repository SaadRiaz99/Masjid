"""A very small CSV table wrapper.

The whole persistence layer is one file per table.  Every change is written
back in a single atomic write, so a crash mid-save can never leave a
half-written file behind.
"""

from __future__ import annotations

import csv
import os
from pathlib import Path


class CsvStore:
    """Reads and writes one CSV file as a list of plain dictionaries."""

    def __init__(self, path, fieldnames: tuple | list):
        self.path = Path(path)
        self.fieldnames = list(fieldnames)
        self._ensure_file()

    # ------------------------------------------------------------------
    # Reading
    # ------------------------------------------------------------------
    def all(self) -> list[dict]:
        """Return every row, normalised to the declared field names."""
        if not self.path.exists() or self.path.stat().st_size == 0:
            return []

        with self.path.open(newline="", encoding="utf-8") as handle:
            reader = csv.DictReader(handle)
            return [
                {field: (row.get(field) or "") for field in self.fieldnames}
                for row in reader
            ]

    def next_id(self) -> int:
        """Return the id the next inserted row should use."""
        highest = 0
        for row in self.all():
            try:
                highest = max(highest, int(row.get("id") or 0))
            except (TypeError, ValueError):
                continue
        return highest + 1

    # ------------------------------------------------------------------
    # Writing
    # ------------------------------------------------------------------
    def save(self, rows: list[dict]) -> None:
        """Overwrite the table with ``rows`` (used for updates and deletes)."""
        temporary = self.path.with_suffix(self.path.suffix + ".tmp")
        with temporary.open("w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(handle, fieldnames=self.fieldnames)
            writer.writeheader()
            for row in rows:
                writer.writerow({field: row.get(field, "") for field in self.fieldnames})
        os.replace(temporary, self.path)

    def insert(self, row: dict) -> None:
        """Append one row to the table."""
        self.save(self.all() + [dict(row)])

    # ------------------------------------------------------------------
    # Internals
    # ------------------------------------------------------------------
    def _ensure_file(self) -> None:
        """Create the file with a header row when it does not exist yet."""
        if self.path.exists() and self.path.stat().st_size > 0:
            return
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.save([])

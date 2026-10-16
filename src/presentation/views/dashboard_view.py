"""Dashboard overview view."""

from __future__ import annotations

import tkinter as tk
from tkinter import ttk

from ..widgets import MUTED, Column, DataTable


class StatCard(ttk.Frame):
    """A small KPI card showing a value and a caption."""

    def __init__(self, parent, caption, accent="#2563eb"):
        super().__init__(parent, padding=18, style="Card.TFrame")
        self.columnconfigure(0, weight=1)

        self._value = ttk.Label(
            self, text="—", font=("Segoe UI", 26, "bold"), foreground=accent,
            style="Card.TLabel",
        )
        self._value.grid(row=0, column=0, sticky="w")

        ttk.Label(
            self, text=caption, font=("Segoe UI", 10), foreground=MUTED,
            style="Card.TLabel",
        ).grid(row=1, column=0, sticky="w", pady=(2, 0))

    def set_value(self, value):
        self._value.config(text=str(value))


class DashboardView(ttk.Frame):
    """Landing screen with headline figures and an at-a-glance stock table."""

    def __init__(self, parent, backend, status_cb=None):
        super().__init__(parent, padding=(26, 22))
        self.backend = backend
        self._set_status = status_cb or (lambda _msg: None)

        self.columnconfigure(0, weight=1)
        self.rowconfigure(3, weight=1)
        self._build()

    def _build(self):
        header = ttk.Frame(self)
        header.grid(row=0, column=0, sticky="ew")
        ttk.Label(
            header, text="Operations Dashboard", font=("Segoe UI", 18, "bold")
        ).pack(anchor="w")
        ttk.Label(
            header,
            text="Overview of resources, regions, allocations and users.",
            foreground=MUTED,
        ).pack(anchor="w", pady=(2, 0))

        cards = ttk.Frame(self)
        cards.grid(row=1, column=0, sticky="ew", pady=(18, 0))
        self.cards = {
            "resources": StatCard(cards, "Resources"),
            "regions": StatCard(cards, "Regions", accent="#0891b2"),
            "allocations": StatCard(cards, "Allocations", accent="#7c3aed"),
            "users": StatCard(cards, "Users", accent="#059669"),
            "low_stock": StatCard(cards, "Low Stock Items", accent="#dc2626"),
        }
        for index, card in enumerate(self.cards.values()):
            card.grid(row=0, column=index, sticky="nsew", padx=(0 if index == 0 else 12, 0))
            cards.columnconfigure(index, weight=1)

        ttk.Label(
            self, text="Low Stock Resources", font=("Segoe UI", 13, "bold")
        ).grid(row=2, column=0, sticky="w", pady=(24, 0))

        columns = (
            Column("name", "Name", 180),
            Column("category", "Category", 120),
            Column("quantity", "Quantity", 90, "e"),
            Column("reorder_level", "Reorder", 90, "e"),
            Column("region", "Region", 150),
            Column("status", "Status", 110),
        )
        self.table = DataTable(self, columns)
        self.table.grid(row=3, column=0, sticky="nsew", pady=(10, 0))

    def refresh(self):
        self._load_summary()
        self._load_low_stock()

    def _load_summary(self):
        try:
            summary = self.backend.get_summary() or {}
        except NotImplementedError as exc:
            for card in self.cards.values():
                card.set_value("—")
            self._set_status(str(exc))
            return
        except Exception as exc:  # noqa: BLE001
            self._set_status(f"Error: {exc}")
            return

        for key, card in self.cards.items():
            card.set_value(summary.get(key, 0))

    def _load_low_stock(self):
        try:
            resources = self.backend.list_resources() or []
        except Exception:  # noqa: BLE001 - dashboard stays usable
            self.table.clear()
            return

        low = [
            self._row(r)
            for r in resources
            if self._is_low(self._row(r))
        ]
        self.table.set_rows(low)

    @staticmethod
    def _row(record) -> dict:
        if isinstance(record, dict):
            return dict(record)
        if hasattr(record, "__dict__"):
            return {k: v for k, v in vars(record).items() if not k.startswith("_")}
        return {"value": record}

    @staticmethod
    def _is_low(row: dict) -> bool:
        status = str(row.get("status", "")).strip().lower()
        if status in {"low", "out of stock", "out"}:
            return True
        try:
            quantity = float(row.get("quantity", 0) or 0)
            reorder = float(row.get("reorder_level", 0) or 0)
        except (TypeError, ValueError):
            return False
        return reorder > 0 and quantity <= reorder

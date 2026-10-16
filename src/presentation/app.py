"""DRAIE application shell: sidebar navigation + swappable content views.

Run with::

    python -m src.presentation.app
"""

from __future__ import annotations

import tkinter as tk
from tkinter import ttk

from .backend import Backend, get_backend
from .views.allocation_view import AllocationView
from .views.dashboard_view import DashboardView
from .views.inventory_view import InventoryView
from .views.regions_view import RegionsView
from .views.users_view import UsersView
from .widgets import (
    CONTENT_BG,
    MUTED,
    SIDEBAR_ACTIVE,
    SIDEBAR_ACTIVE_HOVER,
    SIDEBAR_BG,
    SIDEBAR_HOVER,
    SIDEBAR_TEXT,
)

NAV_ITEMS = (
    ("dashboard", "Dashboard", DashboardView),
    ("inventory", "Inventory", InventoryView),
    ("regions", "Regions", RegionsView),
    ("allocation", "Allocation", AllocationView),
    ("users", "Users & Roles", UsersView),
)


class Application(tk.Tk):
    """Top-level window that hosts the navigation and the active view."""

    def __init__(self, backend: Backend | None = None):
        super().__init__()
        self.backend = backend or get_backend()

        self.title("DRAIE - Disaster Resource Allocator & Inventory Engine")
        self.geometry("1100x680")
        self.minsize(900, 560)
        self.configure(background=CONTENT_BG)

        self._views: dict[str, ttk.Frame] = {}
        self._nav_buttons: dict[str, ttk.Button] = {}
        self._active = None

        self._configure_styles()
        self._build_layout()

        self.show_view("dashboard")

    # ------------------------------------------------------------------
    # Styling
    # ------------------------------------------------------------------
    def _configure_styles(self):
        style = ttk.Style(self)
        if "clam" in style.theme_names():
            style.theme_use("clam")

        style.configure("TFrame", background=CONTENT_BG)
        style.configure("TLabel", background=CONTENT_BG, font=("Segoe UI", 10))
        style.configure("TButton", font=("Segoe UI", 10), padding=(12, 6))
        style.configure(
            "Treeview", font=("Segoe UI", 10), rowheight=26, background="white",
            fieldbackground="white",
        )
        style.configure("Treeview.Heading", font=("Segoe UI", 10, "bold"))
        style.configure("Card.TFrame", background="white", relief="flat")
        style.configure("Card.TLabel", background="white")
        style.configure("Status.TLabel", background="#e2e8f0", foreground=MUTED)

        style.configure(
            "Nav.TButton",
            background=SIDEBAR_BG,
            foreground=SIDEBAR_TEXT,
            borderwidth=0,
            focuscolor=SIDEBAR_BG,
            anchor="w",
            padding=(18, 12),
            font=("Segoe UI", 11),
        )
        style.map(
            "Nav.TButton",
            background=[("active", SIDEBAR_HOVER)],
            foreground=[("active", "white")],
        )
        style.configure(
            "NavActive.TButton",
            background=SIDEBAR_ACTIVE,
            foreground="white",
            borderwidth=0,
            focuscolor=SIDEBAR_ACTIVE,
            anchor="w",
            padding=(18, 12),
            font=("Segoe UI", 11, "bold"),
        )
        style.map("NavActive.TButton", background=[("active", SIDEBAR_ACTIVE_HOVER)])

    # ------------------------------------------------------------------
    # Layout
    # ------------------------------------------------------------------
    def _build_layout(self):
        self.columnconfigure(1, weight=1)
        self.rowconfigure(0, weight=1)

        self._build_sidebar()

        right = ttk.Frame(self)
        right.grid(row=0, column=1, sticky="nsew")
        right.columnconfigure(0, weight=1)
        right.rowconfigure(0, weight=1)

        self.content = ttk.Frame(right)
        self.content.grid(row=0, column=0, sticky="nsew")
        self.content.columnconfigure(0, weight=1)
        self.content.rowconfigure(0, weight=1)

        self.status = ttk.Label(
            right,
            text="Ready",
            anchor="w",
            padding=(16, 8),
            style="Status.TLabel",
        )
        self.status.grid(row=1, column=0, sticky="ew")

    def _build_sidebar(self):
        sidebar = tk.Frame(self, bg=SIDEBAR_BG, width=230)
        sidebar.grid(row=0, column=0, sticky="nsw")
        sidebar.grid_propagate(False)
        sidebar.columnconfigure(0, weight=1)
        sidebar.rowconfigure(99, weight=1)

        brand = tk.Frame(sidebar, bg=SIDEBAR_BG)
        brand.grid(row=0, column=0, sticky="ew", pady=(24, 8), padx=18)
        tk.Label(
            brand, text="DRAIE", bg=SIDEBAR_BG, fg="white",
            font=("Segoe UI", 20, "bold"), anchor="w",
        ).pack(anchor="w")
        tk.Label(
            brand, text="Resource Management", bg=SIDEBAR_BG, fg=SIDEBAR_TEXT,
            font=("Segoe UI", 9), anchor="w",
        ).pack(anchor="w")

        for index, (key, label, _view) in enumerate(NAV_ITEMS, start=1):
            button = ttk.Button(
                sidebar,
                text=label,
                style="Nav.TButton",
                command=lambda k=key: self.show_view(k),
            )
            button.grid(row=index, column=0, sticky="ew")
            self._nav_buttons[key] = button

        footer = tk.Label(
            sidebar,
            text="v0.1.0",
            bg=SIDEBAR_BG,
            fg=SIDEBAR_TEXT,
            font=("Segoe UI", 8),
            anchor="w",
        )
        footer.grid(row=100, column=0, sticky="ew", padx=18, pady=14)

    # ------------------------------------------------------------------
    # Navigation
    # ------------------------------------------------------------------
    def show_view(self, key: str):
        if key not in self._views:
            view_class = self._view_class(key)
            view = view_class(self.content, self.backend, self.set_status)
            view.grid(row=0, column=0, sticky="nsew")
            self._views[key] = view

        view = self._views[key]
        view.tkraise()
        if hasattr(view, "refresh"):
            view.refresh()

        self._active = key
        self._highlight_nav(key)

    def _view_class(self, key):
        for item_key, _label, view_class in NAV_ITEMS:
            if item_key == key:
                return view_class
        raise KeyError(key)

    def _highlight_nav(self, active_key):
        for key, button in self._nav_buttons.items():
            button.configure(
                style="NavActive.TButton" if key == active_key else "Nav.TButton"
            )

    def set_status(self, message: str):
        self.status.config(text=message)


def main():
    Application().mainloop()


if __name__ == "__main__":
    main()

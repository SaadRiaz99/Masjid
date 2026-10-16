"""Reusable tkinter/ttk building blocks for the DRAIE presentation layer."""

from __future__ import annotations

import tkinter as tk
from dataclasses import dataclass
from tkinter import messagebox, ttk

# ---------------------------------------------------------------------------
# Palette
# ---------------------------------------------------------------------------
SIDEBAR_BG = "#0f172a"
SIDEBAR_ACTIVE = "#2563eb"
SIDEBAR_ACTIVE_HOVER = "#1d4ed8"
SIDEBAR_HOVER = "#1e293b"
SIDEBAR_TEXT = "#cbd5e1"
CONTENT_BG = "#f1f5f9"
CARD_BG = "#ffffff"
MUTED = "#64748b"
DANGER = "#dc2626"


@dataclass
class Column:
    """A table column definition."""

    key: str
    heading: str
    width: int = 130
    anchor: str = "w"


@dataclass
class FieldSpec:
    """A form field definition used by :class:`RecordDialog`."""

    key: str
    label: str
    kind: str = "text"  # text | number | combo
    options: tuple = ()
    required: bool = True


class DataTable(ttk.Frame):
    """A Treeview wrapped with a scrollbar and row/selection helpers."""

    def __init__(self, parent, columns, on_double_click=None, **kwargs):
        super().__init__(parent, **kwargs)
        self.columns = list(columns)
        self._records: dict[str, dict] = {}

        self.tree = ttk.Treeview(
            self,
            columns=[c.key for c in self.columns],
            show="headings",
            selectmode="browse",
        )
        for col in self.columns:
            self.tree.heading(col.key, text=col.heading)
            self.tree.column(
                col.key, width=col.width, anchor=col.anchor, stretch=True
            )

        vsb = ttk.Scrollbar(self, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=vsb.set)
        self.tree.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")

        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

        self.tree.tag_configure("low", background="#fef3c7")
        self.tree.tag_configure("out", background="#fee2e2")

        if on_double_click is not None:
            self.tree.bind("<Double-1>", lambda _event: on_double_click())

    def set_rows(self, rows):
        self.tree.delete(*self.tree.get_children())
        self._records.clear()

        for index, row in enumerate(rows):
            iid = f"row{index}"
            values = [self._format(row.get(c.key, "")) for c in self.columns]
            self.tree.insert("", "end", iid=iid, values=values, tags=self._tags(row))
            self._records[iid] = row

    def selected(self) -> dict | None:
        selection = self.tree.selection()
        return self._records.get(selection[0]) if selection else None

    def clear(self):
        self.tree.delete(*self.tree.get_children())
        self._records.clear()

    @staticmethod
    def _format(value) -> str:
        if value is None:
            return ""
        return str(value)

    @staticmethod
    def _tags(row) -> tuple:
        status = str(row.get("status", "")).strip().lower()
        if status in {"out of stock", "out", "cancelled"}:
            return ("out",)
        if status in {"low", "pending"}:
            return ("low",)
        return ()


class RecordDialog(tk.Toplevel):
    """A modal form dialog generated from a list of :class:`FieldSpec`."""

    def __init__(self, parent, title, fields, initial=None):
        super().__init__(parent)
        self.title(title)
        self.fields = list(fields)
        self.result: dict | None = None

        self.transient(parent)
        self.resizable(False, False)
        self.configure(padx=0, pady=0)

        body = ttk.Frame(self, padding=22)
        body.pack(fill="both", expand=True)

        initial = initial or {}
        self._vars: dict[str, tk.StringVar] = {}

        for index, spec in enumerate(self.fields):
            ttk.Label(body, text=spec.label).grid(
                row=index, column=0, sticky="w", pady=7, padx=(0, 16)
            )
            var = tk.StringVar(value=str(initial.get(spec.key, "") or ""))
            self._vars[spec.key] = var

            if spec.kind == "combo" and spec.options:
                widget = ttk.Combobox(
                    body,
                    textvariable=var,
                    values=list(spec.options),
                    state="readonly",
                    width=30,
                )
            else:
                widget = ttk.Entry(body, textvariable=var, width=32)
            widget.grid(row=index, column=1, sticky="ew", pady=7)
            body.columnconfigure(1, weight=1)

        buttons = ttk.Frame(body)
        buttons.grid(
            row=len(self.fields), column=0, columnspan=2, sticky="e", pady=(18, 0)
        )
        ttk.Button(buttons, text="Cancel", command=self._cancel).pack(
            side="right", padx=(8, 0)
        )
        ttk.Button(buttons, text="Save", command=self._save).pack(side="right")

        self.bind("<Return>", lambda _e: self._save())
        self.bind("<Escape>", lambda _e: self._cancel())

        self._center_on(parent)
        self.grab_set()
        self.focus_set()
        self.wait_window(self)

    def _center_on(self, parent):
        self.update_idletasks()
        try:
            px, py = parent.winfo_rootx(), parent.winfo_rooty()
            pw, ph = parent.winfo_width(), parent.winfo_height()
        except tk.TclError:
            px = py = pw = ph = 0
        w, h = self.winfo_width(), self.winfo_height()
        x = px + max((pw - w) // 2, 0)
        y = py + max((ph - h) // 3, 0)
        self.geometry(f"+{x}+{y}")

    def _save(self):
        data: dict = {}
        for spec in self.fields:
            value = self._vars[spec.key].get().strip()
            if spec.required and not value:
                messagebox.showwarning(
                    "Validation", f"{spec.label} is required.", parent=self
                )
                return
            if spec.kind == "number" and value:
                try:
                    value = int(value)
                except ValueError:
                    try:
                        value = float(value)
                    except ValueError:
                        messagebox.showwarning(
                            "Validation",
                            f"{spec.label} must be a number.",
                            parent=self,
                        )
                        return
            data[spec.key] = value
        self.result = data
        self.destroy()

    def _cancel(self):
        self.result = None
        self.destroy()


class BaseView(ttk.Frame):
    """A generic CRUD screen: header + toolbar + data table.

    Subclasses declare ``columns`` / ``form_fields`` and implement the small
    ``fetch_rows`` / ``create`` / ``update`` / ``delete`` hooks, which call into
    the :class:`~src.presentation.backend.Backend`.
    """

    title = "View"
    subtitle = ""
    entity_name = "record"
    id_key = "id"
    columns: tuple[Column, ...] = ()
    form_fields: tuple[FieldSpec, ...] = ()

    def __init__(self, parent, backend, status_cb=None):
        super().__init__(parent, padding=(26, 22))
        self.backend = backend
        self._set_status = status_cb or (lambda _msg: None)
        self._rows: list[dict] = []

        self.columnconfigure(0, weight=1)
        self.rowconfigure(2, weight=1)

        self.search_var = tk.StringVar()
        self.search_var.trace_add("write", lambda *_a: self._apply_filter())

        self._build_header()
        self._build_toolbar()

        self.table = DataTable(self, self.columns, on_double_click=self.edit)
        self.table.grid(row=2, column=0, sticky="nsew", pady=(14, 0))

    # ------------------------------------------------------------------
    # Build helpers
    # ------------------------------------------------------------------
    def _build_header(self):
        header = ttk.Frame(self)
        header.grid(row=0, column=0, sticky="ew")
        ttk.Label(
            header, text=self.title, font=("Segoe UI", 18, "bold")
        ).pack(anchor="w")
        if self.subtitle:
            ttk.Label(
                header, text=self.subtitle, foreground=MUTED
            ).pack(anchor="w", pady=(2, 0))

    def _build_toolbar(self):
        bar = ttk.Frame(self)
        bar.grid(row=1, column=0, sticky="ew", pady=(16, 0))

        ttk.Button(bar, text="+ New", command=self.new).pack(side="left")
        ttk.Button(bar, text="Edit", command=self.edit).pack(side="left", padx=(8, 0))
        ttk.Button(bar, text="Delete", command=self.delete).pack(
            side="left", padx=(8, 0)
        )
        ttk.Button(bar, text="Refresh", command=self.refresh).pack(
            side="left", padx=(8, 0)
        )

        search = ttk.Frame(bar)
        search.pack(side="right")
        ttk.Label(search, text="Search:").pack(side="left", padx=(0, 6))
        ttk.Entry(search, textvariable=self.search_var, width=26).pack(side="left")

    # ------------------------------------------------------------------
    # CRUD actions
    # ------------------------------------------------------------------
    def new(self):
        data = RecordDialog(
            self.winfo_toplevel(),
            f"New {self.entity_name}",
            self.form_fields,
        ).result
        if data is None:
            return
        self._run(lambda: self.create_record(data), f"{self.entity_name} created")

    def edit(self):
        row = self.table.selected()
        if row is None:
            messagebox.showinfo("Select", f"Select a {self.entity_name} first.", parent=self)
            return
        data = RecordDialog(
            self.winfo_toplevel(),
            f"Edit {self.entity_name}",
            self.form_fields,
            initial=row,
        ).result
        if data is None:
            return
        self._run(
            lambda: self.update_record(row.get(self.id_key), data),
            f"{self.entity_name} updated",
        )

    def delete(self):
        row = self.table.selected()
        if row is None:
            messagebox.showinfo("Select", f"Select a {self.entity_name} first.", parent=self)
            return
        if not messagebox.askyesno(
            "Confirm", f"Delete the selected {self.entity_name}?", parent=self
        ):
            return
        self._run(
            lambda: self.delete_record(row.get(self.id_key)),
            f"{self.entity_name} deleted",
        )

    def refresh(self):
        try:
            rows = self.fetch_rows()
        except NotImplementedError as exc:
            self._rows = []
            self.table.clear()
            self._set_status(str(exc))
            return
        except Exception as exc:  # noqa: BLE001 - surfaced to the user
            self._rows = []
            self.table.clear()
            self._set_status(f"Error: {exc}")
            return

        self._rows = [self._to_dict(row) for row in (rows or [])]
        self._apply_filter()
        self._set_status(f"Loaded {len(self._rows)} {self.entity_name}(s)")

    # ------------------------------------------------------------------
    # Internals
    # ------------------------------------------------------------------
    def _run(self, action, success_message):
        try:
            action()
        except NotImplementedError as exc:
            messagebox.showinfo("Backend not implemented", str(exc), parent=self)
            return
        except Exception as exc:  # noqa: BLE001 - surfaced to the user
            messagebox.showerror("Error", str(exc), parent=self)
            return
        self.refresh()
        self._set_status(success_message)

    def _apply_filter(self):
        query = self.search_var.get().strip().lower()
        if query:
            rows = [
                row
                for row in self._rows
                if any(query in str(value).lower() for value in row.values())
            ]
        else:
            rows = self._rows
        self.table.set_rows(rows)

    @staticmethod
    def _to_dict(row) -> dict:
        if isinstance(row, dict):
            return dict(row)
        if hasattr(row, "__dict__"):
            return {k: v for k, v in vars(row).items() if not k.startswith("_")}
        return {"value": row}

    # ------------------------------------------------------------------
    # Hooks for subclasses
    # ------------------------------------------------------------------
    def fetch_rows(self):
        raise NotImplementedError

    def create_record(self, data):
        raise NotImplementedError

    def update_record(self, record_id, data):
        raise NotImplementedError

    def delete_record(self, record_id):
        raise NotImplementedError

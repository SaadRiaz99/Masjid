"""Inventory management view."""

from __future__ import annotations

from ..widgets import BaseView, Column, FieldSpec


class InventoryView(BaseView):
    title = "Inventory Management"
    subtitle = "Track disaster-relief resources and stock levels. Status is derived from stock."
    entity_name = "resource"

    columns = (
        Column("id", "ID", 60),
        Column("name", "Name", 170),
        Column("category", "Category", 120),
        Column("quantity", "Quantity", 90, "e"),
        Column("unit", "Unit", 80),
        Column("region", "Region", 130),
        Column("reorder_level", "Reorder", 90, "e"),
        Column("status", "Status", 120),
    )

    form_fields = (
        FieldSpec("name", "Name"),
        FieldSpec(
            "category",
            "Category",
            kind="combo",
            options=(
                "Medicine",
                "Food",
                "Water",
                "Shelter",
                "Equipment",
                "Clothing",
                "Other",
            ),
        ),
        FieldSpec("quantity", "Quantity", kind="number"),
        FieldSpec(
            "unit",
            "Unit",
            kind="combo",
            options=("pcs", "boxes", "kg", "liters", "packs", "units"),
        ),
        FieldSpec("region", "Region", kind="combo", options_from="regions", required=False),
        FieldSpec("reorder_level", "Reorder Level", kind="number", required=False),
    )

    def fetch_rows(self):
        return self.backend.list_resources()

    def create_record(self, data):
        return self.backend.add_resource(data)

    def update_record(self, record_id, data):
        return self.backend.update_resource(record_id, data)

    def delete_record(self, record_id):
        return self.backend.delete_resource(record_id)

"""Resource allocation view."""

from __future__ import annotations

from ..widgets import BaseView, Column, FieldSpec


class AllocationView(BaseView):
    title = "Resource Allocation"
    subtitle = "Dispatch resources to regions and track delivery."
    entity_name = "allocation"

    columns = (
        Column("id", "ID", 60),
        Column("resource", "Resource", 170),
        Column("region", "Region", 150),
        Column("quantity", "Quantity", 90, "e"),
        Column("priority", "Priority", 100),
        Column("date", "Date", 110),
        Column("status", "Status", 130),
    )

    form_fields = (
        FieldSpec("resource", "Resource", kind="combo", options_from="resources"),
        FieldSpec("region", "Region", kind="combo", options_from="regions"),
        FieldSpec("quantity", "Quantity", kind="number"),
        FieldSpec(
            "priority",
            "Priority",
            kind="combo",
            options=("Low", "Medium", "High", "Critical"),
        ),
        FieldSpec("date", "Date (YYYY-MM-DD)"),
        FieldSpec(
            "status",
            "Status",
            kind="combo",
            options=("Pending", "Approved", "In Transit", "Delivered", "Cancelled"),
        ),
    )

    def fetch_rows(self):
        return self.backend.list_allocations()

    def create_record(self, data):
        return self.backend.add_allocation(data)

    def update_record(self, record_id, data):
        return self.backend.update_allocation(record_id, data)

    def delete_record(self, record_id):
        return self.backend.delete_allocation(record_id)

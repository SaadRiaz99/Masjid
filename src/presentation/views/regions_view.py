"""Regional management view."""

from __future__ import annotations

from ..widgets import BaseView, Column, FieldSpec


class RegionsView(BaseView):
    title = "Regional Management"
    subtitle = "Maintain the regions served and their risk profiles."
    entity_name = "region"

    columns = (
        Column("id", "ID", 60),
        Column("name", "Region", 170),
        Column("district", "District", 150),
        Column("coordinator", "Coordinator", 170),
        Column("population", "Population", 110, "e"),
        Column("risk_level", "Risk Level", 110),
    )

    form_fields = (
        FieldSpec("name", "Region Name"),
        FieldSpec("district", "District"),
        FieldSpec("coordinator", "Coordinator", required=False),
        FieldSpec("population", "Population", kind="number", required=False),
        FieldSpec(
            "risk_level",
            "Risk Level",
            kind="combo",
            options=("Low", "Medium", "High", "Critical"),
        ),
    )

    def fetch_rows(self):
        return self.backend.list_regions()

    def create_record(self, data):
        return self.backend.add_region(data)

    def update_record(self, record_id, data):
        return self.backend.update_region(record_id, data)

    def delete_record(self, record_id):
        return self.backend.delete_region(record_id)

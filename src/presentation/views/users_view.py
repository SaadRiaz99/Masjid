"""Users & roles view."""

from __future__ import annotations

from ..widgets import BaseView, Column, FieldSpec


class UsersView(BaseView):
    title = "Users & Roles"
    subtitle = "Manage system accounts and their access levels."
    entity_name = "user"

    columns = (
        Column("id", "ID", 60),
        Column("name", "Name", 180),
        Column("username", "Username", 160),
        Column("role", "Role", 120),
        Column("region", "Region", 150),
        Column("status", "Status", 100),
    )

    form_fields = (
        FieldSpec("name", "Full Name"),
        FieldSpec("username", "Username"),
        FieldSpec(
            "role",
            "Role",
            kind="combo",
            options=("Admin", "Manager", "Coordinator", "Viewer"),
        ),
        FieldSpec("region", "Region", kind="combo", options_from="regions", required=False),
        FieldSpec(
            "status",
            "Status",
            kind="combo",
            options=("Active", "Inactive"),
        ),
    )

    def fetch_rows(self):
        return self.backend.list_users()

    def create_record(self, data):
        return self.backend.add_user(data)

    def update_record(self, record_id, data):
        return self.backend.update_user(record_id, data)

    def delete_record(self, record_id):
        return self.backend.delete_user(record_id)

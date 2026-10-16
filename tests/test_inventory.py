"""Tests for the inventory business rules."""

from __future__ import annotations

import tempfile
import unittest

from src.business import Actor, InventoryService, ValidationError
from src.data_access import Database


def make_resource(**overrides) -> dict:
    """A valid resource payload, as the form would hand it to the service."""
    resource = {
        "name": "First Aid Kit",
        "category": "Medicine",
        "quantity": 40,
        "unit": "boxes",
        "region": "North Valley",
        "reorder_level": 10,
    }
    resource.update(overrides)
    return resource


class InventoryServiceTests(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)

        self.admin = Actor(role="Admin")
        self.inventory = InventoryService(Database(self._tmp.name).resources, self.admin)

    # ------------------------------------------------------------------
    # Creating resources
    # ------------------------------------------------------------------
    def test_create_resource_assigns_id_and_derives_status(self):
        created = self.inventory.create(make_resource())

        self.assertEqual(created["id"], 1)
        self.assertEqual(created["status"], "In Stock")

    def test_low_stock_status_when_quantity_reaches_reorder_level(self):
        created = self.inventory.create(make_resource(quantity=10, reorder_level=10))

        self.assertEqual(created["status"], "Low")

    def test_out_of_stock_status_when_quantity_is_zero(self):
        created = self.inventory.create(make_resource(quantity=0))

        self.assertEqual(created["status"], "Out of Stock")

    def test_negative_quantity_is_rejected(self):
        with self.assertRaises(ValueError):
            self.inventory.create(make_resource(quantity=-5))

    def test_blank_name_is_rejected(self):
        with self.assertRaises(ValueError):
            self.inventory.create(make_resource(name="   "))

    def test_unknown_category_is_rejected(self):
        with self.assertRaises(ValueError):
            self.inventory.create(make_resource(category="Electronics"))

    def test_duplicate_names_are_rejected(self):
        self.inventory.create(make_resource())

        with self.assertRaises(ValidationError):
            self.inventory.create(make_resource(name="first aid kit"))

    # ------------------------------------------------------------------
    # Updating and deleting
    # ------------------------------------------------------------------
    def test_update_changes_quantity_and_recomputes_status(self):
        created = self.inventory.create(make_resource(quantity=40))

        updated = self.inventory.update(created["id"], {"quantity": 5})

        self.assertEqual(updated["quantity"], 5)
        self.assertEqual(updated["status"], "Low")

    def test_update_can_rename_a_resource(self):
        created = self.inventory.create(make_resource())

        updated = self.inventory.update(created["id"], {"name": "Trauma Kit"})

        self.assertEqual(updated["name"], "Trauma Kit")

    def test_update_rejects_a_name_used_by_another_resource(self):
        self.inventory.create(make_resource())
        other = self.inventory.create(make_resource(name="Water Bladder"))

        with self.assertRaises(ValidationError):
            self.inventory.update(other["id"], {"name": "First Aid Kit"})

    def test_delete_removes_the_resource(self):
        created = self.inventory.create(make_resource())

        self.inventory.delete(created["id"])

        self.assertEqual(self.inventory.list(), [])

    def test_unknown_id_raises_a_validation_error(self):
        with self.assertRaises(ValidationError):
            self.inventory.get(999)

    # ------------------------------------------------------------------
    # Persistence
    # ------------------------------------------------------------------
    def test_data_survives_a_new_service_instance(self):
        self.inventory.create(make_resource())

        reopened = InventoryService(Database(self._tmp.name).resources, self.admin)

        self.assertEqual(len(reopened.list()), 1)
        self.assertEqual(reopened.list()[0]["name"], "First Aid Kit")


if __name__ == "__main__":
    unittest.main()

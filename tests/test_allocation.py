"""Tests for allocation rules and the stock they hold."""

from __future__ import annotations

import tempfile
import unittest

from src.business import (
    Actor,
    AllocationService,
    InventoryService,
    RegionService,
    ValidationError,
)
from src.data_access import Database


class AllocationServiceTests(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)

        self.database = Database(self._tmp.name)
        self.actor = Actor(role="Admin")
        self.inventory = InventoryService(self.database.resources, self.actor)
        self.regions = RegionService(self.database.regions, self.actor)
        self.allocations = AllocationService(
            self.database.allocations, self.inventory, self.regions, self.actor
        )

        self.regions.create({"name": "Riverbend"})
        self.resource = self.inventory.create(
            {
                "name": "Bottled Water",
                "category": "Water",
                "quantity": 1000,
                "unit": "liters",
                "region": "Riverbend",
                "reorder_level": 100,
            }
        )

    def make_allocation(self, **overrides) -> dict:
        """A valid allocation payload, referencing the fixtures above."""
        allocation = {
            "resource": "Bottled Water",
            "region": "Riverbend",
            "quantity": 100,
            "priority": "High",
            "date": "2026-10-16",
            "status": "Pending",
        }
        allocation.update(overrides)
        return allocation

    def stock_of(self, name: str) -> int:
        return self.inventory.find_by_name(name).quantity

    # ------------------------------------------------------------------
    # Creating allocations
    # ------------------------------------------------------------------
    def test_creating_an_active_allocation_holds_the_stock(self):
        self.allocations.create(self.make_allocation())

        self.assertEqual(self.stock_of("Bottled Water"), 900)
        self.assertEqual(self.inventory.list()[0]["status"], "In Stock")

    def test_creating_a_cancelled_allocation_holds_no_stock(self):
        self.allocations.create(self.make_allocation(status="Cancelled"))

        self.assertEqual(self.stock_of("Bottled Water"), 1000)

    def test_more_stock_than_available_is_rejected(self):
        with self.assertRaises(ValueError):
            self.allocations.create(self.make_allocation(quantity=5000))

        self.assertEqual(self.stock_of("Bottled Water"), 1000)

    def test_unknown_resource_is_rejected(self):
        with self.assertRaises(ValidationError):
            self.allocations.create(self.make_allocation(resource="Space Food"))

    def test_unknown_region_is_rejected(self):
        with self.assertRaises(ValidationError):
            self.allocations.create(self.make_allocation(region="Nowhere"))

    def test_bad_date_format_is_rejected(self):
        with self.assertRaises(ValueError):
            self.allocations.create(self.make_allocation(date="16/10/2026"))

    def test_zero_quantity_is_rejected(self):
        with self.assertRaises(ValueError):
            self.allocations.create(self.make_allocation(quantity=0))

    # ------------------------------------------------------------------
    # Editing allocations
    # ------------------------------------------------------------------
    def test_cancelling_restores_the_stock(self):
        created = self.allocations.create(self.make_allocation())

        self.allocations.update(created["id"], {"status": "Cancelled"})

        self.assertEqual(self.stock_of("Bottled Water"), 1000)

    def test_reactivating_a_cancelled_allocation_holds_stock_again(self):
        created = self.allocations.create(self.make_allocation(status="Cancelled"))

        self.allocations.update(created["id"], {"status": "Approved"})

        self.assertEqual(self.stock_of("Bottled Water"), 900)

    def test_raising_the_quantity_holds_the_difference(self):
        created = self.allocations.create(self.make_allocation(quantity=100))

        self.allocations.update(created["id"], {"quantity": 250})

        self.assertEqual(self.stock_of("Bottled Water"), 750)

    def test_lowering_the_quantity_releases_the_difference(self):
        created = self.allocations.create(self.make_allocation(quantity=100))

        self.allocations.update(created["id"], {"quantity": 40})

        self.assertEqual(self.stock_of("Bottled Water"), 960)

    def test_switching_the_resource_moves_the_stock_across(self):
        self.inventory.create(
            {"name": "Tarpaulin", "category": "Shelter", "quantity": 50,
             "unit": "pcs", "region": "Riverbend"}
        )
        created = self.allocations.create(self.make_allocation(quantity=40))
        self.assertEqual(self.stock_of("Bottled Water"), 960)

        self.allocations.update(created["id"], {"resource": "Tarpaulin"})

        self.assertEqual(self.stock_of("Bottled Water"), 1000)
        self.assertEqual(self.stock_of("Tarpaulin"), 10)

    # ------------------------------------------------------------------
    # Deleting allocations
    # ------------------------------------------------------------------
    def test_deleting_an_active_allocation_releases_the_stock(self):
        created = self.allocations.create(self.make_allocation())

        self.allocations.delete(created["id"])

        self.assertEqual(self.stock_of("Bottled Water"), 1000)
        self.assertEqual(self.allocations.list(), [])

    def test_deleting_a_cancelled_allocation_changes_nothing(self):
        created = self.allocations.create(self.make_allocation(status="Cancelled"))

        self.allocations.delete(created["id"])

        self.assertEqual(self.stock_of("Bottled Water"), 1000)


if __name__ == "__main__":
    unittest.main()

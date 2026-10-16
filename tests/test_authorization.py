"""Tests for role based access control and region scoping."""

from __future__ import annotations

import tempfile
import unittest

from src.business import (
    Actor,
    AllocationService,
    InventoryService,
    RegionService,
    UserService,
)
from src.business.errors import AuthorizationError
from src.data_access import Database


class AuthorizationTests(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)

        self.database = Database(self._tmp.name)

    def services_for(self, role: str, region: str = "") -> dict:
        """Build all four services acting as the given role."""
        actor = Actor(role=role, region=region)
        inventory = InventoryService(self.database.resources, actor)
        regions = RegionService(self.database.regions, actor)
        allocations = AllocationService(
            self.database.allocations, inventory, regions, actor
        )
        return {
            "actor": actor,
            "inventory": inventory,
            "regions": regions,
            "allocations": allocations,
            "users": UserService(self.database.users, actor),
        }

    def seed(self) -> None:
        """Fill the tables with data for every test to share."""
        admin = self.services_for("Admin")
        admin["regions"].create({"name": "North Valley"})
        admin["regions"].create({"name": "Riverbend"})
        admin["inventory"].create(
            {"name": "Tent", "quantity": 50, "region": "North Valley"}
        )
        admin["inventory"].create(
            {"name": "Water", "quantity": 500, "region": "Riverbend"}
        )
        admin["allocations"].create(
            {"resource": "Tent", "region": "North Valley", "quantity": 5,
             "date": "2026-10-16"}
        )
        admin["users"].create(
            {"name": "Ali Raza", "username": "ali", "role": "Coordinator",
             "region": "North Valley"}
        )

    # ------------------------------------------------------------------
    # Read access
    # ------------------------------------------------------------------
    def test_admin_manager_and_viewer_can_read_every_entity(self):
        self.seed()

        for role in ("Admin", "Manager", "Viewer"):
            services = self.services_for(role, region="North Valley")
            self.assertEqual(len(services["inventory"].list()), 2, role)
            self.assertEqual(len(services["regions"].list()), 2, role)
            self.assertEqual(len(services["allocations"].list()), 1, role)
            self.assertEqual(len(services["users"].list()), 1, role)

    def test_coordinator_can_read_but_only_within_their_region(self):
        self.seed()
        coordinator = self.services_for("Coordinator", region="North Valley")

        self.assertEqual(len(coordinator["regions"].list()), 2)
        self.assertEqual(len(coordinator["users"].list()), 1)
        self.assertEqual(len(coordinator["allocations"].list()), 1)
        names = [row["name"] for row in coordinator["inventory"].list()]
        self.assertEqual(names, ["Tent"])

    # ------------------------------------------------------------------
    # Viewer
    # ------------------------------------------------------------------
    def test_viewer_cannot_write_to_anything(self):
        self.seed()
        viewer = self.services_for("Viewer")

        with self.assertRaises(AuthorizationError):
            viewer["inventory"].create({"name": "Radio"})
        with self.assertRaises(AuthorizationError):
            viewer["regions"].create({"name": "Highland"})
        with self.assertRaises(AuthorizationError):
            viewer["allocations"].create(
                {"resource": "Tent", "region": "North Valley", "quantity": 1,
                 "date": "2026-10-16"}
            )
        with self.assertRaises(AuthorizationError):
            viewer["users"].create({"name": "New Person", "username": "new"})

    # ------------------------------------------------------------------
    # Manager
    # ------------------------------------------------------------------
    def test_manager_runs_inventory_and_allocations(self):
        self.seed()
        manager = self.services_for("Manager")

        manager["inventory"].create({"name": "Radio", "quantity": 10})
        manager["regions"].create({"name": "Highland"})
        manager["allocations"].create(
            {"resource": "Radio", "region": "Highland", "quantity": 2,
             "date": "2026-10-16"}
        )

        self.assertEqual(len(manager["inventory"].list()), 3)

    def test_manager_cannot_manage_users(self):
        self.seed()
        manager = self.services_for("Manager")

        with self.assertRaises(AuthorizationError):
            manager["users"].create({"name": "Sneaky", "username": "sneaky"})

    # ------------------------------------------------------------------
    # Admin
    # ------------------------------------------------------------------
    def test_admin_manages_users(self):
        self.seed()
        admin = self.services_for("Admin")

        created = admin["users"].create(
            {"name": "Nadia", "username": "nadia", "role": "Viewer"}
        )
        admin["users"].update(created["id"], {"role": "Manager"})
        admin["users"].delete(created["id"])

        self.assertEqual(admin["users"].list()[0]["username"], "ali")

    # ------------------------------------------------------------------
    # Coordinator scoping
    # ------------------------------------------------------------------
    def test_coordinator_cannot_create_a_resource_outside_their_region(self):
        self.seed()
        coordinator = self.services_for("Coordinator", region="North Valley")

        with self.assertRaises(AuthorizationError):
            coordinator["inventory"].create(
                {"name": "Generator", "region": "Riverbend"}
            )

    def test_coordinator_cannot_update_a_resource_outside_their_region(self):
        self.seed()
        water = next(
            row for row in self.services_for("Admin")["inventory"].list()
            if row["name"] == "Water"
        )
        coordinator = self.services_for("Coordinator", region="North Valley")

        with self.assertRaises(AuthorizationError):
            coordinator["inventory"].update(water["id"], {"quantity": 1})

    def test_coordinator_cannot_create_regions_or_users(self):
        self.seed()
        coordinator = self.services_for("Coordinator", region="North Valley")

        with self.assertRaises(AuthorizationError):
            coordinator["regions"].create({"name": "New Place"})
        with self.assertRaises(AuthorizationError):
            coordinator["users"].create({"name": "Someone", "username": "someone"})

    # ------------------------------------------------------------------
    # Unknown roles
    # ------------------------------------------------------------------
    def test_unknown_role_has_no_permissions_at_all(self):
        self.seed()
        stranger = self.services_for("Visitor")

        with self.assertRaises(AuthorizationError):
            stranger["inventory"].list()
        with self.assertRaises(AuthorizationError):
            stranger["regions"].list()


if __name__ == "__main__":
    unittest.main()

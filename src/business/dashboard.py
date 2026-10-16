"""Dashboard figures, assembled from the four entity services."""

from __future__ import annotations

from .permissions import require


def build_summary(inventory, regions, allocations, users) -> dict:
    """Return the headline numbers shown on the dashboard.

    Keys: ``resources``, ``regions``, ``allocations``, ``users``,
    ``low_stock``.
    """
    require(inventory.actor, "resource", "read")
    require(regions.actor, "region", "read")
    require(allocations.actor, "allocation", "read")
    require(users.actor, "user", "read")

    resources = inventory.list()
    return {
        "resources": len(resources),
        "regions": len(regions.list()),
        "allocations": len(allocations.list()),
        "users": len(users.list()),
        "low_stock": sum(
            1 for row in resources if row.get("status") in ("Low", "Out of Stock")
        ),
    }

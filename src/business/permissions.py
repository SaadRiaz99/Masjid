"""Role based access control for the business services.

Every service receives an :class:`Actor` (who is asking) and calls
:func:`require` before doing any work.  Region scoping for coordinators is
handled by :func:`in_scope` / :func:`ensure_in_scope`.
"""

from __future__ import annotations

from dataclasses import dataclass

from .errors import AuthorizationError

ACTIONS = ("read", "create", "update", "delete")

_READ_ONLY = frozenset({"read"})
_EVERYTHING = frozenset(ACTIONS)

#: role -> entity -> set of actions that role may perform on that entity.
CAPABILITIES: dict[str, dict[str, frozenset]] = {
    "Admin": {
        "resource": _EVERYTHING,
        "region": _EVERYTHING,
        "allocation": _EVERYTHING,
        "user": _EVERYTHING,
    },
    "Manager": {
        "resource": _EVERYTHING,
        "region": frozenset({"read", "create", "update"}),
        "allocation": _EVERYTHING,
        "user": _READ_ONLY,
    },
    "Coordinator": {
        "resource": frozenset({"read", "update"}),
        "region": _READ_ONLY,
        "allocation": frozenset({"read", "create", "update"}),
        "user": _READ_ONLY,
    },
    "Viewer": {
        "resource": _READ_ONLY,
        "region": _READ_ONLY,
        "allocation": _READ_ONLY,
        "user": _READ_ONLY,
    },
}


@dataclass(frozen=True)
class Actor:
    """Who a business request is being made on behalf of.

    ``region`` matters for coordinators: it is the one region they are
    allowed to see and touch.
    """

    role: str = "Admin"
    region: str = ""


def can(role: str, entity: str, action: str) -> bool:
    """Check whether ``role`` may perform ``action`` on ``entity``."""
    return action in CAPABILITIES.get(role, {}).get(entity, frozenset())


def require(actor: Actor, entity: str, action: str) -> None:
    """Raise :class:`AuthorizationError` unless the actor may act."""
    if not can(actor.role, entity, action):
        raise AuthorizationError(
            f"{actor.role} is not allowed to {action} {entity}s."
        )


def in_scope(actor: Actor, region: str) -> bool:
    """Coordinators only see their own region; every other role sees all."""
    if actor.role != "Coordinator":
        return True
    return (region or "").strip().casefold() == (actor.region or "").strip().casefold()


def ensure_in_scope(actor: Actor, region: str) -> None:
    """Raise :class:`AuthorizationError` if ``region`` is outside the actor's scope."""
    if not in_scope(actor, region):
        raise AuthorizationError(
            f"Coordinators can only work within their own region "
            f"({actor.region or 'not set'})."
        )

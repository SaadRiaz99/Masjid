"""Errors the business layer raises.

Both classes deliberately inherit from standard exceptions so callers that
only know ``ValueError`` / ``PermissionError`` still work.
"""

from __future__ import annotations


class ValidationError(ValueError):
    """The request was understood but the data is not acceptable.

    Examples: a duplicate name, an unknown region, a missing reference.
    """


class AuthorizationError(PermissionError):
    """The acting user is not allowed to perform the requested action."""

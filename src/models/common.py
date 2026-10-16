"""Small conversion helpers shared by every domain model.

Keeping the conversions in one place means each model reads as a plain list
of fields plus a ``validate`` method, instead of a wall of type juggling.
"""

from __future__ import annotations


def as_text(value, field: str) -> str:
    """Return ``value`` as a stripped string (``None`` becomes ``""``)."""
    if value is None:
        return ""
    return str(value).strip()


def require_text(value, field: str) -> str:
    """Same as :func:`as_text` but rejects empty values."""
    text = as_text(value, field)
    if not text:
        raise ValueError(f"{field} cannot be empty.")
    return text


def as_int(value, field: str, default: int | None = None) -> int:
    """Convert ``value`` to an int.

    Blank values fall back to ``default`` when one is given, otherwise they
    raise an error that names the offending field.
    """
    if value is None or str(value).strip() == "":
        if default is not None:
            return default
        raise ValueError(f"{field} is required.")
    try:
        return int(float(str(value).strip()))
    except ValueError:
        raise ValueError(f"{field} must be a number.") from None


def one_of(value, field: str, allowed: tuple, default: str = "") -> str:
    """Return the canonical entry from ``allowed`` matching ``value``.

    Matching is case-insensitive so typing ``low`` is the same as ``Low``.
    Blank values fall back to ``default`` (which may be ``""``).
    """
    text = as_text(value, field)
    if not text:
        return default

    canonical = {option.lower(): option for option in allowed}
    match = canonical.get(text.lower())
    if match is None:
        choices = ", ".join(allowed)
        raise ValueError(f"{field} must be one of: {choices}.")
    return match

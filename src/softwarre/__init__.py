"""Console script behind the ``softwarre`` command."""

from __future__ import annotations


def main() -> None:
    """Launch the DRAIE desktop application."""
    try:
        # Installed layout: the ``src`` folder itself is on sys.path.
        from presentation.app import main as run_app
    except ImportError:
        # Running from the project root: imports go through ``src``.
        from src.presentation.app import main as run_app

    run_app()

"""Architecture boundary tests.

These tests are run via import-linter, not pytest directly.
Run with: uv run lint-imports

This file serves as documentation and a pytest-discoverable placeholder.
The actual rules are defined in backend/.importlinter.
"""

import pytest


@pytest.mark.architecture
def test_import_boundaries_documentation():
    """Import boundaries are enforced by import-linter. See backend/.importlinter."""

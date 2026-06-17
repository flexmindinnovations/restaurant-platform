import os
import subprocess  # noqa: S404
from pathlib import Path

import pytest


@pytest.mark.architecture
def test_import_boundaries() -> None:
    """Run import-linter via subprocess to verify module separation and domain purity rules."""
    # Locate backend root directory
    backend_dir = Path(__file__).resolve().parent.parent.parent

    # Configure environment with PYTHONPATH pointing to src
    env = os.environ.copy()
    env["PYTHONPATH"] = str(backend_dir / "src")

    # Execute lint-imports command
    result = subprocess.run(
        ["lint-imports"],  # noqa: S607
        capture_output=True,
        text=True,
        cwd=str(backend_dir),
        env=env,
        check=False,
    )

    # Assert success and output errors if failed
    assert result.returncode == 0, f"Import boundaries check failed:\n{result.stdout}\n{result.stderr}"

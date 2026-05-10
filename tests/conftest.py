"""Shared pytest fixtures for the can-log-summarizer test suite.

Anything defined here is automatically available to any test in `tests/`
without imports. Pytest discovers conftest.py files automatically.

Convention: keep this file small. Test-specific fixtures belong in the
test files themselves. Fixtures here should be genuinely shared.
"""
from pathlib import Path
import sys

import pytest


# Make the project's `src/` directory importable from any test.
# This lets tests do `from src.parser import parse_asc` instead of
# fighting with sys.path in every test file.
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))


@pytest.fixture(scope="session")
def project_root() -> Path:
    """Absolute path to the project root."""
    return PROJECT_ROOT


@pytest.fixture(scope="session")
def fixtures_dir() -> Path:
    """Absolute path to tests/fixtures/."""
    return PROJECT_ROOT / "tests" / "fixtures"


@pytest.fixture(scope="session")
def synthetic_fixtures_dir(fixtures_dir: Path) -> Path:
    """Absolute path to tests/fixtures/synthetic/."""
    return fixtures_dir / "synthetic"


@pytest.fixture(scope="session")
def real_fixtures_dir(fixtures_dir: Path) -> Path:
    """Absolute path to tests/fixtures/real/."""
    return fixtures_dir / "real"


@pytest.fixture(scope="session")
def dbc_fixtures_dir(fixtures_dir: Path) -> Path:
    """Absolute path to tests/fixtures/dbcs/."""
    return fixtures_dir / "dbcs"


@pytest.fixture(scope="session")
def project_dbc(project_root: Path) -> Path:
    """The bundled toyota.dbc from the production data directory.

    Use this when a test needs the real DBC the production code uses.
    For tests that need a controlled minimal DBC, use a fixture from
    `dbc_fixtures_dir` instead.
    """
    return project_root / "data" / "dbcs" / "toyota.dbc"

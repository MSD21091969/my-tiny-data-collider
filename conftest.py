"""
Root conftest.py - Project-level test configuration.

CRITICAL: Test directories must NOT have __init__.py files!

With package-dir = {"": "src"} in pyproject.toml, pytest's prepend mode
adds src/ to sys.path automatically. But if tests/ has __init__.py files,
pytest treats test directories as packages matching source code structure,
causing import confusion.

Solution: Tests are NOT packages - they import from the installed package.
"""
import sys
from pathlib import Path


def pytest_load_initial_conftests(early_config, parser, args):
    """
    Ensure src/ is in sys.path before test collection.
    
    This hook runs early enough to fix imports for pytest 8.x.
    """
    project_root = Path(__file__).parent
    src_path = project_root / "src"
    
    if str(src_path) not in sys.path:
        sys.path.insert(0, str(src_path))

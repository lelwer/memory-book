"""Pytest configuration to make the project root importable during tests.

This inserts the repository root (parent of `tests/`) at the front of
`sys.path` so that `import src.main` and similar imports work when running
pytest from any working directory.
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

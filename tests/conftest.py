"""Pytest configuration and shared fixtures."""

import sys
from pathlib import Path

import pytest

# Add pythonx directory to path so tests can import vim4rabbit
pythonx_path = Path(__file__).parent.parent / "pythonx"
if str(pythonx_path) not in sys.path:
    sys.path.insert(0, str(pythonx_path))

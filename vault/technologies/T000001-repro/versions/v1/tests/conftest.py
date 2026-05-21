"""Shared pytest fixtures and sys.path setup for the repro test suite."""

from __future__ import annotations

import sys
from pathlib import Path

# The repro package lives at ../src/repro relative to this file.
# Make it importable without requiring an install step.
_TECH_ROOT = Path(__file__).resolve().parent.parent
_SRC_DIR = _TECH_ROOT / "src"
if str(_SRC_DIR) not in sys.path:
    sys.path.insert(0, str(_SRC_DIR))

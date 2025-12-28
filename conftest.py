"""Test configuration for local development.

Ensures the repository root is on sys.path during pytest collection so tests
can import the `app` package and the `tests` modules as expected.
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

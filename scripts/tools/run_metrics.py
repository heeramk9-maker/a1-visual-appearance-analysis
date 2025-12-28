"""Utility helpers for console-only observability in runner scripts.

Exposes:
- analysis_timer() context manager usable in both sync and async code
- print_model_used(client)

This module is intentionally dependency-free and lightweight.
"""
from __future__ import annotations

import time
from typing import Optional


class _AnalysisTimer:
    """Context manager that prints 'Analyzing...' on enter and prints
    elapsed time on exit. Supports both sync and async contexts.
    """

    def __init__(self) -> None:
        self._start: Optional[float] = None

    def __enter__(self):
        print("Analyzing...")
        self._start = time.monotonic()
        return self

    def __exit__(self, exc_type, exc, tb):
        elapsed = 0.0
        if self._start is not None:
            elapsed = time.monotonic() - self._start
        print(f"Analyzing completed in {elapsed:.2f}s")

    async def __aenter__(self):
        print("Analyzing...")
        self._start = time.monotonic()
        return self

    async def __aexit__(self, exc_type, exc, tb):
        elapsed = 0.0
        if self._start is not None:
            elapsed = time.monotonic() - self._start
        print(f"Analyzing completed in {elapsed:.2f}s")


def analysis_timer():
    """Return a context manager usable as either ``with analysis_timer():`` or
    ``async with analysis_timer():`` to measure and print analysis runtime.
    """
    return _AnalysisTimer()


def print_model_used(client: object) -> str:
    """Safely print and return a model identifier for the provided client.

    Logic:
    - If `client` exposes a `model` attribute, use that value.
    - Otherwise return and print the sentinel string "mock-client".
    """
    model = getattr(client, "model", None)
    model_name = model if model else "mock-client"
    print("Model Used:", model_name)
    return model_name

"""Simple in-memory cache for per-image A1.0 analysis results.

This cache is deterministic, optional, and safe to disable. It stores
validated per-image results keyed by `image_id`.
"""
from __future__ import annotations

from typing import Dict, Any


class ResultCache:
    """Simple in-memory deterministic cache for per-image A1.0 results.

    Features:
    - tracks hits and misses (useful for lightweight telemetry)
    - optional verbose mode to print hits/misses for demos
    - deterministic, in-memory only (no persistence)

    Design note: the cache is intentionally minimal and separate from model
    code; pipeline coordinates calling the cache (lookup before analysis,
    store after final validation) which ensures correctness and avoids
    caching partially validated outputs.
    """

    def __init__(self, verbose: bool = False) -> None:
        self._store: Dict[str, Any] = {}
        self.hits = 0
        self.misses = 0
        self.verbose = verbose

    def get(self, key: str):
        """Return cached value or None. Increment hit/miss counters.

        The method is lightweight and side-effect free besides updating
        in-memory counters. If verbose is True it will print a small
        message to stdout to aid debugging and demos.
        """
        if key in self._store:
            self.hits += 1
            if self.verbose:
                print(f"CACHE HIT: {key}")
            return self._store.get(key)
        else:
            self.misses += 1
            if self.verbose:
                print(f"CACHE MISS: {key}")
            return None

    def set(self, key: str, value: Any) -> None:
        """Store a validated result in the cache."""
        self._store[key] = value

    def clear(self) -> None:
        """Clear cache contents and reset counters."""
        self._store.clear()
        self.hits = 0
        self.misses = 0

    def stats(self) -> Dict[str, int]:
        """Return simple stats useful for tests/demos."""
        return {"hits": self.hits, "misses": self.misses}


__all__ = ["ResultCache"]
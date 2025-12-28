"""Async cache behavior test: ensure process_images_async respects ResultCache semantics."""
from __future__ import annotations

import asyncio

from app.async_pipeline import process_images_async
from app.cache import ResultCache


def test_async_respects_cache():
    cache = ResultCache()

    calls = {"n": 0}

    def counting_client(image, prompts):
        calls["n"] += 1
        return {
            "visual_measurements": {
                "gender_expression": {"score": 0.5, "justification": "x", "uncertain": False},
                "visual_weight": {"score": -1.0, "justification": "x", "uncertain": False},
                "embellishment": {"score": -2.0, "justification": "x", "uncertain": False},
                "unconventionality": {"score": -1.0, "justification": "x", "uncertain": False},
                "formality": {"score": 0.0, "justification": "x", "uncertain": False},
            },
            "attributes": {},
        }

    images = [{"id": "img-cache-1", "source": "x.jpg", "type": "local"}]
    prompts = {"system": "s", "task": "t"}

    # First run -> miss
    results1 = asyncio.run(process_images_async(images, prompts, counting_client, cache=cache, concurrency=2))
    assert calls["n"] == 1
    assert cache.stats()["misses"] == 1
    assert cache.stats()["hits"] == 0

    # Second run -> served from cache, client not called again
    results2 = asyncio.run(process_images_async(images, prompts, counting_client, cache=cache, concurrency=2))
    assert calls["n"] == 1
    assert cache.stats()["hits"] == 1
    assert results1[0] == results2[0]

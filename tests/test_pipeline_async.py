"""Tests for the async pipeline wrapper."""
from __future__ import annotations

import asyncio

from app.async_pipeline import process_images_async
from app.vision_client import mock_vision_client
from app.prompts import SYSTEM_PROMPT, TASK_PROMPT


def test_async_process_multiple_images_success():
    images = [
        {"id": "img1", "source": "a.jpg", "type": "local"},
        {"id": "img2", "source": "b.jpg", "type": "local"},
        {"id": "img3", "source": "c.jpg", "type": "local"},
    ]

    client = mock_vision_client()
    prompts = {"system": SYSTEM_PROMPT, "task": TASK_PROMPT}

    results = asyncio.run(process_images_async(images, prompts, client, cache=None, concurrency=2))

    assert isinstance(results, list)
    assert len(results) == 3
    for res in results:
        # successful results should include validated visual_measurements mapping
        assert "visual_measurements" in res
        assert isinstance(res["visual_measurements"], dict)
        # no top-level errors expected in successful cases
        assert not res.get("errors")


def test_async_isolated_error_handling():
    images = [
        {"id": "ok1", "source": "a.jpg", "type": "local"},
        {"id": "bad", "source": "b.jpg", "type": "local"},
        {"id": "ok2", "source": "c.jpg", "type": "local"},
    ]

    base_client = mock_vision_client()

    def flaky_client(image, prompts):
        if isinstance(image, dict) and image.get("id") == "bad":
            raise RuntimeError("simulated client failure for testing")
        return base_client(image, prompts)

    prompts = {"system": SYSTEM_PROMPT, "task": TASK_PROMPT}

    results = asyncio.run(process_images_async(images, prompts, flaky_client, cache=None, concurrency=3))

    # Ensure ordering preserved
    assert results[0].get("image_id") == "ok1"

    # Second result should contain an analysis error (raised inside analyze_image)
    bad_res = results[1]
    assert "errors" in bad_res
    assert any(e.get("stage") == "analysis" for e in bad_res["errors"]) or any(e.get("stage") == "async_execution" for e in bad_res["errors"])  # accept either depending on where it was caught

    # Third result should be successful
    assert "visual_measurements" in results[2]


if __name__ == "__main__":
    test_async_process_multiple_images_success()
    test_async_isolated_error_handling()
    print("OK: async tests passed")

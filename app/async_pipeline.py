"""async_pipeline.py

Safe, production-minded async wrapper around the existing synchronous
`process_single_image` pipeline.

Constraints preserved:
- Does NOT modify any existing synchronous logic
- `process_single_image()` remains untouched
- Uses `asyncio.to_thread()` for running sync calls concurrently
- Each image is processed independently with isolated error handling
- Preserves per-image output format (returns process_single_image return values
  directly when possible; on unexpected exceptions returns a structured error
  dict compatible with pipeline outputs)

The module intentionally stays small and simple so it can be audited and
reused in higher-level services.
"""
from __future__ import annotations

import asyncio
import logging
from typing import Any, Dict, Iterable, List, Optional

from app.pipeline import process_single_image

logger = logging.getLogger(__name__)


async def _run_image_in_thread(
    image: Any,
    prompts: Any,
    client: Any,
    cache: Any,
    semaphore: Optional[asyncio.Semaphore] = None,
) -> Dict[str, Any]:
    """Run `process_single_image` for a single image inside a thread pool.

    This helper isolates exceptions so that a failure for one image does
    not cancel the rest of the batch. It returns either the exact result
    from `process_single_image`, or a minimal error dict that matches the
    pipeline's error shape.
    """
    if semaphore is None:
        # No concurrency limit requested
        acquire = None
    else:
        acquire = semaphore.acquire()

    try:
        if semaphore is not None:
            await acquire
        # Run the blocking sync pipeline in a thread to avoid blocking the
        # event loop.
        result = await asyncio.to_thread(process_single_image, image, prompts, client, cache)
        # Defensive: ensure result is a dict (the sync pipeline returns dicts)
        if not isinstance(result, dict):
            logger.warning("process_single_image returned non-dict result for image %r", image)
            return {"image": image, "errors": [{"stage": "finalization", "error": "non-dict pipeline result"}], "raw": None}
        return result
    except asyncio.CancelledError:
        # Preserve cancellation semantics but return a structured error
        logger.exception("Task cancelled while processing image %r", image)
        return {"image": image, "errors": [{"stage": "async_cancelled", "error": "task cancelled"}], "raw": None}
    except Exception as e:  # pragma: no cover - defensive branch
        logger.exception("Unexpected error while processing image %r: %s", image, e)
        return {"image": image, "errors": [{"stage": "async_execution", "error": str(e)}], "raw": None}
    finally:
        if semaphore is not None:
            semaphore.release()


async def process_images_async(
    images: Iterable[Any],
    prompts: Any,
    client: Any,
    cache: Any = None,
    concurrency: int = 5,
) -> List[Dict[str, Any]]:
    """Process multiple images concurrently using `process_single_image`.

    Args:
        images: Iterable of image references (each the same shape accepted by
                `process_single_image`). The input order is preserved in the
                returned list.
        prompts: Prompts passed through to `process_single_image`.
        client: Vision client passed through to `process_single_image`.
        cache: Optional cache instance (passed through) – cache semantics are
               still synchronous and handled by the underlying pipeline.
        concurrency: Max number of concurrent worker threads.

    Returns:
        A list of per-image results (dicts). Each result will be either the
        original `process_single_image` return value for that image or an
        error-shaped dict if processing failed in an unexpected way.
    """
    if not isinstance(images, (list, tuple)):
        images = list(images)

    if concurrency is None or concurrency <= 0:
        concurrency = 5

    semaphore = asyncio.Semaphore(concurrency)

    tasks = [
        asyncio.create_task(_run_image_in_thread(img, prompts, client, cache, semaphore))
        for img in images
    ]

    # Await all tasks; per-task exceptions are handled inside the helper so
    # `gather` should not raise. We keep ordering stable by awaiting the
    # created tasks as a single group.
    results = await asyncio.gather(*tasks)
    return results


__all__ = ["process_images_async"]

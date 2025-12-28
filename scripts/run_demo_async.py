"""
run_demo_async.py

Async demo runner that shows how to process many images concurrently
without changing the existing synchronous pipeline implementation.

Usage:
    python scripts/run_demo_async.py <folder_path> [concurrency]

Example:
    python scripts/run_demo_async.py data/sample_images/product_231031 4

This script uses the same A1.0-compatible mock client by default and
preserves the exact per-image output shapes produced by the original
pipeline.
"""
from __future__ import annotations

import asyncio
import sys
from pathlib import Path
from typing import List, Optional

# Ensure project root is on PYTHONPATH
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.async_pipeline import process_images_async
from app.aggregator import aggregate_results
from app.exporter import export_product_result
from app.prompts import SYSTEM_PROMPT, TASK_PROMPT
from app.vision_client import mock_vision_client

SUPPORTED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}


def collect_images(folder: Path) -> List[dict]:
    image_refs = []

    for img_path in sorted(folder.iterdir()):
        if img_path.suffix.lower() not in SUPPORTED_EXTENSIONS:
            continue

        image_refs.append(
            {
                "id": img_path.stem,
                "source": str(img_path),
                "type": "local",
            }
        )

    if not image_refs:
        raise ValueError("No supported image files found in folder")

    return image_refs


async def main_async(folder: Path, concurrency: int = 5) -> None:
    print("============================================================")
    print(">>> ASYNC FOLDER-BASED VISUAL ANALYSIS DEMO <<<")
    print("============================================================")
    print(f"📂 Input folder: {folder}")

    client = mock_vision_client()

    image_refs = collect_images(folder)
    print(f"📸 Found {len(image_refs)} image(s)")

    prompts = {"system": SYSTEM_PROMPT, "task": TASK_PROMPT}

    print(f"⚡ Processing up to {concurrency} images concurrently...")
    per_image_results = await process_images_async(
        images=image_refs,
        prompts=prompts,
        client=client,
        cache=None,
        concurrency=concurrency,
    )

    print("📈 Aggregating per-image results...")
    aggregated = aggregate_results(per_image_results)

    output = export_product_result(
        aggregated,
        product_id=folder.name,
        output_dir="outputs",
        as_csv=True,
    )

    print("============================================================")
    print("✅ Async analysis complete")
    print("------------------------------------------------------------")
    print(f"JSON output: {output['json']}")
    print(f"CSV output : {output['csv']}")
    print("============================================================")


def main(argv: Optional[List[str]] = None) -> None:
    argv = argv if argv is not None else sys.argv

    if len(argv) < 2:
        print("Usage: python scripts/run_demo_async.py <folder_path> [concurrency]")
        sys.exit(1)

    folder = Path(argv[1])
    if not folder.exists() or not folder.is_dir():
        print(f"Invalid folder path: {folder}")
        sys.exit(1)

    concurrency = 5
    if len(argv) >= 3:
        try:
            concurrency = int(argv[2])
            if concurrency <= 0:
                raise ValueError()
        except ValueError:
            print("Invalid concurrency value; must be a positive integer")
            sys.exit(1)

    asyncio.run(main_async(folder, concurrency=concurrency))


if __name__ == "__main__":
    main()

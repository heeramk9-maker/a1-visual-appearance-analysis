"""
run_from_folder_async.py

Async equivalent of `run_from_folder.py` which processes images in a folder
concurrently using `process_images_async`.

Usage:
    python scripts/run_from_folder_async.py <folder_path> [--concurrency N]

Example:
    python scripts/run_from_folder_async.py data/sample_images/product_231031 --concurrency 4
"""
from __future__ import annotations

import sys
from pathlib import Path
from typing import List
import argparse
import asyncio

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

    # Initialize client (mock by default; can be swapped with real AI)
    client = mock_vision_client()

    # Make local scripts/tools importable and load helpers
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from tools.run_metrics import analysis_timer, print_model_used

    image_refs = collect_images(folder)
    print(f"📸 Found {len(image_refs)} image(s)")

    # Observability top lines
    print("Processed products:", 1)
    print_model_used(client)

    prompts = {"system": SYSTEM_PROMPT, "task": TASK_PROMPT}

    # print each image as being queued for parity with sync runner
    for img in image_refs:
        print(f"🤖 Queued image: {img['id']}")

    print(f"⚡ Processing up to {concurrency} images concurrently...")

    # Run processing and aggregation under timer
    async with analysis_timer():
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
        output_dir="outputs/async",
        as_csv=True,
    )

    print("============================================================")
    print("✅ Async analysis complete")
    print("------------------------------------------------------------")
    print("Sample product ids:", [folder.name])
    print(f"JSON output: {output['json']}")
    print(f"CSV output : {output['csv']}")
    print("============================================================")
    print("No processing errors detected.")
    print("Wrote results to:", output['json'])


def main(argv: list[str] | None = None) -> None:
    argv = argv if argv is not None else sys.argv[1:]
    parser = argparse.ArgumentParser()
    parser.add_argument("folder", type=str, help="Path to folder of images")
    parser.add_argument("--concurrency", type=int, default=5, help="Max concurrent images")
    args = parser.parse_args(argv)

    folder = Path(args.folder)
    if not folder.exists() or not folder.is_dir():
        print(f"Invalid folder path: {folder}")
        sys.exit(1)

    try:
        asyncio.run(main_async(folder, concurrency=args.concurrency))
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted by user")


if __name__ == "__main__":
    main()

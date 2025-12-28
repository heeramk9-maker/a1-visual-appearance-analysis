"""
run_from_folder.py

CLI interface to analyze one product using multiple local image files.

This script demonstrates a clean, minimal user interface for submitting
product images via a folder path, without requiring a web UI.

Usage:
    python scripts/run_from_folder.py <folder_path>

Example:
    python scripts/run_from_folder.py data/sample_images/product_231031

The folder should contain image files (jpg, png, jpeg).
All images are treated as belonging to the same product and are aggregated
into a single visual measurement result.
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import List

# Ensure project root is on PYTHONPATH
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.pipeline import process_single_image
from app.aggregator import aggregate_results
from app.exporter import export_product_result
from app.prompts import SYSTEM_PROMPT, TASK_PROMPT
from app.vision_client import mock_vision_client


SUPPORTED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}


def collect_images(folder: Path) -> List[dict]:
    """
    Convert a folder of images into pipeline-compatible image references.
    """
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


def main() -> None:
    if len(sys.argv) != 2:
        print("Usage: python scripts/run_from_folder.py <folder_path>")
        sys.exit(1)

    folder = Path(sys.argv[1])
    if not folder.exists() or not folder.is_dir():
        print(f"Invalid folder path: {folder}")
        sys.exit(1)

    print("============================================================")
    print(">>> FOLDER-BASED VISUAL ANALYSIS DEMO <<<")
    print("============================================================")
    print(f"📂 Input folder: {folder}")

    # Initialize client (mock by default; can be swapped with real AI)
    client = mock_vision_client()

    image_refs = collect_images(folder)
    print(f"📸 Found {len(image_refs)} image(s)")

    prompts = {"system": SYSTEM_PROMPT, "task": TASK_PROMPT}

    per_image_results = []

    for img in image_refs:
        print(f"🤖 Processing image: {img['id']}")
        result = process_single_image(
            image=img,
            prompts=prompts,
            client=client,
        )
        per_image_results.append(result)

    print("📈 Aggregating per-image results...")
    aggregated = aggregate_results(per_image_results)

    output = export_product_result(
        aggregated,
        product_id=folder.name,
        output_dir="outputs",
        as_csv=True,
    )

    print("============================================================")
    print("✅ Analysis complete")
    print("------------------------------------------------------------")
    print(f"JSON output: {output['json']}")
    print(f"CSV output : {output['csv']}")
    print("============================================================")


if __name__ == "__main__":
    main()

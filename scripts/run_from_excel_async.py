"""Run the A1.0 pipeline on a company-provided Excel input (async).

Usage:
    python scripts/run_from_excel_async.py [--concurrency N]

Notes:
- Expects `data/A1.0_data_product_images.xlsx` (read-only).
- One column with product IDs and one with image URLs is required.
- The script uses the mock vision client by default.
- For each product, images are processed concurrently via `process_images_async`.
"""
from __future__ import annotations

from pathlib import Path
import sys
import argparse
# make project root importable when running this script directly
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

# Friendly import of pandas
try:
    import pandas as pd
except Exception as e:
    print("Error: pandas is required to run this script. Install with 'pip install pandas' and try again.")
    raise SystemExit(1)

import json
import asyncio

from app.input_handler import load_images
from app.async_pipeline import process_images_async
from app.vision_client import mock_vision_client
from app.aggregator import aggregate_results
from app.prompts import SYSTEM_PROMPT, TASK_PROMPT

EXCEL_PATH = Path("data/A1.0_data_product_images.xlsx")

PRODUCT_COL = "product_id"
IMAGE_COL = "image_url"

if not EXCEL_PATH.exists():
    print(f"Excel file not found: {EXCEL_PATH}. Place the company-provided Excel file at this path and try again.")
    raise SystemExit(1)


async def main_async(concurrency: int = 5) -> None:
    # 1. Load Excel (company-provided, read-only)
    try:
        df = pd.read_excel(EXCEL_PATH)
    except Exception as e:
        msg = str(e)
        if "openpyxl" in msg.lower():
            print("Failed to read Excel file: openpyxl is required by pandas to read .xlsx files. Install with 'pip install openpyxl' and try again.")
        else:
            print("Failed to read Excel file:", e)
        raise SystemExit(1)

    # Basic column detection (be flexible with common company formats)
    cols = list(df.columns)
    product_candidates = [c for c in cols if c.lower() in ("product_id", "product id", "productid")]
    if not product_candidates:
        product_candidates = [c for c in cols if "product" in c.lower()]
    if not product_candidates:
        print("Expected a product id column; found columns:", cols)
        raise SystemExit(1)
    product_col = product_candidates[0]

    image_cols = [c for c in cols if "image" in c.lower()]
    if not image_cols:
        print("Expected one or more image columns; found columns:", cols)
        raise SystemExit(1)

    print(f"Using product column: {product_col}; image columns: {image_cols}")

    client = mock_vision_client()
    prompts = {"system": SYSTEM_PROMPT, "task": TASK_PROMPT}

    final_results = {}
    errors = {}

    # 2. Group images per product
    for product_id, group in df.groupby(product_col):
        # collect all image-like columns into a single list of URLs for this product
        image_values = []
        for _, row in group.iterrows():
            for c in image_cols:
                val = row.get(c)
                if pd.notna(val) and str(val).strip():
                    image_values.append(str(val).strip())
        image_urls = image_values

        if not image_urls:
            continue

        try:
            images = load_images(image_urls)
        except Exception as e:
            errors[product_id] = {"stage": "load_images", "error": str(e)}
            continue

        # Queue and run images concurrently for this product
        try:
            per_image_outputs = await process_images_async(
                images=images,
                prompts=prompts,
                client=client,
                cache=None,
                concurrency=concurrency,
            )
        except Exception as e:
            errors[product_id] = {"stage": "async_processing", "error": str(e)}
            continue

        # 3. Aggregate per product
        try:
            aggregated = aggregate_results(per_image_outputs)
        except Exception as e:
            errors[product_id] = {"stage": "aggregate", "error": str(e)}
            continue

        final_results[product_id] = aggregated

    # 4. Print summary and save results
    print("Processed products:", len(final_results))
    if final_results:
        sample_keys = list(final_results.keys())[:3]
        print("Sample product ids:", sample_keys)

    out_path = Path("outputs")
    out_path.mkdir(parents=True, exist_ok=True)
    json_path = out_path / "excel_run_results_async.json"
    with json_path.open("w", encoding="utf-8") as fh:
        json.dump(final_results, fh, indent=2, ensure_ascii=False)

    if errors:
        print("Some products failed during processing. See 'outputs/excel_run_errors_async.json' for details.")
        err_path = out_path / "excel_run_errors_async.json"
        with err_path.open("w", encoding="utf-8") as fh:
            json.dump(errors, fh, indent=2, ensure_ascii=False)
    else:
        print("No processing errors detected.")

    print("Wrote results to:", json_path)


def main(argv: list[str] | None = None) -> None:
    argv = argv if argv is not None else sys.argv[1:]
    parser = argparse.ArgumentParser()
    parser.add_argument("--concurrency", type=int, default=5, help="Max concurrent images per product")
    args = parser.parse_args(argv)

    try:
        asyncio.run(main_async(concurrency=args.concurrency))
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted by user")


if __name__ == "__main__":
    main()

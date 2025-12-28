"""Run the A1.0 pipeline on a company-provided Excel input.

Usage:
    python scripts/run_from_excel.py

Notes:
- Expects `data/A1.0_data_product_images.xlsx` (read-only).
- One column with product IDs and one with image URLs is required.
- The script uses the mock vision client by default.
"""
from pathlib import Path
import sys
# make project root importable when running this script directly
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

# Friendly import of pandas
try:
    import pandas as pd
except Exception as e:
    print("Error: pandas is required to run this script. Install with 'pip install pandas' and try again.")
    raise SystemExit(1)

from app.input_handler import load_images
from app.pipeline import process_single_image
from app.vision_client import mock_vision_client
from app.aggregator import aggregate_results
from app.prompts import SYSTEM_PROMPT, TASK_PROMPT
import json

DEFAULT_EXCEL_PATH = Path("data/A1.0_data_product_images.xlsx")

PRODUCT_COL = "product_id"
IMAGE_COL = "image_url"


def run_from_excel(excel_path: Path) -> None:
    """Run the existing Excel pipeline logic given a resolved excel_path."""
    if not excel_path.exists():
        print(f"Excel file not found: {excel_path}. Place the company-provided Excel file at this path and try again.")
        raise SystemExit(1)

    # 1. Load Excel (company-provided, read-only)
    try:
        df = pd.read_excel(excel_path)
    except Exception as e:
        msg = str(e)
        if "openpyxl" in msg.lower():
            print("Failed to read Excel file: openpyxl is required by pandas to read .xlsx files. Install with 'pip install openpyxl' and try again.")
        else:
            print("Failed to read Excel file:", e)
        raise SystemExit(1)

    # Basic column detection (be flexible with common company formats)
    cols = list(df.columns)
    # detect product id column: prefer exact matches then fall back to any column containing 'product'
    product_candidates = [c for c in cols if c.lower() in ("product_id", "product id", "productid")]
    if not product_candidates:
        product_candidates = [c for c in cols if "product" in c.lower()]
    if not product_candidates:
        print("Expected a product id column; found columns:", cols)
        raise SystemExit(1)
    product_col = product_candidates[0]

    # detect image columns: any column containing 'image' (supports Image1, Image2, image_url, etc.)
    image_cols = [c for c in cols if "image" in c.lower()]
    if not image_cols:
        print("Expected one or more image columns; found columns:", cols)
        raise SystemExit(1)

    print(f"Using product column: {product_col}; image columns: {image_cols}")

    # Initialize client and observability helpers
    client = mock_vision_client()

    # Make the local scripts/tools package importable and load helpers
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from tools.run_metrics import analysis_timer, print_model_used

    prompts = {"system": SYSTEM_PROMPT, "task": TASK_PROMPT}

    # Precompute the set of products that have at least one image to be processed
    tasks: list[tuple[str, list[str]]] = []
    for product_id, group in df.groupby(product_col):
        image_values = []
        for _, row in group.iterrows():
            for c in image_cols:
                val = row.get(c)
                if pd.notna(val) and str(val).strip():
                    image_values.append(str(val).strip())
        if image_values:
            tasks.append((product_id, image_values))

    # Top-level observability lines (in required order)
    print("Processed products:", len(tasks))
    print_model_used(client)

    final_results = {}
    errors = {}

    # 2. Run analysis (timed)
    with analysis_timer():
        for product_id, image_urls in tasks:
            try:
                images = load_images(image_urls)
            except Exception as e:
                errors[product_id] = {"stage": "load_images", "error": str(e)}
                continue

            per_image_outputs = []
            for img in images:
                try:
                    result = process_single_image(image=img, prompts=prompts, client=client)
                    per_image_outputs.append(result)
                except Exception as e:
                    per_image_outputs.append({"error": str(e)})

            # 3. Aggregate per product
            try:
                aggregated = aggregate_results(per_image_outputs)
            except Exception as e:
                errors[product_id] = {"stage": "aggregate", "error": str(e)}
                continue

            final_results[product_id] = aggregated

    # 4. Print summary and save results
    if final_results:
        sample_keys = list(final_results.keys())[:3]
        print("Sample product ids:", sample_keys)

    out_path = Path("outputs/sync")
    out_path.mkdir(parents=True, exist_ok=True)
    json_path = out_path / "excel_run_results.json"
    with json_path.open("w", encoding="utf-8") as fh:
        json.dump(final_results, fh, indent=2, ensure_ascii=False)

    if errors:
        print("Some products failed during processing. See 'outputs/sync/excel_run_errors.json' for details.")
        err_path = out_path / "excel_run_errors.json"
        with err_path.open("w", encoding="utf-8") as fh:
            json.dump(errors, fh, indent=2, ensure_ascii=False)
    else:
        print("No processing errors detected.")

    print("Wrote results to:", json_path)


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument('--excel-file', type=str, default=str(DEFAULT_EXCEL_PATH), help='Path to Excel file to process (default: data/A1.0_data_product_images.xlsx)')
    args = parser.parse_args()

    run_from_excel(Path(args.excel_file))

"""Mock demo runner for A1.0 Visual Measurement System.

This script:
- Uses a deterministic mock vision client
- Requires no API keys
- Demonstrates the full pipeline end-to-end
"""
from pathlib import Path
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.vision_client import mock_vision_client
from app.pipeline import process_single_image
from app.aggregator import aggregate_results
from app.exporter import export_product_result


def run_demo():
    client = mock_vision_client()

    # use a simple image reference dict (id string used as image_id in pipeline)
    image_ref = {
        "id": "demo-img-1",
        "source": "https://example.com/sample_glasses.jpg",
        "type": "url",
    }

    # process single image
    single = process_single_image(image_ref, prompts="demo prompt", client=client)
    print("Per-image output:", single)

    # aggregate (single-item aggregation is fine for demo)
    agg = aggregate_results([single])
    print("Aggregated result:", agg)

    # write demo output files under outputs/sync/demo_output.*
    res = export_product_result(agg, product_id="demo_output", output_dir="outputs/sync", as_csv=True)
    print("Wrote:", res)


if __name__ == '__main__':
    run_demo()
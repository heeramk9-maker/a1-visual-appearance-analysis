"""
Optional real OpenAI demo runner for A1.0 Visual Appearance Analysis.

⚠️ Requires OPENAI_API_KEY
⚠️ NOT required for evaluation
"""

from __future__ import annotations

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Ensure project root is on PYTHONPATH
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

load_dotenv()

from app.pipeline import process_single_image
from app.aggregator import aggregate_results
from app.exporter import export_product_result
from app.prompts import SYSTEM_PROMPT, TASK_PROMPT
from app.openai_vision_client import OpenAIVisionClient


def run_demo_real_openai():
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("OPENAI_API_KEY not set. Exiting.")
        return

    client = OpenAIVisionClient(api_key)

    image_ref = {
        "id": "real-openai-img-1",
        "source": "https://images.unsplash.com/photo-1544005313-94ddf0286df2?w=1200&q=80",
        "type": "url",
    }

    prompts = {
        "system": SYSTEM_PROMPT,
        "task": TASK_PROMPT,
    }

    single = process_single_image(image_ref, prompts=prompts, client=client)
    print("Per-image output:", single)

    agg = aggregate_results([single])
    print("Aggregated result:", agg)

    res = export_product_result(
        agg,
        product_id="real_openai_demo_output",
        output_dir="outputs",
        as_csv=True,
    )
    print("Wrote:", res)


if __name__ == "__main__":
    run_demo_real_openai()

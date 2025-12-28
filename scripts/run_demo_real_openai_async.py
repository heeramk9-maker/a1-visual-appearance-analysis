"""Async demo for OpenAI Vision (single-image) using process_images_async."""
from __future__ import annotations

import os
import sys
from pathlib import Path
import argparse
import asyncio
from dotenv import load_dotenv

# Ensure project root is on PYTHONPATH
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

load_dotenv()

from app.async_pipeline import process_images_async
from app.aggregator import aggregate_results
from app.exporter import export_product_result
from app.prompts import SYSTEM_PROMPT, TASK_PROMPT
from app.openai_vision_client import OpenAIVisionClient
import json


async def main_async(concurrency: int = 5) -> None:
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

    print("Per-image output will be printed below")

    per_image_results = await process_images_async(
        images=[image_ref],
        prompts=prompts,
        client=client,
        cache=None,
        concurrency=concurrency,
    )

    single = per_image_results[0]
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


def main(argv: list[str] | None = None) -> None:
    argv = argv if argv is not None else sys.argv[1:]
    parser = argparse.ArgumentParser()
    parser.add_argument("--concurrency", type=int, default=5, help="Max concurrent images")
    args = parser.parse_args(argv)

    try:
        asyncio.run(main_async(concurrency=args.concurrency))
    except KeyboardInterrupt:
        print("\n\n⚠️  Demo interrupted by user.\n")


if __name__ == "__main__":
    main()

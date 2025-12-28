"""Async demo for Gemini Vision (single-image) using process_images_async."""
from __future__ import annotations

import os
import sys
import json
from pathlib import Path
import argparse
import asyncio

# Load .env if present
try:
    from dotenv import load_dotenv
    load_dotenv()
except Exception:
    pass

# Add project root to PYTHONPATH
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.async_pipeline import process_images_async
from app.aggregator import aggregate_results
from app.exporter import export_product_result
from app.prompts import SYSTEM_PROMPT
from app.gemini_vision_client import GeminiVisionClient

A1_TASK_PROMPT = """
Analyze the product image and return ONLY visual appearance reasoning.

Return JSON with:
- visual_measurements: mapping of dimension -> {score, justification, uncertain}
  Dimensions:
    - gender_expression
    - visual_weight
    - embellishment
    - unconventionality
    - formality
- attributes: observable visual attributes only
- confidence_notes (optional)

Rules:
- Scores must be between -5.0 and +5.0
- Do not infer intent, brand, or business context
- If unsure, mark uncertain=true
"""


async def main_async(concurrency: int = 5) -> None:
    print("\n" + "="*60)
    print(">>> GEMINI VISION ASYNC DEMO STARTED <<<")
    print("="*60 + "\n")

    # Check API key
    api_key = os.getenv("GEMINI_API_KEY")
    print(f"🔑 GEMINI_API_KEY detected: {bool(api_key)}")

    if not api_key:
        print("\n❌ ERROR: GEMINI_API_KEY not set.")
        print("   Set it in your .env file or environment:")
        print("   export GEMINI_API_KEY='your-key-here'\n")
        return

    # Initialize client
    try:
        print("🔧 Initializing Gemini client...")
        client = GeminiVisionClient(api_key=api_key)
        print(f"   Using model: {client.model}\n")
    except Exception as e:
        msg = str(e)
        # Graceful fallback for local dev when google-genai isn't installed
        if "google-genai package is not installed" in msg:
            print("\n⚠️  google-genai not installed — falling back to local mock vision client for demo.\n")
            from app.vision_client import mock_vision_client

            client = mock_vision_client()
            print("   Using mock vision client (deterministic local behavior)\n")
        else:
            print(f"\n❌ Failed to initialize client: {e}\n")
            return

    # Define test image
    image_ref = {
        "id": "real-gemini-img-1",
        "source": "https://images.unsplash.com/photo-1544005313-94ddf0286df2?w=1200&q=80",
        "type": "url",
    }

    prompts = {
        "system": SYSTEM_PROMPT,
        "task": A1_TASK_PROMPT,
    }

    print(f"📸 Processing image: {image_ref['id']}")
    print(f"   Source: {image_ref['source'][:60]}...\n")

    # Optional demo cache (in-memory only)
    from app.cache import ResultCache
    demo_cache = ResultCache(verbose=True)

    # Run inference (wrap single image as list and call async wrapper)
    try:
        print("🤖 Running inference...")
        per_image_results = await process_images_async(
            images=[image_ref],
            prompts=prompts,
            client=client,
            cache=demo_cache,
            concurrency=concurrency,
        )

        single = per_image_results[0]
        print("Cache stats after inference:", demo_cache.stats())

        # Check for errors
        if single.get("errors"):
            print("\n⚠️  Errors encountered during processing:")
            for err in single["errors"]:
                print(f"   Stage: {err.get('stage', 'unknown')}")
                print(f"   Error: {err.get('error', 'unknown')}\n")
        else:
            print("✅ Inference completed successfully\n")

        print("-" * 60)
        print("📊 Per-image output:")
        print("-" * 60)
        print(json.dumps(single, indent=2, default=str))
        print()

    except Exception as e:
        print(f"\n❌ Inference failed: {e}\n")
        import traceback
        traceback.print_exc()
        return

    # Aggregate results
    try:
        print("\n📈 Aggregating results...")
        agg = aggregate_results([single])

        print("-" * 60)
        print("📋 Aggregated result:")
        print("-" * 60)
        print(json.dumps(agg, indent=2, default=str))
        print()

    except Exception as e:
        print(f"\n⚠️  Aggregation failed: {e}\n")
        agg = {"error": str(e), "raw": [single]}

    # Export results
    try:
        print("\n💾 Exporting results...")
        result_files = export_product_result(
            agg,
            product_id="real_gemini_demo_output",
            output_dir="outputs/async",
            as_csv=True,
        )

        print("-" * 60)
        print("✅ Export complete:")
        print("-" * 60)
        for fmt, path in result_files.items():
            print(f"   {fmt.upper()}: {path}")
        print()

    except Exception as e:
        print(f"\n⚠️  Export failed: {e}\n")

    print("="*60)
    print(">>> DEMO COMPLETED <<<")
    print("="*60 + "\n")


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

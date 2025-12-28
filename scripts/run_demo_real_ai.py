"""Real AI demo runner for A1.0 Visual Measurement System.

This script demonstrates how the same pipeline can be executed
using a real vision-capable AI model instead of the mock client.

⚠️ This script is OPTIONAL.
⚠️ It requires an API key and is NOT required for evaluation.
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

# Ensure project root is on PYTHONPATH
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.pipeline import process_single_image
from app.aggregator import aggregate_results
from app.exporter import export_product_result
from app.prompts import SYSTEM_PROMPT


# A1.0 task prompt: visual measurements, attributes, and uncertainty handling
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


# -------------------------------
# Real Vision Client (OpenAI-style)
# -------------------------------
class RealVisionClient:
    """
    Minimal real vision client wrapper.

    Exposes the same interface as mock_vision_client:
        infer(image, prompts) -> dict
    """

    def __init__(self, openai_client):
        self.client = openai_client

    def infer(self, image, prompts):
        """
        image: dict with {id, source, type}
        prompts: dict with keys 'system' and 'task'
        """
        # Validate inputs early to provide clear error messages for callers
        if not isinstance(prompts, dict) or "system" not in prompts or "task" not in prompts:
            raise TypeError("prompts must be a dict containing 'system' and 'task' keys")
        if not isinstance(image, dict) or "source" not in image:
            raise TypeError("image must be a dict containing a 'source' key")

        # This implementation targets the OpenAI "responses" API shape but
        # tolerates slight variations in the response object to remain robust.
        response = self.client.responses.create(
            model=os.getenv("OPENAI_VISION_MODEL", "gpt-4o-mini"),
            input=[
                {"role": "system", "content": prompts["system"]},
                {
                    "role": "user",
                    "content": [
                        {"type": "input_text", "text": prompts["task"]},
                        {"type": "input_image", "image_url": image["source"]},
                    ],
                },
            ],
        )

        # Prefer the SDK-provided output_text
        raw_text = None
        if hasattr(response, "output_text"):
            raw_text = response.output_text
        elif isinstance(response, dict) and "output_text" in response:
            raw_text = response["output_text"]
        else:
            # Try the more explicit output array shape
            out = getattr(response, "output", None) or (response.get("output") if isinstance(response, dict) else None)
            if out and isinstance(out, list) and len(out) > 0:
                first = out[0]
                # content may be nested
                content = first.get("content") if isinstance(first, dict) else None
                if isinstance(content, list) and len(content) > 0 and isinstance(content[0], dict):
                    raw_text = content[0].get("text")

        if raw_text is None:
            # Fallback to stringification
            raw_text = str(response)

        try:
            parsed = json.loads(raw_text)
        except json.JSONDecodeError as e:
            raise ValueError("Unable to parse model response as JSON") from e

        if not isinstance(parsed, dict):
            raise TypeError("Parsed model response is not a JSON object/dict")

        return parsed


def run_demo_real_ai():
    print("Running optional real-AI demo (requires OPENAI_API_KEY)")

    # -------------------------------
    # 1. Check API key
    # -------------------------------
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("OPENAI_API_KEY not set. This script is optional and intended for local testing only.")
        print("Set OPENAI_API_KEY and install the 'openai' package to run this demo.")
        return

    # Import here to avoid dependency for mock runs
    try:
        from openai import OpenAI
    except Exception:  # pragma: no cover - depends on local environment
        print("Unable to import 'openai'. Install it with: pip install openai")
        return

    openai_client = OpenAI(api_key=api_key)
    client = RealVisionClient(openai_client)

    # -------------------------------
    # 2. Image input (URL or local)
    # -------------------------------
    # For local images, upload first or serve via local HTTP server.
    image_ref = {
        "id": "real-ai-img-1",
        "source": "https://images.unsplash.com/photo-1544005313-94ddf0286df2?w=1200&q=80",
        "type": "url",
    }

    prompts = {"system": SYSTEM_PROMPT, "task": A1_TASK_PROMPT}

    # -------------------------------
    # 3. Run pipeline
    # -------------------------------
    single = process_single_image(image_ref, prompts=prompts, client=client)
    print("Per-image output:", single)

    # -------------------------------
    # 4. Aggregate & export
    # -------------------------------
    agg = aggregate_results([single])
    print("Aggregated result:", agg)

    res = export_product_result(
        agg, product_id="real_ai_demo_output", output_dir="outputs/sync", as_csv=True
    )
    print("Wrote:", res)


if __name__ == "__main__":
    run_demo_real_ai()

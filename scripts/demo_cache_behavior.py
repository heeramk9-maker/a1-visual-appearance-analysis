"""Demo showing ResultCache behavior with the pipeline.

Run:
    python scripts/demo_cache_behavior.py

It will:
- create a ResultCache with verbose prints
- run the pipeline twice for the same image_id using a counting client
- demonstrate that the 2nd run is served from cache (no client call)
"""
from importlib import import_module
import sys
from pathlib import Path
# Ensure project root is on PYTHONPATH so `app` imports work when running this script directly
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.cache import ResultCache
from app.pipeline import process_single_image


def demo():
    cache = ResultCache(verbose=True)

    calls = {"n": 0}

    def counting_client(image, prompts):
        calls["n"] += 1
        return {
            "visual_measurements": {
                "gender_expression": {"score": 0.5, "justification": "x", "uncertain": False},
                "visual_weight": {"score": -1.0, "justification": "x", "uncertain": False},
                "embellishment": {"score": -2.0, "justification": "x", "uncertain": False},
                "unconventionality": {"score": -1.0, "justification": "x", "uncertain": False},
                "formality": {"score": 0.0, "justification": "x", "uncertain": False},
            },
            "attributes": {},
        }

    image = {"id": "demo-img-1", "source": "sample", "type": "local"}
    prompts = "p"

    print("--- First run (should MISS and call client) ---")
    out1 = process_single_image(image, prompts=prompts, client=counting_client, cache=cache)
    print("Client calls:", calls["n"], "Cache stats:", cache.stats())

    print("--- Second run (should HIT and NOT call client) ---")
    out2 = process_single_image(image, prompts=prompts, client=counting_client, cache=cache)
    print("Client calls:", calls["n"], "Cache stats:", cache.stats())

    assert out1 == out2
    print("Demo passed: second run served from cache")


if __name__ == "__main__":
    demo()
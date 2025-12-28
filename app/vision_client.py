"""vision_client.py
Single controlled entry point for calling a vision-capable LLM
to perform visual appearance analysis (A1.0).

This module returns structured visual reasoning output and
does NOT perform physical measurement or real-world size estimation.
"""
from __future__ import annotations

from typing import Any, Callable
import json


class VisionClient:
    """Minimal wrapper around a provided inference callable.

    The provided `infer_func` should accept (image, prompts) and return
    either a dict or a JSON string.
    """

    def __init__(self, infer_func: Callable[[Any, Any], Any]):
        if not callable(infer_func):
            raise TypeError("infer_func must be callable")
        self._infer = infer_func

    def infer(self, image: Any, prompts: Any) -> Any:
        return self._infer(image, prompts)


def analyze_image(image: Any, prompts: Any, client: Any = None) -> dict:
    """Analyze a single image using a vision-capable client and return raw JSON.

    Args:
        image: A single image reference (e.g. path, URL, bytes, or a dict
               returned from `load_images`). Must NOT be a list of images.
        prompts: Prompt(s) to send to the vision model (str or dict).
        client: Either a callable(image, prompts) returning dict|str, or an
                object exposing `infer(image, prompts)`.

    Returns:
        A Python dict parsed from the client's response.

    Raises:
        TypeError for invalid argument types.
        NotImplementedError if no `client` is provided.
        ValueError if client returns invalid JSON string.
    """
    # Enforce single image: no lists allowed here
    if isinstance(image, (list, tuple)):
        raise TypeError("analyze_image expects a single image, not a list/tuple")

    if not isinstance(prompts, (str, dict)):
        raise TypeError("prompts must be a str or dict")

    if client is None:
        raise NotImplementedError("No client provided. Pass a callable or an object with `infer` method.")

    # Resolve the callable to invoke
    if callable(client):
        res = client(image, prompts)
    elif hasattr(client, "infer") and callable(getattr(client, "infer")):
        res = client.infer(image, prompts)
    else:
        raise TypeError("client must be a callable or an object with an `infer(image, prompts)` method")

    # Accept dicts directly; parse JSON strings
    if isinstance(res, dict):
        return res
    if isinstance(res, str):
        try:
            parsed = json.loads(res)
        except json.JSONDecodeError as e:
            raise ValueError("client returned string that is not valid JSON") from e
        if not isinstance(parsed, dict):
            raise TypeError("parsed JSON is not a JSON object/dict")
        return parsed

    raise TypeError("client must return a dict or a JSON-serializable string")


# Lightweight mock client for testing and local development. This is NOT a
# real inference client; it returns a deterministic, minimal JSON structure
# that conforms to the A1.0 visual appearance schema.
def mock_vision_client(return_json_string: bool = False) -> Callable[[Any, Any], Any]:
    """Return a mock A1.0-compliant payload (visual appearance reasoning).

    The payload matches A1.0: no physical dimensions, only subjective
    `visual_measurements` with scores in [-5.0, 5.0], plus an `attributes`
    mapping and a `confidence_notes` string.
    """
    def _mock(image, prompts):
        payload = {
            "visual_measurements": {
                "gender_expression": {
                    "score": 0.5,
                    "justification": "Balanced, neutral frame styling",
                    "uncertain": False,
                },
                "visual_weight": {
                    "score": -1.0,
                    "justification": "Thin frame with minimal material",
                    "uncertain": False,
                },
                "embellishment": {
                    "score": -2.0,
                    "justification": "No decorative elements visible",
                    "uncertain": False,
                },
                "unconventionality": {
                    "score": -1.5,
                    "justification": "Classic rectangular design",
                    "uncertain": False,
                },
                "formality": {
                    "score": 0.0,
                    "justification": "Neither clearly formal nor casual",
                    "uncertain": False,
                },
            },
            "attributes": {
                "frame_geometry": "rectangular",
                "transparency": "opaque",
                "dominant_colors": ["black"],
                "visible_texture": "none",
                "visible_wirecore": "uncertain",
                "suitable_for_kids": "uncertain",
            },
            "confidence_notes": "Clear frontal image with good lighting",
        }
        return json.dumps(payload) if return_json_string else payload

    return _mock


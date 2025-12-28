"""
Gemini vision client for A1.0 visual appearance analysis.
"""
from __future__ import annotations

import json
import os
from typing import Optional

try:
    from google import genai
except Exception:  # pragma: no cover - optional dependency
    genai = None


class GeminiVisionClient:
    """Minimal Gemini client wrapper compatible with the project's vision
    client interface using `google.genai`.

    - Validates inputs early
    - Supports selecting model via `GEMINI_VISION_MODEL` env var
    - Uses `client.models.generate_content` to call Gemini
    """

    def __init__(self, api_key: str, model: Optional[str] = None):
        if genai is None:
            raise RuntimeError("google.genai package is not installed")
        self.client = genai.Client(api_key=api_key)
        # Prefer a vision-capable model by default
        self.model_name = model or os.getenv("GEMINI_VISION_MODEL", "gemini-1.5-flash")

    def infer(self, image: dict, prompts: dict) -> dict:
        """
        image: dict with {id, source, type}
        prompts: dict with keys 'system' and 'task'
        """
        # Validate inputs
        if not isinstance(prompts, dict) or "system" not in prompts or "task" not in prompts:
            raise TypeError("prompts must be a dict containing 'system' and 'task' keys")
        if not isinstance(image, dict) or "source" not in image:
            raise TypeError("image must be a dict containing a 'source' key")

        prompt_text = (
            f"{prompts['system']}\n\n{prompts['task']}\n\n"
            "Rules:\n- Output ONLY valid JSON\n- Do not include markdown\n- Do not include explanations outside JSON"
        )

        # Call the model using the Client API
        try:
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=[prompt_text, image["source"]],
            )
        except Exception as e:
            raise RuntimeError(f"Failed to call Gemini model: {e}") from e

        # Extract text from common response shapes robustly
        raw_text = None
        if hasattr(response, "text"):
            raw_text = response.text
        elif isinstance(response, dict) and "text" in response:
            raw_text = response["text"]
        else:
            # Try candidates/content shapes
            candidates = getattr(response, "candidates", None) or (response.get("candidates") if isinstance(response, dict) else None)
            if candidates and isinstance(candidates, list) and len(candidates) > 0:
                first = candidates[0]
                if isinstance(first, dict):
                    raw_text = first.get("content") or first.get("text")
                else:
                    raw_text = str(first)

        if raw_text is None:
            raw_text = str(response)

        try:
            parsed = json.loads(raw_text)
        except json.JSONDecodeError as e:
            raise ValueError("Gemini response is not valid JSON") from e

        if not isinstance(parsed, dict):
            raise TypeError("Parsed Gemini response is not a JSON object/dict")

        return parsed
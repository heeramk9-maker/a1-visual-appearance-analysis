from __future__ import annotations

import json
import requests
from typing import Optional
from io import BytesIO
from PIL import Image

# Import `google.genai` lazily and defensively so the module can be
# imported even when the SDK isn't installed. The demo scripts will
# surface a helpful error if the package is missing.
try:
    from google import genai
except Exception:  # pragma: no cover - optional dependency
    genai = None
try:
    from google.genai import types
except Exception:  # pragma: no cover - optional dependency
    types = None


class GeminiVisionClient:
    """
    Gemini vision client using the current google.genai SDK.

    Conforms to interface:
        infer(image: dict, prompts: dict) -> dict
    """

    def __init__(self, api_key: str, model: Optional[str] = None):
        if not api_key:
            raise ValueError("GEMINI_API_KEY is required")

        # Ensure the SDK is present and surface a clear error otherwise
        if genai is None:
            raise RuntimeError("google-genai package is not installed. Install with: pip install google-genai")

        # Initialize Gemini client
        self.client = genai.Client(api_key=api_key)

        # Use Gemini 2.5 Flash (best balance of speed and capability)
        self.model = model or "models/gemini-2.5-flash"

    def _download_image(self, url: str) -> bytes:
        """Download image from URL and return as bytes."""
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        
        # Verify it's actually an image
        try:
            img = Image.open(BytesIO(response.content))
            img.verify()
        except Exception as e:
            raise ValueError(f"Downloaded content is not a valid image: {e}")
        
        return response.content

    def infer(self, image: dict, prompts: dict) -> dict:
        """
        image: {id, source, type}
        prompts: {system, task}
        """

        if image.get("type") != "url":
            raise ValueError("Only URL-based images are supported")

        prompt_text = f"""
{prompts['system']}

{prompts['task']}

STRICT OUTPUT RULES:
- Return ONLY valid JSON
- No markdown
- No explanations
- Scores must be between -5.0 and +5.0
"""

        try:
            # Download the image (used for validation); we'll send a URL
            # to the model when the 'types' helpers are not available.
            _ = self._download_image(image["source"])

            if types is not None:
                # Create Part from bytes with inline_data if SDK bindings present
                image_part = types.Part(
                    inline_data=types.Blob(
                        mime_type="image/jpeg",
                        data=_
                    )
                )
                contents = [prompt_text, image_part]
            else:
                # Fallback: just send the image URL as an explicit input_image
                contents = [prompt_text, {"type": "input_image", "image_url": image["source"]}]

            response = self.client.models.generate_content(
                model=self.model,
                contents=contents,
            )
        except Exception as e:
            raise RuntimeError(f"Gemini API call failed: {e}") from e

        # Gemini returns plain text
        text = response.text.strip()

        # Strict JSON parsing with recovery
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            start = text.find("{")
            end = text.rfind("}") + 1

            if start == -1 or end == 0:
                raise ValueError(f"Gemini response is not valid JSON: {text}")

            return json.loads(text[start:end])
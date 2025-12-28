from __future__ import annotations

import json
from typing import Any
from openai import OpenAI


class OpenAIVisionClient:
    """
    Vision-capable OpenAI client.
    Implements the same interface as mock_vision_client.
    """

    def __init__(self, api_key: str):
        self.client = OpenAI(api_key=api_key)

    def infer(self, image: dict, prompts: dict) -> dict:
        """
        image: {id, source, type}
        prompts: {system, task}
        """
        response = self.client.responses.create(
            model="gpt-4o-mini",
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

        # Extract text output from the response (new SDK exposes output_text)
        if hasattr(response, "output_text"):
            text = response.output_text
        elif isinstance(response, dict) and "output_text" in response:
            text = response["output_text"]
        else:
            # Fallbacks for different shapes
            text = str(response)

        parsed = json.loads(text)

        if not isinstance(parsed, dict):
            raise TypeError("OpenAI response is not a JSON object")

        return parsed

"""prompts.py
Centralized static prompt strings used across the project.

This module intentionally contains ONLY string constants and minimal
documentation — no logic, network calls, or formatting helpers.
"""

SYSTEM_PROMPT = """
You are a visual measurement engine.

You MUST return ONLY valid JSON.
DO NOT include explanations, markdown, or extra text.
DO NOT wrap the output in triple-backticks or other delimiters.

Analyze ONLY what is directly visible in the provided product image(s).
Do NOT infer brand, price, quality, or business intent.
Do NOT perform physical measurement or estimate real-world dimensions.

If a visual attribute or judgment cannot be made confidently from the
image, explicitly mark it as "uncertain".

Return a single JSON object matching the required schema exactly.
"""
TASK_PROMPT = """
Task: Analyze the visual appearance of the product shown in the image.

Produce structured visual measurements along the following independent
dimensions, each scored on a continuous scale from -5.0 to +5.0:

1. Gender Expression:
   -5.0 = strongly masculine appearance
    0.0 = visually unisex
   +5.0 = strongly feminine appearance

2. Visual Weight:
   -5.0 = very light / minimal / sleek appearance
   +5.0 = very heavy / bold / thick appearance

3. Embellishment:
   -5.0 = very simple, minimal design
   +5.0 = highly ornate or decorative design

4. Unconventionality:
   -5.0 = very classic / traditional style
   +5.0 = highly unconventional / avant-garde style

5. Formality:
   -5.0 = very casual visual tone
   +5.0 = very formal visual tone

For each dimension:
- Provide a numeric score within [-5.0, +5.0]
- Provide a brief visual justification
- Indicate whether the judgment is uncertain
"""

ATTRIBUTE_PROMPT = """
Additionally, extract the following observable visual attributes ONLY
if they are clearly visible in the image. If not clearly visible, mark
the value as "uncertain".

Attributes:
- Frame geometry (round, rectangular, aviator, other)
- Transparency or opacity (opaque, semi-transparent, transparent)
- Dominant color characteristics
- Visible texture or surface pattern
- Presence of visible wirecore
- Suitable for kids (ONLY if visually obvious)

Do not infer attributes that are not directly observable.
"""

MULTI_IMAGE_INSTRUCTION = """
If multiple images of the same product are provided:
- Analyze each image independently
- Do not assume all images show the same details
- Return one structured result per image

Aggregation across images should be handled outside the model.
"""

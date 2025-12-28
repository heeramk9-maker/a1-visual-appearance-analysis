"""pipeline.py
Single-image pipeline that wires together vision_client, schema, measurements,
and attributes modules to produce a clean per-image JSON output.
"""
from __future__ import annotations

from typing import Any, Dict
from pydantic import ValidationError

from app.vision_client import analyze_image
from app.schema import validate_image_analysis
from app.measurements import parse_measurements
from app.attributes import parse_attributes

# Required A1.0 visual measurement dimensions
REQUIRED_DIMENSIONS = {
    "gender_expression",
    "visual_weight",
    "embellishment",
    "unconventionality",
    "formality",
}


def process_single_image(image: Any, prompts: Any, client: Any, cache: Any = None) -> Dict[str, Any]:
    """Run the single-image pipeline and return a cleaned per-image result.

    Steps:
      1. Call the vision client to get raw JSON
      2. Validate A1.0 visual reasoning outputs against schema
      3. Parse any score-like outputs with `parse_measurements`
      4. Normalize categorical attributes with `parse_attributes`

    The function never aggregates across images and never mutates external
    state; it returns a JSON-serializable dict that contains both parsed
    outputs and an embedded `raw` copy for auditing.
    """
    out: Dict[str, Any] = {"image": image, "errors": []}

    # Resolve deterministic image id for caching
    image_id = image["id"] if isinstance(image, dict) and "id" in image else str(image)

    # 🔹 Cache lookup (optional)
    # We perform the cache lookup *before* calling the vision client. This
    # placement ensures we skip the costly model invocation entirely when a
    # validated, final result already exists for this `image_id`.
    #
    # Trade-offs: caching at this level caches the fully validated output
    # (post-schema validation) which avoids returning partially parsed or
    # invalid payloads. It also means that if downstream parsing logic
    # changes, data may be stale until the cache is cleared.
    if cache is not None:
        cached = cache.get(image_id)
        if cached is not None:
            return cached

    try:
        raw = analyze_image(image, prompts, client=client)
    except Exception as e:
        out["errors"].append({"stage": "analysis", "error": str(e)})
        out["raw"] = None
        return out

    out["raw"] = raw

    # Reject any attempts to supply physical measurement fields (A1.0 forbids this)
    forbidden = {"width_mm", "height_mm", "area_mm2", "unit"}
    if isinstance(raw, dict) and any(k in raw for k in forbidden):
        out["errors"].append({"stage": "forbidden_physical_measurement", "error": "physical measurement fields are not allowed under A1.0"})
        return out

    # Parse score-like outputs (A1.0 visual_measurements) if present
    try:
        if isinstance(raw, dict) and "visual_measurements" in raw:
            target = raw["visual_measurements"]
            parsed_scores = parse_measurements(target)
            out["visual_measurements"] = parsed_scores
        elif isinstance(raw, dict):
            # A1.0 requires a top-level 'visual_measurements' mapping
            out["errors"].append({
                "stage": "visual_measurements",
                "error": "Expected 'visual_measurements' field in A1.0 output",
            })
            return out
    except Exception as e:
        out["errors"].append({"stage": "parse_measurements", "error": str(e)})

    # Parse attributes if present
    try:
        attributes = None
        if isinstance(raw, dict) and "attributes" in raw:
            attributes = parse_attributes(raw["attributes"])
            out["attributes"] = attributes
    except Exception as e:
        out["errors"].append({"stage": "parse_attributes", "error": str(e)})

    # Pass through confidence notes if present
    confidence_notes = None
    if isinstance(raw, dict) and "confidence_notes" in raw:
        confidence_notes = raw.get("confidence_notes")

    # Assemble final per-image object and validate against ImageAnalysis schema
    final_candidate = {
        "image_id": image["id"] if isinstance(image, dict) and "id" in image else str(image),
        "visual_measurements": None,
        "attributes": attributes or {},
        "confidence_notes": confidence_notes,
    }

    # Build a clean visual_measurements mapping (name -> {score, justification, uncertain})
    vm_clean = None
    if "visual_measurements" in out:
        vm_parsed = out["visual_measurements"]
        # vm_parsed may be one of:
        # - {'visual_measurements': {name: item, ...}, 'raw': ...}  (preferred A1.0 shape)
        # - {'results': {name: item, ...}, 'raw': ...}            (back-compat)
        # - or a direct mapping {name: item, ...}
        res = None
        if isinstance(vm_parsed, dict):
            if "visual_measurements" in vm_parsed and isinstance(vm_parsed["visual_measurements"], dict):
                res = vm_parsed["visual_measurements"]
            elif "results" in vm_parsed and isinstance(vm_parsed["results"], dict):
                res = vm_parsed["results"]
            else:
                # maybe a direct mapping already
                if all(isinstance(v, dict) for v in vm_parsed.values()):
                    res = vm_parsed
        if isinstance(res, dict):
            vm_clean = {name: {k: v for k, v in (val.items() if isinstance(val, dict) else []) if k in ("score", "justification", "uncertain")} for name, val in res.items()}
        elif isinstance(res, list):
            vm_clean = {f"score_{i+1}": {k: v for k, v in (val.items() if isinstance(val, dict) else []) if k in ("score", "justification", "uncertain")} for i, val in enumerate(res)}

    # Enforce that all REQUIRED_DIMENSIONS are present in the parsed mapping
    if not vm_clean or not REQUIRED_DIMENSIONS.issubset(set(vm_clean.keys())):
        out["errors"].append({
            "stage": "visual_measurements",
            "error": "Missing required A1.0 visual measurement dimensions",
        })
        return out

    final_candidate["visual_measurements"] = vm_clean

    try:
        validated = validate_image_analysis(final_candidate)
        result = validated.model_dump()
        # 🔹 Cache store (optional)
        # We store the *validated* final result to ensure any cached
        # object satisfies schema constraints. This preserves the
        # pipeline's invariant that returned objects are A1.0-compliant.
        # Cache writes are intentionally performed only after successful
        # final validation to avoid caching partial or invalid outputs.
        if cache is not None:
            cache.set(image_id, result)
        return result
    except ValidationError as e:
        out["errors"].append({"stage": "final_validation", "error": e.errors()})
        return out

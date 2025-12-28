"""measurements.py
Functions to parse and normalize visual score outputs (A1.0).

This module isolates subjectivity handling: it clamps numeric visual
scores to [-5.0, 5.0], preserves justification and uncertainty fields,
and returns predictable structured outputs even when inputs are malformed.
"""
from __future__ import annotations

from typing import Any, Dict, List, Optional
import re


_CLAMP_MIN = -5.0
_CLAMP_MAX = 5.0


def _to_float(value: Any) -> Optional[float]:
    """Try to convert `value` to float. Return None if not possible."""
    if value is None:
        return None
    if isinstance(value, (int, float)):
        return float(value)
    if isinstance(value, str):
        s = value.strip()
        if s == "":
            return None
        try:
            # direct float parse
            return float(s)
        except ValueError:
            # try to extract first numeric substring (e.g., "score: -3.2")
            m = re.search(r"[-+]?[0-9]*\.?[0-9]+", s)
            if m:
                try:
                    return float(m.group(0))
                except ValueError:
                    return None
            return None
    return None


def _to_bool(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, (int, float)):
        return bool(value)
    if isinstance(value, str):
        s = value.strip().lower()
        if s in ("true", "1", "yes", "y"):
            return True
        if s in ("false", "0", "no", "n"):
            return False
    return False


def _clamp(v: float) -> float:
    return max(_CLAMP_MIN, min(_CLAMP_MAX, v))


def _process_item(item: Dict[str, Any]) -> Dict[str, Any]:
    """Process a single score-like item and return normalized dict."""
    errors: List[str] = []

    raw_score = item.get("score") if isinstance(item, dict) else None
    score_val = _to_float(raw_score)

    if score_val is None:
        errors.append("missing_or_invalid_score")
        clamped = None
    else:
        clamped = _clamp(score_val)
        if clamped != score_val:
            errors.append(f"clamped:{score_val}->{clamped}")

    justification = item.get("justification") if isinstance(item, dict) else None
    if justification is not None and not isinstance(justification, str):
        justification = str(justification)

    uncertain = _to_bool(item.get("uncertain") if isinstance(item, dict) else None)

    return {
        "score": clamped,
        "justification": justification,
        "uncertain": uncertain,
        "errors": errors,
        "raw": item,
    }


def parse_measurements(raw_response: Any) -> Dict[str, Any]:
    """Parse measurement-like responses and return normalized structure.

    Handles A1.0 `visual_measurements` dicts (mapping name -> {score, justification, uncertain}).

    Output for named measurements is:
        {"results": {name: normalized_item, ...}, "raw": raw_response}

    For backward compatibility, lists and single-item dicts are still supported.
    """
    # A1.0-style mapping of named visual measurements
    if isinstance(raw_response, dict) and any(isinstance(v, dict) and "score" in v for v in raw_response.values()):
        results = {}
        for name, val in raw_response.items():
            results[name] = _process_item(val if isinstance(val, dict) else {"score": val})
        # NOTE:
        # 'errors' and 'raw' returned by `_process_item` are internal diagnostics
        # and MUST be stripped before schema validation or inclusion in final
        # outputs. This function returns a stable A1.0-shaped mapping under
        # the `visual_measurements` key for downstream consumers.
        return {"visual_measurements": results, "raw": raw_response}

    # If a dict containing a list of scores, normalize that form
    if isinstance(raw_response, dict):
        if "scores" in raw_response and isinstance(raw_response["scores"], list):
            results = [_process_item(it if isinstance(it, dict) else {"score": it}) for it in raw_response["scores"]]
            return {"results": results, "raw": raw_response}
        if "results" in raw_response and isinstance(raw_response["results"], list):
            results = [_process_item(it if isinstance(it, dict) else {"score": it}) for it in raw_response["results"]]
            return {"results": results, "raw": raw_response}

        # treat as single item dict
        return {"result": _process_item(raw_response), "raw": raw_response}

    # If it's a list of values, treat as multiple scores
    if isinstance(raw_response, list):
        results = [_process_item(it if isinstance(it, dict) else {"score": it}) for it in raw_response]
        return {"results": results, "raw": raw_response}

    # Unexpected types: wrap as a single item with no score
    return {"result": _process_item({"score": None, "justification": None, "uncertain": False}), "raw": raw_response}


def _legacy_not_used():
    raise NotImplementedError("Legacy placeholder; not used in A1.0")


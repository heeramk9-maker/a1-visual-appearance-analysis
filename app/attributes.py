"""attributes.py
Categorical attribute normalization and parsing.

The parser enforces a whitelist of allowed values, normalizes common
synonyms, and converts unknown or missing values to the sentinel
string "uncertain". It never invents attributes that were not present
in the input (meta rule: never infer missing info).
"""
from __future__ import annotations

from typing import Any, Dict, List
import re


# Allowed canonical values
_ALLOWED_COLORS = {
    "red",
    "green",
    "blue",
    "yellow",
    "black",
    "white",
    "gray",
    "brown",
    "orange",
    "pink",
    "purple",
    "cyan",
}

_ALLOWED_SHAPES = {
    "rectangle",
    "square",
    "circle",
    "ellipse",
    "oval",
    "triangle",
    "polygon",
}

_ALLOWED_ORIENTATIONS = {"portrait", "landscape"}

_ALLOWED_MATERIALS = {"metal", "plastic", "wood", "glass", "fabric", "paper", "ceramic"}

_UNKNOWN = "uncertain"


def _extract_text(value: Any) -> str:
    """Extract a reasonable textual representation from `value` for
    normalization. Return empty string when nothing sensible can be extracted."""
    if value is None:
        return ""
    if isinstance(value, str):
        return value.strip()
    if isinstance(value, dict):
        # common fields that may carry a label
        for k in ("label", "value", "name", "text"):
            if k in value and isinstance(value[k], str):
                return value[k].strip()
        return ""
    if isinstance(value, (list, tuple)) and value:
        return _extract_text(value[0])
    try:
        return str(value).strip()
    except Exception:
        return ""


def _normalize_color(s: Any) -> str:
    txt = _extract_text(s).lower()
    if not txt:
        return _UNKNOWN

    # normalize common British spelling
    txt = txt.replace("grey", "gray")

    # remove punctuation
    txt = re.sub(r"[^a-z0-9\s]", " ", txt)

    # attempt to find an allowed color token inside the string
    for token in re.split(r"\s+", txt):
        if token in _ALLOWED_COLORS:
            return token

    # as a fallback, try to match words like 'lightblue' -> 'blue'
    for color in _ALLOWED_COLORS:
        if color in txt:
            return color

    return _UNKNOWN


def _normalize_shape(s: Any) -> str:
    txt = _extract_text(s).lower()
    if not txt:
        return _UNKNOWN

    txt = re.sub(r"[^a-z0-9\s]", " ", txt)

    # synonym map
    syn = {
        "rect": "rectangle",
        "box": "rectangle",
        "square": "square",
        "sq": "square",
        "round": "circle",
        "circular": "circle",
        "ellipse": "ellipse",
        "oval": "oval",
        "tri": "triangle",
        "triangle": "triangle",
    }

    for token in re.split(r"\s+", txt):
        if token in syn:
            return syn[token]
        if token in _ALLOWED_SHAPES:
            return token

    # fallback: look for any allowed shape as substring
    for shape in _ALLOWED_SHAPES:
        if shape in txt:
            return shape

    return _UNKNOWN


def _normalize_orientation(s: Any) -> str:
    txt = _extract_text(s).lower()
    if not txt:
        return _UNKNOWN
    if "portrait" in txt:
        return "portrait"
    if "landscape" in txt:
        return "landscape"
    return _UNKNOWN


def _normalize_colors(value: Any) -> List[str]:
    """Normalize an input that may be a single color, CSV-like string, or list
    into a list of canonical color strings. If no colors are recognizable and
    the input was present, return ["uncertain"]. If input is absent/empty,
    return an empty list."""
    # Treat explicit presence of `None` as an explicitly provided but
    # uninformative value (i.e. present but unknown) and signal uncertainty.
    if value is None:
        return [_UNKNOWN]
    items: List[str] = []
    if isinstance(value, (list, tuple)):
        items = [str(v) for v in value]
    else:
        txt = _extract_text(value)
        if not txt:
            return []
        # split on commas, slashes, 'and', or whitespace
        items = re.split(r"[,&/]|\band\b", txt)
    out_colors: List[str] = []
    for it in items:
        c = _normalize_color(it)
        if c != _UNKNOWN and c not in out_colors:
            out_colors.append(c)
    if not out_colors:
        # if input was present but nothing matched, signal uncertainty
        txt = _extract_text(value)
        if txt:
            return [_UNKNOWN]
        return []
    return out_colors


def _normalize_frame_geometry(s: Any) -> str:
    # reuse shape normalization semantics but return under A1.0 name
    return _normalize_shape(s)


def _normalize_transparency(s: Any) -> str:
    txt = _extract_text(s).lower()
    if not txt:
        return _UNKNOWN
    if "transparent" in txt and ("part" not in txt and "%" not in txt and "semi" not in txt):
        return "transparent"
    if "translucent" in txt or "semi-transparent" in txt or "semi transparent" in txt or "%" in txt or "part" in txt:
        return "translucent"
    if "opaque" in txt:
        return "opaque"
    return _UNKNOWN


def _normalize_visible_texture(s: Any) -> str:
    txt = _extract_text(s)
    if not txt:
        return _UNKNOWN
    return txt


def _normalize_yes_no_uncertain(value: Any) -> str:
    if value is None:
        return _UNKNOWN
    if isinstance(value, bool):
        return "yes" if value else "no"
    if isinstance(value, (int, float)):
        return "yes" if bool(value) else "no"
    txt = _extract_text(value).lower()
    if txt in ("yes", "y", "true", "1"):
        return "yes"
    if txt in ("no", "n", "false", "0"):
        return "no"
    return _UNKNOWN


def parse_attributes(raw: Dict[str, Any]) -> Dict[str, Any]:
    """Parse A1.0 visual-only attributes and return a mapping.

    Returned keys (A1.0):
      - dominant_colors: list[str] (if input present)
      - frame_geometry: str ('rectangle', 'circle', etc.) (if input present)
      - transparency: str ('transparent'|'translucent'|'opaque'|'uncertain')
      - visible_texture: str or 'uncertain'
      - visible_wirecore: 'yes'|'no'|'uncertain'
      - suitable_for_kids: 'yes'|'no'|'uncertain'
    """
    if not isinstance(raw, dict):
        raise TypeError("raw must be a dict")

    out: Dict[str, Any] = {}

    # dominant_colors can be supplied under 'dominant_colors' or legacy 'color'
    if "dominant_colors" in raw or "color" in raw:
        colors = raw.get("dominant_colors", raw.get("color"))
        out["dominant_colors"] = _normalize_colors(colors)

    # frame geometry (legacy 'shape')
    if "frame_geometry" in raw or "shape" in raw:
        out["frame_geometry"] = _normalize_frame_geometry(raw.get("frame_geometry", raw.get("shape")))

    # transparency and visible_texture: include explicit uncertainty when missing
    out["transparency"] = _normalize_transparency(raw.get("transparency"))
    out["visible_texture"] = _normalize_visible_texture(raw.get("visible_texture"))

    # yes/no/uncertain constrained attributes — default to 'uncertain' if missing
    out["visible_wirecore"] = _normalize_yes_no_uncertain(raw.get("visible_wirecore"))
    out["suitable_for_kids"] = _normalize_yes_no_uncertain(raw.get("suitable_for_kids"))

    return out


__all__ = ["parse_attributes", "_UNKNOWN"]

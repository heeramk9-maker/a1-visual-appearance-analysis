import pytest
from app.attributes import parse_attributes, _UNKNOWN


def test_dominant_colors_simple():
    out = parse_attributes({"color": "Light Blue"})
    assert "dominant_colors" in out
    assert out["dominant_colors"] == ["blue"]


def test_dominant_colors_unknown_becomes_uncertain():
    out = parse_attributes({"color": "chartreuse"})
    assert out["dominant_colors"] == [_UNKNOWN]


def test_frame_geometry_synonym_and_case():
    out = parse_attributes({"shape": "Rect"})
    assert out["frame_geometry"] == "rectangle"


def test_transparency_and_texture_and_yes_no_defaults():
    out = parse_attributes({})
    # missing dominant colors should not be invented
    assert "dominant_colors" not in out
    # defaults for other visual-only fields are explicit 'uncertain'
    assert out["transparency"] == _UNKNOWN
    assert out["visible_texture"] == _UNKNOWN
    assert out["visible_wirecore"] == _UNKNOWN
    assert out["suitable_for_kids"] == _UNKNOWN


def test_none_value_becomes_uncertain():
    out = parse_attributes({"color": None, "shape": None})
    assert out["dominant_colors"] == [_UNKNOWN]
    assert out["frame_geometry"] == _UNKNOWN


def test_unexpected_keys_ignored_and_color():
    out = parse_attributes({"foo": "bar", "color": "red"})
    assert "foo" not in out
    assert out["dominant_colors"] == ["red"]


def test_yes_no_fields_and_texture():
    out = parse_attributes({"visible_wirecore": "Yes", "suitable_for_kids": "no", "visible_texture": "Woven"})
    assert out["visible_wirecore"] == "yes"
    assert out["suitable_for_kids"] == "no"
    assert out["visible_texture"].lower().startswith("woven")

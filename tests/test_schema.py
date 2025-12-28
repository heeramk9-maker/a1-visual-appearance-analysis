import pytest
from pydantic import ValidationError

from app.schema import validate_visual_score, validate_visual_measurements, validate_image_analysis


def test_visual_score_validation():
    valid = {"score": 0.7, "justification": "clear object", "uncertain": False}
    vs = validate_visual_score(valid)
    assert vs.score == 0.7

    with pytest.raises(ValidationError):
        validate_visual_score({"score": 6.0, "justification": "x", "uncertain": False})


def test_visual_measurements_mapping():
    vm = {
        "gender_expression": {"score": 0.5, "justification": "neutral", "uncertain": False},
        "visual_weight": {"score": -1.0, "justification": "light", "uncertain": False},
        "embellishment": {"score": -2.0, "justification": "plain", "uncertain": False},
        "unconventionality": {"score": -1.5, "justification": "classic", "uncertain": False},
        "formality": {"score": 0.0, "justification": "balanced", "uncertain": False},
    }
    vms = validate_visual_measurements(vm)
    assert vms.gender_expression.score == 0.5


def test_image_analysis_validation():
    vm = {
        "gender_expression": {"score": 0.5, "justification": "neutral", "uncertain": False},
        "visual_weight": {"score": -1.0, "justification": "light", "uncertain": False},
        "embellishment": {"score": -2.0, "justification": "plain", "uncertain": False},
        "unconventionality": {"score": -1.5, "justification": "classic", "uncertain": False},
        "formality": {"score": 0.0, "justification": "balanced", "uncertain": False},
    }
    data = {"image_id": "img1", "visual_measurements": vm, "attributes": {"color": "red"}, "confidence_notes": "ok"}
    out = validate_image_analysis(data)
    assert out.image_id == "img1"

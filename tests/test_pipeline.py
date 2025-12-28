from app.pipeline import process_single_image
from app.vision_client import mock_vision_client


def test_pipeline_with_valid_measurement():
    # client returns full A1.0-style visual measurements from the provided mock
    out = process_single_image("img.jpg", "prompt", client=mock_vision_client())
    # validated model_dump should include final contract fields
    assert out["image_id"] == "img.jpg"
    assert out["visual_measurements"]["gender_expression"]["score"] == 0.5
    # attributes are A1.0-aligned and coming from the mock
    assert out["attributes"]["dominant_colors"] == ["black"]


def test_pipeline_with_invalid_measurement():
    def bad_measure(i, p):
        return {"width_mm": -1.0, "height_mm": 5.0, "unit": "mm"}

    out = process_single_image("img.jpg", "prompt", client=bad_measure)
    assert out["errors"]
    assert any(e.get("stage") == "forbidden_physical_measurement" for e in out["errors"])

def test_pipeline_with_scores_and_attributes():
    def score_client(i, p):
        return {"scores": [{"score": 7, "justification": "a"}, {"score": "-6", "uncertain": "1"}], "attributes": {"color": "Light Blue", "shape": "rect"}}

    out = process_single_image("img.jpg", "prompt", client=score_client)
    # A1.0 requires a top-level 'visual_measurements' mapping; older list forms should be rejected
    assert out["errors"]
    assert any(e.get("stage") == "visual_measurements" for e in out["errors"])

def test_pipeline_handles_client_errors():
    def raise_client(i, p):
        raise RuntimeError("boom")

    out = process_single_image("img.jpg", "prompt", client=raise_client)
    assert out["errors"]
    assert out["raw"] is None

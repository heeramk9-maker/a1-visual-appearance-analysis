from app.measurements import parse_measurements


def test_single_valid_score():
    raw = {"score": 3.2, "justification": "ok", "uncertain": False}
    out = parse_measurements(raw)
    assert "result" in out
    r = out["result"]
    assert r["score"] == 3.2
    assert r["justification"] == "ok"
    assert r["uncertain"] is False
    assert r["errors"] == []


def test_clamp_high_and_low():
    raw_high = {"score": 10}
    raw_low = {"score": -10}
    oh = parse_measurements(raw_high)["result"]
    ol = parse_measurements(raw_low)["result"]
    assert oh["score"] == 5.0
    assert any(word.startswith("clamped") for word in oh["errors"])
    assert ol["score"] == -5.0


def test_string_score_parsing():
    raw = {"score": "4.5", "uncertain": "true"}
    r = parse_measurements(raw)["result"]
    assert r["score"] == 4.5
    assert r["uncertain"] is True


def test_unparsable_score():
    raw = {"score": "not a number"}
    r = parse_measurements(raw)["result"]
    assert r["score"] is None
    assert "missing_or_invalid_score" in r["errors"]


def test_scores_list():
    raw = {"scores": [{"score": 7, "justification": "a"}, {"score": "-6", "uncertain": "1"}]}
    out = parse_measurements(raw)
    assert "results" in out
    results = out["results"]
    assert results[0]["score"] == 5.0
    assert results[1]["score"] == -5.0
    assert results[1]["uncertain"] is True


def test_unexpected_input_type():
    out = parse_measurements(12345)
    r = out["result"]
    assert r["score"] is None
    assert r["uncertain"] is False


def test_named_visual_measurements_mapping():
    raw = {
        "gender_expression": {"score": 0.5, "justification": "neutral", "uncertain": False},
        "visual_weight": {"score": -2.0, "justification": "light", "uncertain": False},
    }
    parsed = parse_measurements(raw)
    assert "visual_measurements" in parsed
    assert parsed["visual_measurements"]["gender_expression"]["score"] == 0.5
    assert parsed["visual_measurements"]["visual_weight"]["score"] == -2.0

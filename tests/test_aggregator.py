import pytest
from app.aggregator import aggregate_results


def make_img(scores=None, attrs=None):
    out = {}
    if scores is not None:
        out["visual_measurements"] = scores
    if attrs is not None:
        out["attributes"] = attrs
    return out


def test_aggregate_dimension_consensus():
    imgs = [make_img({"gender_expression": {"score": 1}}), make_img({"gender_expression": {"score": 2}}), make_img({"gender_expression": {"score": 3}})]
    agg = aggregate_results(imgs)
    assert agg["visual_consensus"]["gender_expression"]["mean"] == 2.0
    assert agg["visual_consensus"]["gender_expression"]["range"] == [1, 3]
    assert agg["visual_consensus"]["gender_expression"]["confidence"] == pytest.approx(3/3)


def test_missing_dimension_counts_into_confidence():
    imgs = [make_img({"gender_expression": {"score": 1}}), make_img({}), make_img({"gender_expression": {"score": 3}})]
    agg = aggregate_results(imgs)
    # only two images provided gender_expression
    assert agg["visual_consensus"]["gender_expression"]["confidence"] == pytest.approx(2/3)


def test_attribute_majority_and_confidence():
    imgs = [make_img({"gender_expression": {"score": 1}}, {"color": "blue"}), make_img({"gender_expression": {"score": 2}}, {"color": "blue"}), make_img({"gender_expression": {"score": 3}}, {"color": "red"})]
    agg = aggregate_results(imgs)
    assert agg["attribute_summary"]["color"]["value"] == "blue"
    assert agg["attribute_summary"]["color"]["confidence"] == pytest.approx(2/3)


def test_attribute_disagreement_reported():
    imgs = [make_img({"gender_expression": {"score": 1}}, {"color": "blue"}), make_img({"gender_expression": {"score": 2}}, {"color": "red"}), make_img({"gender_expression": {"score": 3}}, {"color": "green"})]
    agg = aggregate_results(imgs)
    assert "color" in agg["attribute_disagreements"]


def test_score_disagreements_detected():
    imgs = [make_img({"gender_expression": {"score": 1}}), make_img({"gender_expression": {"score": 1}}), make_img({"gender_expression": {"score": 10}})]
    agg = aggregate_results(imgs)
    assert agg["visual_consensus"]["gender_expression"]["disagreement"] is True

import json
import tempfile
from app.exporter import export_product_result


def test_export_json_and_metadata_and_confidence():
    agg = {"score_summary": {"count": 2, "missing": 1, "mean": 2.0, "median": 2.0}, "attribute_disagreements": {"color": {}}}
    with tempfile.TemporaryDirectory() as td:
        res = export_product_result(agg, product_id="test123", metadata={"batch": 1}, output_dir=td, as_csv=False)
        assert "json" in res
        p = res["json"]
        with open(p, "r", encoding="utf-8") as fh:
            obj = json.load(fh)
        assert obj["product_id"] == "test123"
        assert "confidence" in obj
        assert "confidence_notes" in obj


def test_export_csv_option():
    agg = {"score_summary": {"count": 3, "missing": 0, "mean": 3.0, "median": 3.0}}
    with tempfile.TemporaryDirectory() as td:
        res = export_product_result(agg, product_id="prod2", output_dir=td, as_csv=True)
        assert "csv" in res
        # ensure files exist
        with open(res["json"], "r", encoding="utf-8") as fh:
            _ = json.load(fh)
        with open(res["csv"], "r", encoding="utf-8") as fh:
            data = fh.read()
        assert "prod2" in data


def test_export_csv_includes_visual_consensus():
    # Construct a simple visual_consensus with two dimensions
    agg = {
        "visual_consensus": {
            "gender_expression": {"mean": 0.5, "confidence": 0.9, "disagreement": False},
            "formality": {"mean": -0.2, "confidence": 0.75, "disagreement": True},
        }
    }
    with tempfile.TemporaryDirectory() as td:
        res = export_product_result(agg, product_id="prod_consensus", output_dir=td, as_csv=True)
        assert "csv" in res
        with open(res["csv"], "r", encoding="utf-8") as fh:
            data = fh.read()
        # header should include per-dimension mean column
        assert "gender_expression_mean" in data
        # the mean value should be present in the CSV
        assert "0.5" in data

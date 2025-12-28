import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.exporter import export_product_result


def run():
    try:
        agg = {"score_summary": {"count": 2, "missing": 1, "mean": 2.0, "median": 2.0}, "attribute_disagreements": {"color": {}}}
        res = export_product_result(agg, product_id="test123", metadata={"batch": 1}, output_dir="outputs", as_csv=True)
        print("Wrote:", res)
        print("OK: exporter tests passed")
        return 0
    except Exception as e:
        print("ERROR:", e)
        return 1

if __name__ == '__main__':
    raise SystemExit(run())
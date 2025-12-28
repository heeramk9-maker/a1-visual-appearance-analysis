import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.pipeline import process_single_image


def run():
    try:
        def good_client(i, p):
            return {"visual_measurements": {"gender_expression": {"score": 0.5, "justification": "x", "uncertain": False}}, "attributes": {"color": "red"}}

        out = process_single_image("img.jpg", "prompt", client=good_client)
        if "visual_measurements" not in out:
            print("ERROR: expected visual_measurements")
            return 1
        if out["attributes"].get("dominant_colors") != ["red"]:
            print("ERROR: expected dominant_colors to contain 'red'")
            return 1

        def bad_measure(i, p):
            return {"width_mm": -1.0, "height_mm": 5.0, "unit": "mm"}

        out2 = process_single_image("img.jpg", "prompt", client=bad_measure)
        if not out2["errors"] or not any(e.get("stage") == "forbidden_physical_measurement" for e in out2["errors"]):
            print("ERROR: expected forbidden_physical_measurement error for invalid measurement")
            return 1

        def score_client(i, p):
            return {"scores": [{"score": 7}, {"score": "-6"}], "attributes": {"color": "Light Blue", "shape": "rect"}}

        out3 = process_single_image("img.jpg", "prompt", client=score_client)
        # A1.0 requires a top-level 'visual_measurements' mapping; older list forms should be rejected
        if not out3.get("errors") or not any(e.get("stage") == "visual_measurements" for e in out3.get("errors", [])):
            print("ERROR: expected rejection of list-style visual measurements")
            return 1

        def raise_client(i, p):
            raise RuntimeError("boom")

        err = process_single_image("img.jpg", "prompt", client=raise_client)
        if not err["errors"] or err["raw"] is not None:
            print("ERROR: expected errors and raw None for failing client")
            return 1

        print("OK: pipeline tests passed")
        return 0
    except Exception as e:
        print("ERROR:", e)
        return 2


if __name__ == '__main__':
    raise SystemExit(run())
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.schema import validate_visual_score, validate_visual_measurements, validate_image_analysis


def run():
    try:
        # visual score
        vs = validate_visual_score({"score": 0.2, "justification": "ok", "uncertain": True})
        print("OK: valid visual score parsed")

        try:
            validate_visual_score({"score": 6.0, "justification": "x", "uncertain": True})
            print("ERROR: invalid visual score did not raise")
            return 1
        except Exception:
            pass

        # visual measurements mapping
        vm = {
            "gender_expression": {"score": 0.5, "justification": "x", "uncertain": False},
            "visual_weight": {"score": -1.0, "justification": "y", "uncertain": False},
            "embellishment": {"score": -2.0, "justification": "z", "uncertain": False},
            "unconventionality": {"score": -1.5, "justification": "w", "uncertain": False},
            "formality": {"score": 0.0, "justification": "v", "uncertain": False},
        }
        vms = validate_visual_measurements(vm)
        print("OK: visual measurements parsed")

        # image analysis
        data = {"image_id": "img1", "visual_measurements": vm, "attributes": {"color": "red"}}
        out = validate_image_analysis(data)
        print("OK: image analysis validated")

        print("OK: all schema tests passed")
        return 0
    except Exception as e:
        print("ERROR:", e)
        return 2


if __name__ == '__main__':
    raise SystemExit(run())
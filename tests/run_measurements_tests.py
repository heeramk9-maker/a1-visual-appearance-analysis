import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.measurements import parse_measurements


def run():
    try:
        raw = {"score": 3.2, "justification": "ok", "uncertain": False}
        r = parse_measurements(raw)["result"]
        if r["score"] != 3.2:
            print("ERROR: expected 3.2")
            return 1

        r2 = parse_measurements({"score": 10})["result"]
        if r2["score"] != 5.0:
            print("ERROR: clamping failed")
            return 1

        out = parse_measurements({"scores": [{"score": 7}, {"score": "-6"}]})
        if out["results"][0]["score"] != 5.0 or out["results"][1]["score"] != -5.0:
            print("ERROR: list clamping failed")
            return 1

        print("OK: measurement parser tests passed")
        return 0
    except Exception as e:
        print("ERROR:", e)
        return 2


if __name__ == '__main__':
    raise SystemExit(run())
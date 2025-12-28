import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.attributes import parse_attributes


def run():
    try:
        out = parse_attributes({"color": "Light Blue", "shape": "rect"})
        if out.get("dominant_colors") != ["blue"] or out.get("frame_geometry") != "rectangle":
            print("ERROR: normalization failed")
            return 1

        out2 = parse_attributes({"color": "unknownish"})
        if out2.get("dominant_colors") != ["uncertain"]:
            print("ERROR: unknown color should be ['uncertain']")
            return 1

        out3 = parse_attributes({})
        if "dominant_colors" in out3:
            print("ERROR: missing dominant_colors should not be inferred")
            return 1
        # defaults for other visual-only fields are provided explicitly
        if out3.get("transparency") != "uncertain" or out3.get("visible_wirecore") != "uncertain":
            print("ERROR: default fields not set to 'uncertain'")
            return 1

        print("OK: attribute parser tests passed")
        return 0
    except Exception as e:
        print("ERROR:", e)
        return 2


if __name__ == '__main__':
    raise SystemExit(run())